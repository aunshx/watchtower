"""Stage 1: Acquire — fetch pain signal candidates from GitHub."""

import hashlib
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from github import Github, GithubException, RateLimitExceededException
from rich import box
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, GITHUB_TOKEN, PAIN_SEARCH_QUERIES, TARGET_REPOS

console = Console()

NOW = datetime.now(timezone.utc)
THIRTY_DAYS_AGO = NOW - timedelta(days=30)
SIXTY_DAYS_AGO = NOW - timedelta(days=60)
RECENT_DATE_STR = SIXTY_DAYS_AGO.strftime("%Y-%m-%d")
MIN_BODY_LEN = 50
MAX_PRS_PER_REPO = 30
MAX_SEARCH_RESULTS = 50


def _ensure_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _wait_for_reset(g: Optional[Github] = None, resource: str = "core") -> None:
    sleep_secs = 60
    if g:
        try:
            rl = g.get_rate_limit()
            bucket = getattr(rl, resource, rl.core)
            reset = _ensure_utc(bucket.reset)
            sleep_secs = max(10, (reset - datetime.now(timezone.utc)).total_seconds() + 5)
        except Exception:
            pass
    console.print(f"[yellow]Rate limit hit. Sleeping {sleep_secs:.0f}s until reset...[/yellow]")
    time.sleep(sleep_secs)


def gh(func, *args, g: Optional[Github] = None, resource: str = "core", **kwargs):
    """Call a GitHub API function, retrying transparently on rate limit errors."""
    while True:
        try:
            return func(*args, **kwargs)
        except RateLimitExceededException:
            _wait_for_reset(g, resource)
        except GithubException as e:
            if e.status in (403, 429):
                _wait_for_reset(g, resource)
            else:
                raise


def _repo_from_url(url: str) -> str:
    """Extract owner/repo from a GitHub URL without an extra API call."""
    parts = url.split("/")
    if len(parts) >= 5:
        return f"{parts[3]}/{parts[4]}"
    return "unknown/unknown"


def _make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:16]


def _is_maintainer(raw_data: dict) -> bool:
    return raw_data.get("author_association", "") in ("OWNER", "MEMBER", "COLLABORATOR")


def _make_candidate(
    source_type: str,
    repo: str,
    url: str,
    title: str,
    body: str,
    author: str,
    maintainer_signal: bool,
    created_at: datetime,
    pr_size: Optional[int] = None,
    context_snippet: str = "",
) -> Optional[dict]:
    body = (body or "").strip()
    if len(body) < MIN_BODY_LEN:
        return None
    if _ensure_utc(created_at) < SIXTY_DAYS_AGO:
        return None
    return {
        "id": _make_id(url),
        "source_type": source_type,
        "repo": repo,
        "url": url,
        "title": title,
        "body": body,
        "author": author,
        "maintainer_signal": maintainer_signal,
        "created_at": _ensure_utc(created_at).isoformat(),
        "pr_size": pr_size,
        "context_snippet": context_snippet,
    }


def fetch_pr_candidates(g: Github, repo_name: str) -> list:
    candidates = []
    try:
        repo = gh(g.get_repo, repo_name, g=g)
        pulls = gh(repo.get_pulls, state="all", sort="updated", direction="desc", g=g)
        pr_count = 0

        for pr in pulls:
            if pr_count >= MAX_PRS_PER_REPO:
                break
            if _ensure_utc(pr.updated_at) < THIRTY_DAYS_AGO:
                break
            pr_count += 1

            pr_size = None
            try:
                pr_size = pr.additions + pr.deletions
            except Exception:
                pass

            pr_context = (pr.body or "")[:500]

            # PR body itself
            c = _make_candidate(
                source_type="pr_comment",
                repo=repo_name,
                url=pr.html_url,
                title=pr.title,
                body=pr.body or "",
                author=pr.user.login if pr.user else "unknown",
                maintainer_signal=_is_maintainer(pr.raw_data),
                created_at=pr.created_at,
                pr_size=pr_size,
            )
            if c:
                candidates.append(c)

            # PR discussion comments
            try:
                for comment in gh(pr.get_issue_comments, g=g):
                    try:
                        c = _make_candidate(
                            source_type="pr_comment",
                            repo=repo_name,
                            url=comment.html_url,
                            title=pr.title,
                            body=comment.body or "",
                            author=comment.user.login if comment.user else "unknown",
                            maintainer_signal=_is_maintainer(comment.raw_data),
                            created_at=comment.created_at,
                            pr_size=pr_size,
                            context_snippet=pr_context,
                        )
                        if c:
                            candidates.append(c)
                    except RateLimitExceededException:
                        _wait_for_reset(g)
                    except GithubException:
                        pass
            except GithubException:
                pass

    except GithubException as e:
        console.print(f"  [red]Error fetching {repo_name}: {e}[/red]")

    return candidates


