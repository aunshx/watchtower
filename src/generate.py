"""Stage 3: Generate — draft three artifacts per qualified pain moment."""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import anthropic
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent))
from config import ANTHROPIC_API_KEY, DATA_DIR, GENERATION_MODEL, OUTPUTS_DIR

console = Console()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

_COMMENT_TMPL = (PROMPTS_DIR / "generate_comment.md").read_text()
_OUTREACH_TMPL = (PROMPTS_DIR / "generate_outreach.md").read_text()
_CASE_STUDY_TMPL = (PROMPTS_DIR / "generate_case_study.md").read_text()

MAX_CONCURRENT = 9  # 3 artifacts × 5 moments, all in parallel


def _fill(template: str, **fields) -> str:
    """Safe field substitution that tolerates curly braces in field values."""
    result = template
    for key, value in fields.items():
        result = result.replace("{" + key + "}", str(value) if value is not None else "")
    return result


def _comment_prompt(c: dict) -> str:
    return _fill(
        _COMMENT_TMPL,
        repo=c["repo"],
        url=c["url"],
        pain_type=c.get("pain_type", ""),
        rationale=c.get("rationale", ""),
        entire_relevance=c.get("entire_relevance", ""),
        body=c["body"][:3000],
    )


def _outreach_prompt(c: dict) -> str:
    return _fill(
        _OUTREACH_TMPL,
        repo=c["repo"],
        author=c.get("author", "maintainer"),
        url=c["url"],
        pain_type=c.get("pain_type", ""),
        rationale=c.get("rationale", ""),
        entire_relevance=c.get("entire_relevance", ""),
        maintainer_audience_size=c.get("maintainer_audience_size", "medium"),
        body=c["body"][:3000],
    )


def _case_study_prompt(c: dict) -> str:
    return _fill(
        _CASE_STUDY_TMPL,
        pain_type=c.get("pain_type", ""),
        rationale=c.get("rationale", ""),
        entire_relevance=c.get("entire_relevance", ""),
        body=c["body"][:3000],
    )


async def _call(
    client: anthropic.AsyncAnthropic,
    sem: asyncio.Semaphore,
    prompt: str,
    label: str,
) -> str:
    async with sem:
        try:
            response = await client.messages.create(
                model=GENERATION_MODEL,
                max_tokens=1024,
                thinking={"type": "adaptive"},
                messages=[{"role": "user", "content": prompt}],
            )
            for block in response.content:
                if block.type == "text":
                    return block.text.strip()
            return ""
        except anthropic.APIError as e:
            console.print(f"  [red]API error ({label}): {e}[/red]")
            return f"[Generation failed: {e}]"


async def generate_moment(
    client: anthropic.AsyncAnthropic,
    sem: asyncio.Semaphore,
    candidate: dict,
    out_dir: Path,
    run_ts: str,
) -> dict:
    moment_id = candidate["id"]
    moment_dir = out_dir / f"pain_moment_{moment_id}"
    moment_dir.mkdir(parents=True, exist_ok=True)

    # Write source + classification
    (moment_dir / "source.json").write_text(
        json.dumps({k: v for k, v in candidate.items()
                    if k not in {"pain_score", "pain_type", "rationale",
                                 "entire_relevance", "maintainer_audience_size"}},
                   indent=2)
    )
    (moment_dir / "classification.json").write_text(
        json.dumps({k: candidate.get(k) for k in
                    ["pain_score", "pain_type", "rationale",
                     "entire_relevance", "maintainer_audience_size"]},
                   indent=2)
    )

    label = f"{candidate['repo']}#{moment_id[:8]}"
    console.print(f"  Generating artifacts for [cyan]{label}[/cyan]...")

    comment, outreach, case_study = await asyncio.gather(
        _call(client, sem, _comment_prompt(candidate), f"{label}/comment"),
        _call(client, sem, _outreach_prompt(candidate), f"{label}/outreach"),
        _call(client, sem, _case_study_prompt(candidate), f"{label}/case_study"),
    )

    (moment_dir / "public_comment.md").write_text(comment)
    (moment_dir / "outreach.md").write_text(outreach)
    (moment_dir / "case_study.md").write_text(case_study)

    (moment_dir / "meta.json").write_text(json.dumps({
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "run_timestamp": run_ts,
        "model": GENERATION_MODEL,
        "prompt_versions": {
            "comment": "generate_comment.md",
            "outreach": "generate_outreach.md",
            "case_study": "generate_case_study.md",
        },
    }, indent=2))

    return {
        "id": moment_id,
        "repo": candidate["repo"],
        "pain_score": candidate.get("pain_score"),
        "pain_type": candidate.get("pain_type"),
        "dir": str(moment_dir),
        "comment": comment,
        "outreach": outreach,
        "case_study": case_study,
    }


def load_latest_qualified() -> list:
    classified_dir = DATA_DIR / "classified"
    runs = sorted(classified_dir.iterdir(), reverse=True)
    if not runs:
        console.print("[red]No classified data found. Run classify.py first.[/red]")
        sys.exit(1)
    path = runs[0] / "qualified.json"
    console.print(f"Loading qualified candidates from [cyan]{path}[/cyan]")
    data = json.loads(path.read_text())
    if not data:
        console.print("[red]No qualified candidates found. Re-run classify.py.[/red]")
        sys.exit(1)
    return data


async def run_async() -> None:
    if not ANTHROPIC_API_KEY:
        console.print("[bold red]ANTHROPIC_API_KEY not set.[/bold red]")
        sys.exit(1)

    qualified = load_latest_qualified()
    console.print(f"Generating artifacts for [bold]{len(qualified)}[/bold] pain moments...\n")

    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUTS_DIR / "runs" / run_ts
    out_dir.mkdir(parents=True, exist_ok=True)

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    console.rule("[bold cyan]Stage 3: Generate[/bold cyan]")

    results = await asyncio.gather(*[
        generate_moment(client, sem, c, out_dir, run_ts)
        for c in qualified
    ])

    # Summary table
    console.rule("[bold green]Generated Artifacts[/bold green]")
    table = Table(box=box.ROUNDED)
    table.add_column("Score", justify="center", style="bold red", width=6)
    table.add_column("Repo", style="cyan", width=28)
    table.add_column("Pain Type", style="yellow", width=22)
    table.add_column("Output Dir", style="dim", width=45)

    for r in results:
        table.add_row(
            str(r["pain_score"]),
            r["repo"],
            r["pain_type"],
            r["dir"].replace(str(OUTPUTS_DIR), "outputs"),
        )
    console.print(table)

    # Preview top artifact
    best = max(results, key=lambda x: x.get("pain_score", 0))
    console.rule(f"[bold]Preview — top pain moment: {best['repo']}[/bold]")
    console.print(Panel(best["comment"], title="Public Comment", border_style="green"))
    console.print(Panel(best["outreach"], title="Outreach Message", border_style="blue"))

    console.print(f"\n[bold green]Done.[/bold green] All artifacts saved to [cyan]{out_dir}[/cyan]")


def run() -> None:
    asyncio.run(run_async())


if __name__ == "__main__":
    run()
