"""Compare v1 and v2 artifacts side-by-side.

Usage:
  python scripts/compare_artifacts.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
from config import OUTPUTS_DIR

ARTIFACT_MAP = {
    "public_comment": "public_comment.md",
    "outreach": "outreach.md",
    "case_study": "case_study.md",
}


def find_latest(base: Path) -> Path | None:
    runs = sorted(base.iterdir(), reverse=True) if base.exists() else []
    return runs[0] if runs else None


def read_artifact(moment_dir: Path, filename: str) -> str:
    p = moment_dir / filename
    return p.read_text().strip() if p.exists() else "(not found)"


def word_count(text: str) -> int:
    return len(text.split())


def main():
    v1_dir = find_latest(OUTPUTS_DIR / "runs")
    v2_dir = find_latest(OUTPUTS_DIR / "runs_v2")

    if not v1_dir or not v2_dir:
        print("ERROR: Need at least one v1 run and one v2 run.")
        sys.exit(1)

    # Find common pain moment IDs across both runs
    v1_moments = {p.name.replace("pain_moment_", "") for p in v1_dir.glob("pain_moment_*") if p.is_dir()}
    v2_moments = {p.name.replace("pain_moment_", "") for p in v2_dir.glob("pain_moment_*") if p.is_dir()}
    common = sorted(v1_moments & v2_moments)

    if not common:
        print("No common pain moments between v1 and v2 runs.")
        print(f"  v1: {sorted(v1_moments)}")
        print(f"  v2: {sorted(v2_moments)}")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUTS_DIR / f"comparison_{ts}.md"

    lines = [
        "# Artifact Comparison: v1 (single-shot) vs v2 (agentic ReAct)\n",
        f"**v1 run:** `{v1_dir.name}`  ",
        f"**v2 run:** `{v2_dir.name}`  ",
        f"**Common moments:** {len(common)}  ",
        "",
    ]

    for mid in common:
        v1_moment_dir = v1_dir / f"pain_moment_{mid}"
        v2_moment_dir = v2_dir / f"pain_moment_{mid}"

        # Load trace for metadata
        trace_files = list(v2_moment_dir.glob("*_trace.json"))
        v2_meta = {}
        if trace_files:
            v2_meta = json.loads(trace_files[0].read_text())

        lines.append(f"---\n## Moment `{mid[:8]}` — {v2_meta.get('repo', '')}\n")

        for artifact_key, filename in ARTIFACT_MAP.items():
            v1_text = read_artifact(v1_moment_dir, filename)
            v2_text = read_artifact(v2_moment_dir, filename)

            if v1_text == "(not found)" and v2_text == "(not found)":
                continue

            lines.append(f"### {artifact_key.replace('_', ' ').title()}\n")

            # Structural diff summary
            v1_wc = word_count(v1_text)
            v2_wc = word_count(v2_text)
            diff = v2_wc - v1_wc
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            lines.append(f"Word count: v1={v1_wc} → v2={v2_wc} ({diff_str})  \n")

            # Load trace for this artifact type
            trace_path = v2_moment_dir / f"{artifact_key}_trace.json"
            if trace_path.exists():
                trace = json.loads(trace_path.read_text())
                lines.append(f"Agent: {trace['total_tool_calls']} tool calls, "
                              f"{trace['total_iterations']} iterations, "
                              f"{trace['total_input_tokens']:,} input tokens  \n")

            lines.append("\n**v1 (single-shot):**\n")
            lines.append("```")
            lines.append(v1_text)
            lines.append("```\n")

            lines.append("**v2 (agentic):**\n")
            lines.append("```")
            lines.append(v2_text)
            lines.append("```\n")

    out_path.write_text("\n".join(lines))
    print(f"Comparison written: {out_path}")


if __name__ == "__main__":
    main()
