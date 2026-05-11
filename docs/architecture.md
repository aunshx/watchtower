# Checkpoint Scout — Architecture & Build Spec

> This document is the source of truth for what we're building. Hand it to Claude Code in the first session to ground the work.

## Mission

Build a GTM agent for Entire (entire.io) that scans public GitHub for moments where open-source maintainers are visibly struggling with AI-generated code, and drafts three artifacts per pain moment that Entire's GTM team could ship the next day.

## The thesis the agent embodies

Entire is racing to become the default substrate for AI-generated code before incumbents (GitHub, Cursor, Anthropic) absorb the context-preservation layer. The fastest path to default is not enterprise sales (too slow given Entire's seed stage) and not generic developer marketing (too noisy). It's hijacking acute pain moments in public OSS workflows where Entire is the obvious answer.

Wedge persona: open-source maintainers, not enterprise compliance buyers. They have the loudest public voice and the most existential pain right now from AI-PR slop.

## Pipeline (three stages)

### Stage 1: Acquire

Pull recent pain signals from GitHub public API.

**Inputs:** GitHub token, list of target repos, list of search queries

**What it does:**
- For each target repo, fetch recent PRs and their comments (last 30 days)
- Run GitHub Issue Search for AI-coding pain phrases
- Store raw results to `data/raw/{timestamp}/candidates.json`

**Output schema** (one entry per candidate):
```json
{
  "id": "string",
  "source_type": "pr_comment|issue|search_result",
  "repo": "owner/name",
  "url": "https://github.com/...",
  "title": "string",
  "body": "string (the comment text or PR body)",
  "author": "string (commenter username)",
  "maintainer_signal": "bool (is the author a repo maintainer)",
  "created_at": "ISO8601",
  "pr_size": "int (lines changed, if available)",
  "context_snippet": "string (surrounding text or PR description)"
}
```

**Filters at this stage:**
- Skip if body length under 50 chars (likely too thin to classify)
- Skip if older than 60 days
- Dedupe by URL

### Stage 2: Classify

For each candidate, call Claude to score whether it's a real AI-coding pain moment and tag the pain type.

**Input:** the candidate JSON from Stage 1

**Prompt structure** (see `prompts/classify.md` for the full prompt):
- Provide the candidate's body, repo context, and PR/issue metadata
- Ask Claude to return structured JSON with pain_score (0-10), pain_type, and a one-sentence rationale
- Pain types: `context_loss`, `oversized_pr`, `intent_unclear`, `ai_authorship_concern`, `ai_quality_complaint`, `merge_conflict_ai`, `review_burden`, `other`, `not_a_pain_moment`

**Output:** `data/classified/{timestamp}/scored.json` with original candidate plus classification fields

**Filter:** keep only entries with pain_score >= 6 and pain_type != "not_a_pain_moment"

### Stage 3: Generate

For each high-scoring pain moment, draft three artifacts in parallel.

**Artifact A: Public Comment Draft**

A comment that could be posted on the actual PR/issue thread (if a human at Entire decides to ship it).

Tone: useful first, promotional second. The comment should add genuine value to the conversation regardless of whether the maintainer adopts Entire. Lead with the specific problem the maintainer is facing, offer Entire as a concrete tool, end with a one-line install command.

Length: 60-120 words.

**Artifact B: Outreach Message Draft**

A personalized DM/email Entire could send through public contact channels (X DM, email, LinkedIn) to the maintainer.

Tone: peer-to-peer, not vendor-to-prospect. References the specific repo, the specific pain incident, and the maintainer's broader work. Offers concrete help, ends with a no-pressure CTA.

Length: 80-150 words.

**Artifact C: Case Study Skeleton**

A draft blog post Entire could publish (sanitized to remove identifying details).

Tone: Entire's voice (from their `entire.io/blog/hello-entire-world` launch post: thoughtful, builder-to-builder, structural reasoning).

Structure: Hook (the problem), the scene (what happened in this incident, generalized), the cost (what was lost without context), the alternative (what Entire would have captured), the lesson (the structural insight).

Length: 200-300 words.

**Output:** `outputs/runs/{timestamp}/pain_moment_{id}/` with:
- `source.json` — original PR/issue data
- `classification.json` — pain score and type
- `public_comment.md`
- `outreach.md`
- `case_study.md`
- `meta.json` — generation metadata (model used, prompt versions, timestamps)

## Quality bar

For the submission, we want 2-3 pain moments where all three artifacts are good enough that Entire could realistically ship them. Hand-pick the best three after running on ~5-10 candidates.

## What this agent is NOT

- Not a list-personalization tool (it ignores prospect lists entirely)
- Not an autonomous posting tool (drafts only, human in the loop)
- Not a comprehensive scraper (focuses on quality of pain moments, not volume)
- Not a sales tool (the outputs are useful content first, lead-gen second)

## Stretch features (if time permits)

- Add X/Twitter scanning for public maintainer posts complaining about AI PRs
- Add a "decay" filter so we don't surface moments that have already been resolved
- Generate a one-page "pain moment dashboard" HTML report showing the top moments visually
- Self-reference: instrument the agent with Entire CLI and include the generated checkpoints as part of the submission, demonstrating Entire's product working on the agent that builds with Entire's product
