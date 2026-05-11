# Checkpoint Scout

A go-to-market agent for Entire (entire.io). Scans public GitHub for moments where open-source maintainers are visibly struggling with AI-generated code, and drafts three artifacts per pain moment that Entire's GTM team could ship.

## What it does

For each detected pain moment, generates:
1. **Public comment** — a useful, non-spammy draft comment for the PR or issue thread
2. **Outreach message** — a personalized DM/email to the maintainer for offline follow-up
3. **Case study skeleton** — a draft blog post Entire could publish

All outputs are drafts saved to disk. Nothing is auto-posted to GitHub.

## Architecture

Three stages:
1. **Acquire** (`src/acquire.py`) — Pull recent PRs and issue comments from a curated list of large OSS repos via GitHub API
2. **Classify** (`src/classify.py`) — For each candidate, ask Claude to score whether it's a real AI-coding pain moment and tag the pain type
3. **Generate** (`src/generate.py`) — For each high-scoring pain moment, draft the three artifacts

## The bet

Entire is in a race-to-default category creation play. The wedge: hijack acute pain moments in public OSS workflows where Entire is the obvious answer, before incumbents (GitHub, Cursor, Anthropic) absorb the context-preservation layer.

Target persona: open-source maintainers, not enterprise compliance buyers. They have the loudest public voice and the most existential pain right now from AI-generated PR slop.

## Setup

```bash
cp .env.example .env
# Fill in GITHUB_TOKEN
pip install -r requirements.txt
python src/acquire.py
python src/classify.py
python src/generate.py
```

## Why this design

- **Targets pain, not lists.** Most GTM agents personalize cold outreach to a prospect list. This one ignores lists and chases moments.
- **Drafts, never posts.** Auto-posting promotional comments on OSS would be spam. Human-in-the-loop is the only ethical version.
- **Useful outputs even if not shipped.** The case study skeleton has standalone marketing value. The PR comment, if shipped, adds value to the maintainer's conversation regardless of whether they adopt Entire.

## Status

Prototype built in one day for the Basis Set AI Fellowship application. See `docs/writeup.md` for the full thinking.