def fetch_search_candidates(g: Github, query_template: str) -> list:
    candidates = []
    query = query_template.format(recent_date=RECENT_DATE_STR)

    try:
        results = gh(g.search_issues, query, g=g, resource="search")
        count = 0
        for item in results:
            if count >= MAX_SEARCH_RESULTS:
                break
            try:
                count += 1
                repo_name = _repo_from_url(item.html_url)
                c = _make_candidate(
                    source_type="search_result",
                    repo=repo_name,
                    url=item.html_url,
                    title=item.title,
                    body=item.body or "",
                    author=item.user.login if item.user else "unknown",
                    maintainer_signal=_is_maintainer(item.raw_data),
                    created_at=item.created_at,
                )
                if c:
                    candidates.append(c)
                time.sleep(0.5)  # respect 30 req/min search rate limit
            except RateLimitExceededException:
                _wait_for_reset(g, "search")
            except GithubException:
                pass
    except GithubException as e:
        console.print(f"  [red]Search error: {e}[/red]")

    return candidates


def run() -> None:
    if not GITHUB_TOKEN:
        console.print("[bold red]GITHUB_TOKEN not set. Add it to .env and retry.[/bold red]")
        sys.exit(1)

    g = Github(GITHUB_TOKEN)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = DATA_DIR / "raw" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    all_candidates: list = []
    seen_urls: set = set()

    def _add_unique(raw: list) -> int:
        added = 0
        for c in raw:
            if c["url"] not in seen_urls:
                seen_urls.add(c["url"])
                all_candidates.append(c)
                added += 1
        return added

    # ── Repo scanning ──────────────────────────────────────────────────────────
    console.rule("[bold cyan]Stage 1: Acquire — scanning repos[/bold cyan]")
    repo_counts: dict = {}

    for repo_name in TARGET_REPOS:
        console.print(f"\n[bold]{repo_name}[/bold]")
        added = _add_unique(fetch_pr_candidates(g, repo_name))
        repo_counts[repo_name] = added
        console.print(f"  [green]→ {added} unique candidates[/green]")

    # ── Search queries ─────────────────────────────────────────────────────────
    console.rule("[bold cyan]Pain search queries[/bold cyan]")
    query_counts: dict = {}

    for query_template, _pain_hint in PAIN_SEARCH_QUERIES:
        label = query_template[:70]
        console.print(f"\n[dim]{label}[/dim]")
        added = _add_unique(fetch_search_candidates(g, query_template))
        query_counts[label] = added
        console.print(f"  [green]→ {added} unique candidates[/green]")
        time.sleep(2)  # buffer between queries

    # ── Save ───────────────────────────────────────────────────────────────────
    out_file = out_dir / "candidates.json"
    out_file.write_text(json.dumps(all_candidates, indent=2))

    # ── Summary tables ─────────────────────────────────────────────────────────
    console.rule("[bold green]Summary[/bold green]")

    repo_table = Table(
        title="Candidates by Repo",
        box=box.ROUNDED,
        show_footer=True,
    )
    repo_table.add_column("Repository", style="cyan", footer="TOTAL")
    repo_table.add_column(
        "Candidates",
        justify="right",
        style="green",
        footer=str(sum(repo_counts.values())),
    )
    for name, count in sorted(repo_counts.items(), key=lambda x: -x[1]):
        repo_table.add_row(name, str(count))

    query_table = Table(
        title="Candidates by Search Query",
        box=box.ROUNDED,
        show_footer=True,
    )
    query_table.add_column("Query (truncated)", style="yellow", footer="TOTAL")
    query_table.add_column(
        "Candidates",
        justify="right",
        style="green",
        footer=str(sum(query_counts.values())),
    )
    for label, count in query_counts.items():
        query_table.add_row(label, str(count))

    console.print(repo_table)
    console.print(query_table)
    console.print(f"\n[bold]Total unique candidates:[/bold] {len(all_candidates)}")
    console.print(f"[bold]Output:[/bold] {out_file}")


if __name__ == "__main__":
    run()
