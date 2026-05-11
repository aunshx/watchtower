# Classification Prompt

You are evaluating whether a GitHub comment, PR, or issue is a real "AI-coding pain moment" that an open-source maintainer is experiencing.

A real AI-coding pain moment has these properties:
- The author (commenter or PR author) is a real person who is genuinely frustrated, confused, or burdened
- The frustration is specifically about AI-generated code (from Claude Code, Cursor, Copilot, Gemini CLI, or similar) — not about human-written code
- The pain is structural: missing context, oversized diffs, unclear intent, attribution confusion, review burden, merge conflicts between AI sessions
- The moment is recent enough (within the last 60 days) that intervention could still be useful

A signal is NOT a pain moment if:
- It's a generic complaint about code quality with no AI tie-in
- It's a feature request or bug report unrelated to AI code generation
- It's an AI-generated post itself (spam from an AI account)
- The frustration is resolved within the same thread (no remaining pain)
- The thread is more than 60 days old with no recent activity

## Pain Types

Tag with the most specific applicable type:
- `context_loss` — reviewer can't tell what the AI was trying to do; conversation history is gone
- `oversized_pr` — PR is too large to review, AI generated more than a human can sanely evaluate
- `intent_unclear` — code works but the *why* is missing
- `ai_authorship_concern` — maintainer worried about provenance, licensing, or attribution
- `ai_quality_complaint` — code quality is visibly degraded due to AI generation
- `merge_conflict_ai` — multiple AI sessions or agents stepped on each other
- `review_burden` — maintainer is drowning in AI-generated contributions
- `other` — genuine pain that doesn't fit above
- `not_a_pain_moment` — doesn't meet the bar

## Input

Source type: {source_type}
Repository: {repo}
URL: {url}
Title: {title}
Author: {author}
Is maintainer: {maintainer_signal}
Created: {created_at}
PR size (lines changed): {pr_size}

Body:
---
{body}
---

Context snippet:
---
{context_snippet}
---

## Output

Return ONLY a JSON object with this exact schema, no other text:

```json
{
  "pain_score": <integer 0-10, where 0 is "not a pain moment" and 10 is "textbook Entire-shaped pain">,
  "pain_type": "<one of the types above>",
  "rationale": "<one sentence explaining the score>",
  "entire_relevance": "<one sentence on how Entire's product would specifically help in this moment>",
  "maintainer_audience_size": "<small|medium|large — your guess at this maintainer's public reach based on the repo and any signals in the data>"
}
```
