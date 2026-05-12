"""Agentic generator — ReAct-style loop with tool use for each artifact."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent))
from config import ANTHROPIC_API_KEY, OUTPUTS_DIR
from tools import TOOL_SCHEMAS, execute_tool

console = Console()

SYSTEM_TMPL = (Path(__file__).parent.parent / "prompts" / "agent_system_v2.md").read_text()
ARTIFACT_PROMPTS = {
    "public_comment": (Path(__file__).parent.parent / "prompts" / "generate_comment.md").read_text(),
    "outreach": (Path(__file__).parent.parent / "prompts" / "generate_outreach.md").read_text(),
    "case_study": (Path(__file__).parent.parent / "prompts" / "generate_case_study.md").read_text(),
}

MAX_TOOL_CALLS = 10
MAX_ITERATIONS = 20
MODEL = "claude-opus-4-7"


def _fill(template: str, **fields) -> str:
    result = template
    for key, value in fields.items():
        result = result.replace("{" + key + "}", str(value) if value is not None else "")
    return result


def _build_user_message(moment: dict, artifact_type: str) -> str:
    tmpl = ARTIFACT_PROMPTS[artifact_type]
    artifact_guidance = _fill(
        tmpl,
        repo=moment.get("repo", ""),
        url=moment.get("url", ""),
        author=moment.get("author", "maintainer"),
        pain_type=moment.get("pain_type", ""),
        rationale=moment.get("rationale", ""),
        entire_relevance=moment.get("entire_relevance", ""),
        maintainer_audience_size=moment.get("maintainer_audience_size", "medium"),
        body=(moment.get("body") or "")[:3000],
        context_snippet=(moment.get("context_snippet") or "")[:500],
    )

    return f"""## Pain moment

ID: {moment['id']}
Repo: {moment['repo']}
URL: {moment['url']}
Author: {moment.get('author', 'unknown')}
Pain type: {moment.get('pain_type', '')}
Score: {moment.get('pain_score', '')}
Signal: {moment.get('rationale', '')}
Entire relevance: {moment.get('entire_relevance', '')}

Body (excerpt):
---
{(moment.get('body') or '')[:2000]}
---

## Artifact guidance

{artifact_guidance}

## Your task

Produce a high-quality {artifact_type.replace('_', ' ')} using the tools above. \
Call research tools to gather context, draft, critique, refine, then call \
submit_final_artifact when done."""


def run_agent(
    moment: dict,
    artifact_type: str,
    run_dir: Path,
) -> dict:
    """
    Run the ReAct loop for one (moment, artifact_type) pair.
    Returns dict with final_artifact, trace, token_usage.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    system_msg = SYSTEM_TMPL.replace("{artifact_type}", artifact_type.replace("_", " "))

    messages: list[dict] = [
        {"role": "user", "content": _build_user_message(moment, artifact_type)},
    ]

    trace: list[dict] = []
    tool_call_count = 0
    final_artifact: str | None = None
    total_input_tokens = 0
    total_output_tokens = 0

    console.print(
        f"  [dim]→ {artifact_type} | moment {moment['id'][:8]}[/dim]"
    )

    for iteration in range(MAX_ITERATIONS):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=system_msg,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )
        except anthropic.APIError as e:
            console.print(f"    [red]API error: {e}[/red]")
            trace.append({"iteration": iteration, "error": str(e)})
            break

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # Build trace entry
        trace_entry: dict[str, Any] = {
            "iteration": iteration,
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "content": [],
        }

        # Extract text blocks for trace
        text_parts = []
        tool_uses = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
                trace_entry["content"].append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                tool_uses.append(block)
                trace_entry["content"].append({
                    "type": "tool_use",
                    "name": block.name,
                    "id": block.id,
                    "input": block.input,
                })

        trace.append(trace_entry)

        # End turn with no tool calls → capture text as final (fallback)
        if response.stop_reason == "end_turn" and not tool_uses:
            if text_parts:
                final_artifact = "\n\n".join(text_parts).strip()
                console.print(f"    [yellow]Text fallback (no submit_final_artifact called)[/yellow]")
            break

        # Process tool calls
        if not tool_uses:
            break

        # Append assistant turn to messages
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in tool_uses:
            tool_name = block.name
            tool_input = block.input

            if tool_name == "submit_final_artifact":
                final_artifact = tool_input.get("artifact", "")
                console.print(f"    [green]✓ submit_final_artifact called[/green]")
                # Still need to send a tool result to satisfy API requirements
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": "Artifact submitted.",
                })
                # Add the tool result message, then break out of the loop
                messages.append({"role": "user", "content": tool_results})
                trace.append({"iteration": iteration, "note": "submit_final_artifact received, loop ending"})
                break
            else:
                tool_call_count += 1
                console.print(
                    f"    [dim]tool_call {tool_call_count}/{MAX_TOOL_CALLS}: {tool_name}[/dim]"
                )
                result_str = execute_tool(tool_name, tool_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

                # Check tool budget
                if tool_call_count >= MAX_TOOL_CALLS:
                    console.print(
                        f"    [yellow]Tool call limit ({MAX_TOOL_CALLS}) reached[/yellow]"
                    )
                    messages.append({"role": "user", "content": tool_results})
                    messages.append({
                        "role": "user",
                        "content": (
                            "You have reached the tool call limit. "
                            "Write your final artifact now and call submit_final_artifact."
                        ),
                    })
                    tool_results = []
                    break

        # If we broke out due to submit_final_artifact, stop the outer loop too
        if final_artifact is not None:
            break

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    # ── Save outputs ──────────────────────────────────────────────────────────
    moment_dir = run_dir / f"pain_moment_{moment['id']}"
    moment_dir.mkdir(parents=True, exist_ok=True)

    artifact_text = final_artifact or "[Generation produced no output]"
    (moment_dir / f"{artifact_type}.md").write_text(artifact_text)

    trace_data = {
        "artifact_type": artifact_type,
        "moment_id": moment["id"],
        "repo": moment["repo"],
        "model": MODEL,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tool_calls": tool_call_count,
        "total_iterations": len(trace),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "final_artifact": artifact_text,
        "trace": trace,
    }
    (moment_dir / f"{artifact_type}_trace.json").write_text(json.dumps(trace_data, indent=2))

    return trace_data
