Subject: The "pure agent PR" filter problem on transformers

Hi Arthur,

Saw the Code Agent Policy you added to the PR template (#45892 / CONTRIBUTING.md) — "bottlenecked by our ability to review and respond to them" is a brutal sentence to have to write. And the fact that on #45396 you noted you "needed both claude and copilot's help on this one 😅" makes the line you're trying to draw really clear: agent-assisted is fine, pure agent PRs are not. The hard part is telling them apart at triage time, before a human burns 20 minutes on one.

We're building Entire — an open-source CLI (Checkpoints) that captures Claude Code / Cursor / Copilot sessions locally on `git push` and links transcripts + prompts to the commits they produced. The byproduct is exactly the provenance signal your AGENTS.md is trying to enforce: who drove the work, what the human actually asked for, what the agent decided on its own.

Happy to share what we've seen from other large repos hitting the same wall, or just hand you the CLI to poke at. No pitch — feel free to ignore.

— [NAME], Entire (entire.io)