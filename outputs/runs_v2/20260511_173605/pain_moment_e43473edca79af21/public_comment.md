The policy reads like the real problem isn't AI — it's contextless agent PRs arriving as opaque diffs with no intent attached. Your contributing guide still allows agents "in drafting or to help diagnose issues," so the missing piece sounds more like provenance than the tool itself.

That's roughly what we built [Entire](https://entire.io) for. Open-source CLI that captures Claude Code / Copilot sessions locally on each `git push` and links the transcript and prompts to the commit. A reviewer could see at a glance: human-driven with assist, or fully autonomous? What were they actually trying to do?

Runs locally, free, no server:

```
curl -fsSL https://entire.io/install.sh | bash
```

Docs: https://entire.io/docs — would genuinely value hearing whether that signal would help triage, or where it falls short for a repo at your scale.