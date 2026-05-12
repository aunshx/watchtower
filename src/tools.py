"""Tool definitions (Anthropic format) and execution for the agentic generator."""

import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import anthropic
from github import Github, GithubException, RateLimitExceededException

sys.path.insert(0, str(Path(__file__).parent))
from config import ANTHROPIC_API_KEY, DATA_DIR, GITHUB_TOKEN

# ── Cache ───────────────────────────────────────────────────────────────────

CACHE_DIR = DATA_DIR / "tool_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(tool_name: str, args: dict) -> str:
    raw = json.dumps({"tool": tool_name, "args": args}, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_get(key: str) -> Any | None:
    p = CACHE_DIR / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def _cache_set(key: str, value: Any) -> None:
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(value, indent=2))


# ── Anthropic tool schemas ───────────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "fetch_maintainer_recent_comments",
        "description": (
            "Fetch recent GitHub issues and PRs where this user has commented. "
            "Useful for learning the maintainer's voice, concerns, and writing style."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "GitHub username to look up",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 5, max 10)",
                    "default": 5,
                },
            },
            "required": ["username"],
        },
    },
    {
        "name": "fetch_full_thread",
        "description": (
            "Fetch the full conversation on a GitHub PR or issue URL. "
            "Returns all comments in chronological order. "
            "Use this to understand the full context of the pain moment."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full GitHub PR or issue URL",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "fetch_repo_context",
        "description": (
            "Fetch README excerpt, CONTRIBUTING.md, and any AI/agent policy file "
            "from a GitHub repo. Useful for understanding the project's tone and policies."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in 'owner/name' format",
                },
            },
            "required": ["repo"],
        },
    },
    {
        "name": "critique_self",
        "description": (
            "Submit your current draft for structured critique. "
            "A separate critic evaluates the draft and returns specific issues. "
            "Use this after your first draft before finalizing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "draft": {
                    "type": "string",
                    "description": "The current draft text to critique",
                },
                "plan_summary": {
                    "type": "string",
                    "description": "One sentence summarizing what this draft is trying to achieve",
                },
            },
            "required": ["draft", "plan_summary"],
        },
    },
    {
        "name": "submit_final_artifact",
        "description": (
            "Submit the final artifact. Call this when your draft is polished "
            "and you are satisfied with the output. This ends the generation loop."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "artifact": {
                    "type": "string",
                    "description": "The final markdown artifact text, ready to use",
                },
            },
            "required": ["artifact"],
        },
    },
]

# ── GitHub client (lazy) ─────────────────────────────────────────────────────

_gh: Github | None = None


def _github() -> Github:
    global _gh
    if _gh is None:
        _gh = Github(GITHUB_TOKEN)
    return _gh


def _gh_call(func, *args, **kwargs):
    """Retry once on rate limit."""
    try:
        return func(*args, **kwargs)
    except RateLimitExceededException:
        rl = _github().get_rate_limit()
        wait = max(10, (rl.core.reset.timestamp() - time.time()) + 2)
        time.sleep(min(wait, 60))
        return func(*args, **kwargs)
    except GithubException as e:
        if e.status in (403, 429):
            time.sleep(30)
            return func(*args, **kwargs)
        raise


def _parse_github_url(url: str) -> tuple[str, str, int]:
    """Return (owner/repo, 'issues'|'pulls', number) from a GitHub URL."""
    m = re.search(r"github\.com/([^/]+/[^/]+)/(issues|pull)/(\d+)", url)
    if not m:
        raise ValueError(f"Cannot parse GitHub URL: {url}")
    return m.group(1), m.group(2), int(m.group(3))


def _file_content(repo, path: str, max_chars: int = 1500) -> str | None:
    try:
        content = _gh_call(repo.get_contents, path)
        text = content.decoded_content.decode("utf-8", errors="replace")
        return text[:max_chars]
    except GithubException:
        return None


# ── Tool implementations ─────────────────────────────────────────────────────

