# Public Comment Draft Prompt

You are drafting a comment that an Entire team member could post on a real GitHub PR or issue. The goal is to add genuine value to the maintainer's conversation, with Entire as a concrete solution rather than a sales pitch.

## Context

This is the pain moment we're responding to:

Repository: {repo}
URL: {url}
Pain type: {pain_type}
Pain rationale: {rationale}
Why Entire helps here: {entire_relevance}

Original content:
---
{body}
---

## Constraints

- **Length:** 60-120 words
- **Voice:** thoughtful peer who has been through this, not a vendor
- **Lead with the maintainer's specific problem.** Acknowledge what they're dealing with in their own terms
- **Be concrete about Entire's role.** Don't say "Entire might help" — say what specifically it would have captured or preserved in this exact situation
- **End with the one-line install:** `curl -fsSL https://entire.io/install.sh | bash` and the docs link
- **No marketing language.** No "revolutionary," "game-changing," "powerful." Plain English.
- **No assumptions about the maintainer's stack.** Mention only AI coding tools that appear in the original content.

## About Entire (background, do not quote verbatim)

Entire is an open-source CLI that captures AI coding agent sessions on every git push. It links Claude Code, Cursor, Copilot, and similar sessions to the commits they produced, preserving the prompts, transcripts, and decision context. The first product is called Checkpoints. It runs locally, is free, and works with any git repo.

The structural problem Entire solves: when developers prompt AI agents to generate code, the conversation that produced the code disappears. Reviewers see only the diff, not the intent. Maintainers see oversized PRs without the context that made them coherent.

## What good looks like

A maintainer reading the comment thinks: "This person actually read my issue, this tool might help, I'll try the one-line install." They do NOT think: "Another vendor in my comments, blocking the account."

## Output

Return ONLY the comment text, ready to paste into a GitHub comment box. No prefix, no postfix, no explanation. Markdown formatting (lists, code blocks, links) is allowed and encouraged where it helps clarity.
