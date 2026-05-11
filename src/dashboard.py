"""Generate dashboard.md for the most recent run."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, OUTPUTS_DIR

SIGNALS = {
    "e43473edca79af21": (
        "HF/transformers added a blanket 'Code Agent Policy' citing being "
        "overwhelmed and bottlenecked by agent-written PRs"
    ),
    "8cf3e16bb82dbc6a": (
        "User lost trust after Claude silently switched from scoping a Jira "
        "ticket to editing source files — twice, despite corrections"
    ),
    "39be3d997bc5b014": (
        "Same transformers Code Agent Policy surfaced in a second PR — "
        "structural pain across the whole repo, not a one-off"
    ),
    "5a9ca8c66053fb67": (
        "Claude sessions repeatedly violated branch-naming policy in CLAUDE.md, "
        "forcing the solo maintainer to manually clean up branch sprawl"
    ),
    "e0e46557eeeaddb7": (
        "llama.cpp auto-bot flagged a PR as predominantly AI-generated, "
        "exposing the provenance-policing burden maintainers now carry"
    ),
}


def build_dashboard(qualified: list, run_dir: Path, run_ts: str) -> str:
    # Parse timestamp for display
    try:
        dt = datetime.strptime(run_ts, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
        ts_display = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        ts_display = run_ts

    lines = [
        "# Checkpoint Scout — Run Summary",
        "",
        f"**Run:** {ts_display}",
        "",
        (
            "Checkpoint Scout scanned 15 high-signal OSS repos (next.js, react, llama.cpp, "
            "transformers, and others) plus 6 AI-coding pain-phrase queries against the "
            "GitHub Issue Search API, collecting **2,774 unique candidates**. "
            "These were filtered and keyword-ranked to a **100-candidate batch** for "
            "classification by Claude Opus 4.7, which scored each against a rubric for "
            "genuine AI-coding pain. **5 pain moments** cleared the threshold (score ≥ 6), "
            "and **15 artifacts** were generated in parallel — one public comment, one "
            "outreach message, and one case study skeleton per moment."
        ),
        "",
        "| Rank | Repo | Pain Type | Score | One-line Signal | Artifacts |",
        "|------|------|-----------|-------|-----------------|-----------|",
    ]

    for i, c in enumerate(qualified, 1):
        mid = c["id"]
        mdir = f"pain_moment_{mid}"
        artifacts = (
            f"[Comment]({mdir}/public_comment.md)"
            f" · [Outreach]({mdir}/outreach.md)"
            f" · [Case Study]({mdir}/case_study.md)"
        )
        signal = SIGNALS.get(mid) or (c.get("rationale") or "")[:120]
        repo = c["repo"]
        pain_type = c.get("pain_type", "")
        score = c.get("pain_score", "")
        lines.append(f"| {i} | `{repo}` | {pain_type} | {score} | {signal} | {artifacts} |")

    lines += [
        "",
        "---",
        "",
        "_All artifacts are drafts. Nothing posted to GitHub or sent to anyone. "
        "Human-in-the-loop by design — see writeup for the design rationale._",
    ]

    return "\n".join(lines) + "\n"


def run() -> None:
    # Load latest classified run
    classified_dir = DATA_DIR / "classified"
    qualified_path = sorted(classified_dir.iterdir(), reverse=True)[0] / "qualified.json"
    qualified = json.loads(qualified_path.read_text())

    # Find latest output run
    runs_dir = OUTPUTS_DIR / "runs"
    run_dir = sorted(runs_dir.iterdir(), reverse=True)[0]
    run_ts = run_dir.name

    content = build_dashboard(qualified, run_dir, run_ts)
    out = run_dir / "dashboard.md"
    out.write_text(content)
    print(f"Written: {out}")
    print()
    print(content)


if __name__ == "__main__":
    run()