def exec_fetch_maintainer_recent_comments(username: str, limit: int = 5) -> dict:
    limit = min(limit, 10)
    key = _cache_key("fetch_maintainer_recent_comments", {"username": username, "limit": limit})
    cached = _cache_get(key)
    if cached:
        return cached

    try:
        g = _github()
        results = _gh_call(g.search_issues, f"commenter:{username}", sort="updated", order="desc")
        items = []
        for item in results[:limit]:
            items.append({
                "repo": item.repository.full_name if item.repository else "unknown",
                "url": item.html_url,
                "title": item.title,
                "body": (item.body or "")[:500],
                "created_at": item.created_at.isoformat() if item.created_at else "",
            })
        result = {"username": username, "recent_activity": items}
    except Exception as e:
        result = {"username": username, "error": str(e), "recent_activity": []}

    _cache_set(key, result)
    return result


def exec_fetch_full_thread(url: str) -> dict:
    key = _cache_key("fetch_full_thread", {"url": url})
    cached = _cache_get(key)
    if cached:
        return cached

    try:
        repo_name, kind, number = _parse_github_url(url)
        g = _github()
        repo = _gh_call(g.get_repo, repo_name)

        # Get issue or PR description
        if "pull" in kind:
            item = _gh_call(repo.get_pull, number)
        else:
            item = _gh_call(repo.get_issue, number)

        # Collect maintainer logins for maintainer_signal
        try:
            collab_logins = {c.login for c in _gh_call(repo.get_collaborators)}
        except GithubException:
            collab_logins = set()

        comments = [
            {
                "author": item.user.login if item.user else "unknown",
                "body": (item.body or "")[:800],
                "created_at": item.created_at.isoformat() if item.created_at else "",
                "is_maintainer": (item.user.login in collab_logins) if item.user else False,
                "type": "description",
            }
        ]

        for comment in _gh_call(item.get_comments)[:30]:
            comments.append({
                "author": comment.user.login if comment.user else "unknown",
                "body": (comment.body or "")[:800],
                "created_at": comment.created_at.isoformat() if comment.created_at else "",
                "is_maintainer": (comment.user.login in collab_logins) if comment.user else False,
                "type": "comment",
            })

        result = {"url": url, "thread": comments}
    except Exception as e:
        result = {"url": url, "error": str(e), "thread": []}

    _cache_set(key, result)
    return result


def exec_fetch_repo_context(repo: str) -> dict:
    key = _cache_key("fetch_repo_context", {"repo": repo})
    cached = _cache_get(key)
    if cached:
        return cached

    try:
        g = _github()
        r = _gh_call(g.get_repo, repo)
        result = {
            "repo": repo,
            "readme_excerpt": _file_content(r, "README.md") or _file_content(r, "readme.md"),
            "contributing": _file_content(r, "CONTRIBUTING.md") or _file_content(r, "contributing.md"),
            "ai_policy": (
                _file_content(r, "CLAUDE.md")
                or _file_content(r, "AI_POLICY.md")
                or _file_content(r, ".github/CONTRIBUTING.md")
            ),
        }
    except Exception as e:
        result = {"repo": repo, "error": str(e)}

    _cache_set(key, result)
    return result


def exec_critique_self(draft: str, plan_summary: str) -> dict:
    # No cache — critiques should be fresh per draft
    critique_prompt = (Path(__file__).parent.parent / "prompts" / "critique_v2.md").read_text()
    user_msg = f"""Plan: {plan_summary}

Draft:
---
{draft}
---

Return ONLY valid JSON following the schema in the prompt."""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        resp = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=512,
            system=critique_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = resp.content[0].text.strip()
        # Extract the first complete JSON object regardless of surrounding text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise json.JSONDecodeError("No JSON object found", raw, 0)
        return json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        return {"issues": [f"Critique parse error: {e}"], "severity": "low", "should_refine": False}
    except Exception as e:
        return {"issues": [f"Critique error: {e}"], "severity": "low", "should_refine": False}


# ── Dispatcher ───────────────────────────────────────────────────────────────

def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name and return JSON string result."""
    try:
        if name == "fetch_maintainer_recent_comments":
            result = exec_fetch_maintainer_recent_comments(**args)
        elif name == "fetch_full_thread":
            result = exec_fetch_full_thread(**args)
        elif name == "fetch_repo_context":
            result = exec_fetch_repo_context(**args)
        elif name == "critique_self":
            result = exec_critique_self(**args)
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as e:
        result = {"error": f"Tool execution failed: {e}"}

    return json.dumps(result, indent=2, default=str)
