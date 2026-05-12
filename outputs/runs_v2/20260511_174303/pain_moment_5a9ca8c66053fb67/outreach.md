Subject: claude/clever-mendel-a7Wc6 — branch sprawl across DomI/CHILmesh/ADMESH

Hey Dom,

Saw DomI#13 and the trail of session votes underneath it — the SDK harness injecting `claude/<random-name>` over your `daily-issue-fixing` mandate, then your `/enforce-branch-policy` skill in #20 as the pre-commit-hook fix. The 2026-05-09 CHILmesh note that naming the failure mode explicitly ("the SDK harness injects...") was what finally made the override unambiguous is a really sharp write-up.

I work on Entire (entire.io) — open-source CLI that captures Claude Code / Cursor sessions on git push and links the transcript + prompts to the resulting commit. Different layer than your pre-commit hook, but the captured session metadata (including the injected system prompt) would give you forensic data on *which* harness directive caused each sprawl event, across all four repos, without relying on the session itself to self-audit in a comment afterward.

Free, local, no signup. Happy to share notes on the harness-injection detection side if useful — otherwise feel free to ignore.

— [NAME]