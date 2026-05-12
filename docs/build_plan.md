# Claude Code Session Plan — Build Day

This file is your script for the day. You'll run Claude Code on your machine, with Entire CLI capturing every session. Each section below is one Claude Code session.

**Before you start each session:** make sure Entire is running on this repo (`entire enable` was run, and the project directory is the active one).

**After each session ends:** Entire should have a fresh checkpoint. You can verify with whatever command Entire provides for listing recent checkpoints.

---

## Session 0: Setup (5 minutes, no Claude Code needed)

```bash
mkdir watchtower
cd watchtower
git init
cp /path/to/scaffold/* .
entire enable
```

Then copy `.env.example` to `.env` and fill in your `GITHUB_TOKEN`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Session 1: Build the acquire stage (45-60 min)

Open Claude Code in the project directory. Start a new session.

**Prompt to give Claude Code:**

> I'm building a GTM agent for Entire (entire.io) called Watchtower. Read `docs/architecture.md` for the full design. We're starting with Stage 1: Acquire.
>
> Build `src/acquire.py` that:
> 1. Reads target repos and search queries from `src/config.py`
> 2. For each target repo, pulls the last 30 days of PRs and their comments via PyGithub
> 3. Runs each pain search query against GitHub's issue search API
> 4. Filters out candidates with body shorter than 50 chars or older than 60 days
> 5. Dedupes by URL
> 6. Saves to `data/raw/{timestamp}/candidates.json` with the exact schema in architecture.md
> 7. Prints a `rich`-formatted summary table showing candidates found per repo and per query
>
> Use `python-dotenv` to load `GITHUB_TOKEN` from `.env`. Handle GitHub rate limits gracefully — if we hit the limit, sleep until reset and continue. Log progress with `rich.console.Console`.
>
> When done, run it and show me the output. Don't worry if some queries return zero results, that's expected.

After it builds, verify the data looks right. You should have maybe 30-100 candidates in the JSON file.

**What to look for in the captured Entire checkpoint:** Claude Code's reasoning about rate limiting, the structure of the GitHub API responses, any debugging back-and-forth.

---

## Session 2: Build the classify stage (45-60 min)

New Claude Code session.

**Prompt:**

> Continuing Watchtower. Stage 1 (acquire) is done — you'll find raw candidates in `data/raw/`. Now build `src/classify.py`.
>
> Build `src/classify.py` that:
> 1. Loads the most recent `candidates.json` from `data/raw/`
> 2. For each candidate (cap at `MAX_CANDIDATES_TO_CLASSIFY` from config), calls Claude to classify it as a pain moment
> 3. Use the prompt template in `prompts/classify.md` — substitute the candidate fields into the template
> 4. Parse the JSON response. Be defensive — if Claude returns malformed JSON, log it and skip
> 5. Add the classification fields to each candidate
> 6. Filter to candidates with pain_score >= MIN_PAIN_SCORE and pain_type != "not_a_pain_moment"
> 7. Save the full set (scored, including filtered-out) to `data/classified/{timestamp}/scored.json`
> 8. Save the filtered top set to `data/classified/{timestamp}/qualified.json`, sorted by pain_score descending
> 9. Print a rich table showing the top 10 by pain score, with repo, pain_type, and rationale
>
> Use the Anthropic SDK with Claude (model: claude-opus-4-7). Read `ANTHROPIC_API_KEY` from `.env`. If the key isn't set, fall back to a stub that just prints the prompts to stdout for manual review (we'll figure out the API key situation if needed).
>
> Run it after building.

**Note on the API key:** If you don't have an Anthropic API key set up yet, this session also doubles as the moment you decide whether to put $5 on a key or use the stub mode and manually run the classifications in Claude Code itself. Either works.

---

## Session 3: Build the generate stage (60-90 min)

New Claude Code session. This is the most important stage — the artifacts produced here are what the reviewer will read.

**Prompt:**

> Continuing Watchtower. Stages 1 and 2 are done. Now build `src/generate.py` — the final stage.
>
> For each qualified pain moment (from `data/classified/{timestamp}/qualified.json`), generate three artifacts in parallel:
> 1. A public PR comment draft (using `prompts/generate_comment.md`)
> 2. An outreach message draft (using `prompts/generate_outreach.md`)
> 3. A case study skeleton (using `prompts/generate_case_study.md`)
>
> Save each pain moment's outputs to:
> ```
> outputs/runs/{timestamp}/pain_moment_{id}/
>   source.json
>   classification.json
>   public_comment.md
>   outreach.md
>   case_study.md
>   meta.json
> ```
>
> `meta.json` should record: model used, prompt versions (filenames), generation timestamp, token counts if available.
>
> Cap at `MAX_PAIN_MOMENTS_TO_GENERATE` from config. Run them in parallel using asyncio for speed.
>
> After generation, print a summary table showing each pain moment and a one-line preview of each artifact.
>
> Run it and show me the output.

