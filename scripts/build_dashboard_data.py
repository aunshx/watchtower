"""Build web/public/data.json from the latest agent run outputs."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
WEB_PUBLIC = ROOT / "web" / "public"

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


def find_latest(base: Path, subdir: str) -> Path:
    d = base / subdir
    runs = sorted(d.iterdir(), reverse=True)
    if not runs:
        print(f"ERROR: no runs found in {d}", file=sys.stderr)
        sys.exit(1)
    return runs[0]


def read_text(path: Path) -> str:
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        return ""


def main() -> None:
    # Latest classified run
    classified_run = find_latest(DATA_DIR, "classified")
    qualified_path = classified_run / "qualified.json"
    scored_path = classified_run / "scored.json"

    qualified = json.loads(qualified_path.read_text())
    scored = json.loads(scored_path.read_text())
    print(f"Loaded {len(qualified)} qualified + {len(scored)} scored candidates")

    # Latest output run
    output_run = find_latest(OUTPUTS_DIR, "runs")
    print(f"Loading artifacts from {output_run}")

    # Parse run timestamp
    ts_str = output_run.name
    try:
        dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
        run_timestamp = dt.isoformat().replace("+00:00", "Z")
    except ValueError:
        run_timestamp = ts_str

    # Count raw candidates for funnel
    raw_runs = sorted((DATA_DIR / "raw").iterdir(), reverse=True)
    raw_count = 0
    if raw_runs:
        raw_path = raw_runs[0] / "candidates.json"
        try:
            raw_count = len(json.loads(raw_path.read_text()))
        except Exception:
            raw_count = 2774

    # Build pain moments (qualified only, with full artifacts)
    pain_moments = []
    for rank, c in enumerate(qualified, 1):
        mid = c["id"]
        moment_dir = output_run / f"pain_moment_{mid}"

        comment = read_text(moment_dir / "public_comment.md")
        outreach = read_text(moment_dir / "outreach.md")
        case_study = read_text(moment_dir / "case_study.md")

        if not any([comment, outreach, case_study]):
            print(f"  WARNING: no artifacts found for {mid}", file=sys.stderr)

        pain_moments.append({
            "id": mid,
            "rank": rank,
            "repo": c["repo"],
            "pain_type": c.get("pain_type", ""),
            "score": c.get("pain_score", 0),
            "signal": SIGNALS.get(mid) or (c.get("rationale") or "")[:200],
            "url": c["url"],
            "artifacts": {
                "comment": comment,
                "outreach": outreach,
                "case_study": case_study,
            },
            "classification": {
                "rationale": c.get("rationale", ""),
                "entire_relevance": c.get("entire_relevance", ""),
            },
        })

    artifacts_generated = sum(
        1 for m in pain_moments
        for v in m["artifacts"].values() if v
    )

    # Build classified candidates (all 100, sorted by score desc)
    scored_sorted = sorted(scored, key=lambda x: x.get("pain_score", 0), reverse=True)
    classified_candidates = [
        {
            "id": c.get("id", ""),
            "repo": c.get("repo", ""),
            "pain_score": c.get("pain_score", 0),
            "pain_type": c.get("pain_type", ""),
            "pain_rationale": c.get("rationale", ""),
            "url": c.get("url", ""),
            "author": c.get("author", ""),
        }
        for c in scored_sorted
    ]

    output = {
        "run_timestamp": run_timestamp,
        "funnel": {
            "raw_candidates": raw_count,
            "classified": 100,
            "qualified": len(qualified),
            "artifacts_generated": artifacts_generated,
        },
        "pain_moments": pain_moments,
        "classified_candidates": classified_candidates,
    }

    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)
    out_path = WEB_PUBLIC / "data.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"Written: {out_path} ({out_path.stat().st_size:,} bytes)")
    print(f"  Funnel: {output['funnel']}")
    print(f"  Pain moments: {len(pain_moments)}")
    print(f"  Classified candidates: {len(classified_candidates)}")


if __name__ == "__main__":
    main()
