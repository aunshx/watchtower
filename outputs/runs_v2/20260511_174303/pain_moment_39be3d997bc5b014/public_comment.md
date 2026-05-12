The policy draws a useful line: agent-assisted drafting and diagnosis is fine; "pure code agent PRs" with no human intent are what's drowning review. The hard part is reviewers can't tell which is which from the diff alone — the conversation that produced the code is gone by the time the PR lands.

We've been working on exactly that gap with [Entire](https://entire.io) — an open-source CLI that captures Claude Code / Codex sessions locally on `git push` and links the prompts and transcripts to the commits they produced. For a repo like this, a reviewer (or a triage bot reading `AGENTS.md`-style metadata) could see at a glance whether a PR was a human iterating with an agent, or an autonomous run on someone else's issue.

Free, local, any git repo:

```
curl -fsSL https://entire.io/install.sh | bash
```

Docs: https://entire.io/docs