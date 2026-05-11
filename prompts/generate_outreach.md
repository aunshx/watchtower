# Outreach Message Draft Prompt

You are drafting a personalized message that an Entire team member could send to a maintainer through public contact channels (X DM, email, LinkedIn). Offline follow-up to a real pain moment.

## Context

This is the pain moment we're responding to:

Repository: {repo}
Maintainer: {author}
URL: {url}
Pain type: {pain_type}
Pain rationale: {rationale}
Why Entire helps here: {entire_relevance}
Maintainer audience size: {maintainer_audience_size}

Original content:
---
{body}
---

## Constraints

- **Length:** 80-150 words
- **Voice:** peer-to-peer, builder talking to builder. Not vendor-to-prospect.
- **Subject line / opener:** reference the specific repo and the specific situation. Not "I saw your post" — "I saw your comment on PR #1234 in {repo}."
- **Show you read it.** Reference something specific from the original content. A phrase, a detail, the technical specifics of what they were struggling with.
- **Don't pitch.** Don't say "I'd love to show you a demo" or "let me schedule 15 minutes." Just offer concrete help.
- **No CTA pressure.** End with a low-stakes offer ("happy to share notes," "feel free to ignore"). The goal of this message is to start a real conversation, not to book a call.
- **Sign as a real human.** Use a placeholder `[NAME]` for the sender's name. Assume the sender is a member of Entire's GTM team, not Dohmke himself.

## About Entire (background, do not quote verbatim)

Entire is an open-source CLI that captures AI coding agent sessions on every git push. It links Claude Code, Cursor, Copilot, and similar sessions to the commits they produced, preserving the prompts, transcripts, and decision context. The first product is called Checkpoints. It runs locally, is free, and works with any git repo.

## What good looks like

The maintainer thinks: "This isn't a templated cold message. This person actually saw my specific problem and has something concrete that might help. I'll write back." They do NOT think: "Standard SaaS outreach, archive."

## Output format

Return ONLY the message text, ready to send. Include a subject line as the first line if appropriate (for email) or a one-line opener (for DM). No explanation, no preamble.

If sending via X DM or LinkedIn, no subject line is needed.
If sending via email, include `Subject: ` as the first line.
