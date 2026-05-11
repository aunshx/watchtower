# Case Study Skeleton Prompt

You are drafting a short case study (or "field note") that Entire could publish on their blog. The case study draws inspiration from a real pain moment but is sanitized to avoid identifying the specific maintainer or repo.

## Context

This is the pain moment we're drawing from:

Pain type: {pain_type}
Pain rationale: {rationale}
Why Entire helps here: {entire_relevance}
General context (do NOT reference specific names or repos in the output):
---
{body}
---

## Constraints

- **Length:** 200-300 words
- **Sanitize.** Do not name the specific repo, maintainer, PR, or any identifying detail. Reframe as "a maintainer of a popular open-source library" or similar.
- **Voice:** Entire's voice from their launch post — thoughtful, builder-to-builder, structural reasoning. Examples of phrases that match this voice: "the fundamental role of a developer has been refactored," "machines are the primary producers of code," "Git was never extended to version everything developers build with in the AI era." Don't quote these directly, but match the register.
- **Structure** (do not literally label the sections, but follow this arc):
  - **Hook (1-2 sentences):** the scene. A real moment.
  - **What happened (2-3 sentences):** the pain incident, generalized.
  - **What was lost (2-3 sentences):** the context, intent, or reasoning that disappeared.
  - **What Entire would capture (2-3 sentences):** the specific thing Checkpoints would have preserved.
  - **The structural insight (1-2 sentences):** the broader point about software development in the AI era.
- **No marketing language.** Plain English. No "revolutionary," "transform," "unlock."
- **No CTA at the bottom.** This is a thought piece, not a sales asset. If it makes someone curious, the docs link in the post bio is enough.

## About Entire (background, do not quote verbatim)

Entire is building the next developer platform for the AI era. The first product is Checkpoints: an open-source CLI that captures AI coding agent sessions on every git push, linking sessions to the commits they produced. The platform's longer thesis is that the unit of work in software has shifted — from human-written code that humans review, to agent-written code that needs preserved context to be reviewable, queryable, and trustworthy.

## What good looks like

A reader who's been frustrated by AI-PR review burden thinks: "Yeah, this is exactly the problem. I should try Checkpoints." A reader who has not yet felt this pain thinks: "This is going to matter to me in three months when our team starts shipping agent-generated code more aggressively."

## Output

Return ONLY the case study text in markdown, ready to publish. Include a working title at the top as a `# heading`. No explanation, no preamble.