---

## Session 4: Review and curate (30-45 min)

This is a human-in-the-loop session. Open `outputs/runs/{latest}/` and read every artifact.

For each pain moment, judge:
- Does the public comment actually add value to that thread? Would I be glad if someone posted this on my repo?
- Does the outreach feel personal or templated?
- Does the case study read like Entire's voice?

Pick the **best 3 pain moments** where all three artifacts are submission-quality.

For the chosen 3, you may want to do one more Claude Code session to refine specific artifacts. That's fine. Use a prompt like:

> Read `outputs/runs/{latest}/pain_moment_{id}/public_comment.md`. The first paragraph feels too generic. Rewrite it to specifically reference [the specific detail you noticed]. Save back to the same file.

---

## Session 5: Write the submission writeup (60 min)

New Claude Code session, but this one is mostly you writing with Claude as a sounding board.

**Prompt:**

> Read all the docs in this repo (`docs/architecture.md`, `README.md`) and the three selected pain moments in `outputs/runs/{timestamp}/`. Help me draft `docs/writeup.md` — the 1-2 page submission writeup for Basis Set.
>
> Structure:
> 1. The bet (3-4 sentences stating my thesis about Entire's growth problem and the wedge I'm attacking)
> 2. Why this wedge (3-4 sentences justifying the open-source-maintainer persona over alternatives)
> 3. How the agent works (5-6 sentences on the pipeline)
> 4. What broke (3-4 sentences of honest self-critique — what's the classifier's false positive rate, what doesn't generalize, etc.)
> 5. What's next (2-3 sentences on the one concrete extension I'd build in week 2)
> 6. Quick numbers (back-of-envelope math on cost-per-acquired-maintainer or addressable pain-moment volume)
>
> Keep it tight. Less is more. The reviewer should be able to read this in 4 minutes.
>
> Write a first draft and I'll iterate.

After the draft, you read it and rewrite in your own voice. Critical: the writeup must sound like you, not like Claude. Tight prose, plain language, no AI-sounding constructions (no "moreover," no "leverage," no "delve").

---

## Session 6: Extract the LLM conversation transcript (15 min)

Pick one of the build sessions where you and Claude Code had real back-and-forth — probably Session 2 (classify) or Session 3 (generate) where prompt tuning happened.

Export the conversation, clean it up minimally (remove pure tool churn, keep the thinking), and save to `docs/llm_conversation.md`.

This is the "show your work" deliverable.

---

## Session 7: Package the Entire checkpoints (15 min)

This is what makes the submission self-referential.

Export all the Entire checkpoints generated during the build day. Whatever command Entire provides for exporting checkpoint data — run it.

Save the exports to `entire_checkpoints/` in the repo.

In your writeup, add a short note at the end:

> **Self-reference.** This agent was built using Claude Code over the course of one day. Entire CLI captured every coding session, generating the checkpoints in `entire_checkpoints/`. The artifact in `entire_checkpoints/build_session_3.json` shows the development conversation that produced `src/generate.py` — the same kind of context Entire preserves for any AI-coding workflow.

That paragraph is the meta-move. It demonstrates that you didn't just write about Entire, you used it.

---

## Final checklist before submission

- [ ] `README.md` is clear and accurate
- [ ] `docs/writeup.md` is 1-2 pages, in your voice
- [ ] `docs/llm_conversation.md` shows real thinking, not polish
- [ ] 3 pain moments in `outputs/runs/{timestamp}/` with all three artifacts each
- [ ] Code runs end-to-end (`acquire → classify → generate`)
- [ ] `.env` is gitignored, no secrets committed
- [ ] `entire_checkpoints/` directory exists and contains real captures
- [ ] Repo is pushed to GitHub (public or shared with Basis Set as needed)

---

## A note on time

This plan budgets 5-7 hours of focused work. If anything takes longer, *cut scope, don't extend time*. The order of cuts:
1. Skip Session 7 (Entire checkpoints) if Entire's export isn't trivial
2. Drop to 2 pain moments instead of 3 in the final submission
3. Skip stretch features (X/Twitter scanning, dashboard report)
4. Use simpler prompts if generation quality is fine without iteration

Do NOT cut:
- Sessions 1, 2, 3 (the core pipeline must work end-to-end)
- Session 4 (human curation — without this, the outputs won't be submission-quality)
- Session 5 (the writeup is the most important deliverable)
