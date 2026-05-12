The Code Agent Policy in this template is striking — especially the line drawing a distinction between "drafting/diagnosis" use (fine) and "pure code agent PRs" (closed without review). The hard part is that both look identical in the diff: a reviewer has no signal for whether a human actually drove the session or just pasted the output.

We've been building [Entire](https://entire.io) for exactly that gap. It's an open-source CLI that captures Claude Code / Copilot / Cursor sessions locally and links the transcript + prompts to the commits on `git push`, so a PR surfaces *what was asked and why*, not just what changed. That's roughly the provenance signal your policy is implicitly asking for.

Install: `curl -fsSL https://entire.io/install.sh | bash` · [docs](https://entire.io)