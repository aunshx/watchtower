"""Run the agentic generator. By default tests a single (moment, artifact) pair.

Usage:
  python scripts/run_agent_generator.py                  # test: HF moment, public_comment
  python scripts/run_agent_generator.py --all            # run all 15 (requires approval)
  python scripts/run_agent_generator.py --moment <id> --artifact <type>
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from config import DATA_DIR, OUTPUTS_DIR
from agent_generator import run_agent

console = Console()

ARTIFACT_TYPES = ["public_comment", "outreach", "case_study"]
TEST_MOMENT_ID = "e43473edca79af21"  # HuggingFace transformers, score=8


def load_qualified() -> list:
    classified_dir = DATA_DIR / "classified"
    runs = sorted(classified_dir.iterdir(), reverse=True)
    path = runs[0] / "qualified.json"
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Run all 15 artifacts (requires prior approval)")
    parser.add_argument("--moment", default=TEST_MOMENT_ID, help="Pain moment ID to run")
    parser.add_argument("--artifact", default="public_comment", choices=ARTIFACT_TYPES)
    args = parser.parse_args()

    qualified = load_qualified()
    moment_by_id = {c["id"]: c for c in qualified}

    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUTS_DIR / "runs_v2" / run_ts
    run_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        pairs = [(m, a) for m in qualified for a in ARTIFACT_TYPES]
        console.rule("[bold red]Full run — all 15 artifacts[/bold red]")
    else:
        moment = moment_by_id.get(args.moment)
        if not moment:
            console.print(f"[red]Moment {args.moment} not found in qualified.json[/red]")
            sys.exit(1)
        pairs = [(moment, args.artifact)]
        console.rule(f"[bold cyan]Test run — {args.moment[:8]} / {args.artifact}[/bold cyan]")

    all_traces = []
    total_input = 0
    total_output = 0

    for moment, artifact_type in pairs:
        console.print(f"\n[bold]{moment['repo']}[/bold] → [yellow]{artifact_type}[/yellow]")
        trace = run_agent(moment, artifact_type, run_dir)
        all_traces.append(trace)
        total_input += trace["total_input_tokens"]
        total_output += trace["total_output_tokens"]

    # ── Summary ───────────────────────────────────────────────────────────────
    console.rule("[bold green]Run complete[/bold green]")

    table = Table(box=box.ROUNDED)
    table.add_column("Moment", style="cyan")
    table.add_column("Artifact", style="yellow")
    table.add_column("Tool calls", justify="right")
    table.add_column("Iterations", justify="right")
    table.add_column("In tokens", justify="right")
    table.add_column("Out tokens", justify="right")

    for t in all_traces:
        table.add_row(
            t["moment_id"][:8],
            t["artifact_type"],
            str(t["total_tool_calls"]),
            str(t["total_iterations"]),
            str(t["total_input_tokens"]),
            str(t["total_output_tokens"]),
        )

    console.print(table)
    console.print(f"\nTotal input tokens:  {total_input:,}")
    console.print(f"Total output tokens: {total_output:,}")
    approx_cost = (total_input * 5 + total_output * 25) / 1_000_000
    console.print(f"Approx cost (Opus):  ${approx_cost:.3f}")
    console.print(f"\nOutputs: [cyan]{run_dir}[/cyan]")

    if not args.all and all_traces:
        t = all_traces[0]
        console.rule("[bold]Final artifact[/bold]")
        console.print(Panel(t["final_artifact"], border_style="green"))


if __name__ == "__main__":
    main()
