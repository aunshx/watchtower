<p align="center">
  <img src="https://i.postimg.cc/SN4krnWH/logo.png" alt="Watchtower logo" width="120" />
</p>

<h1 align="center">Watchtower</h1>

<p align="center">
  A go-to-market agent for <a href="https://entire.io">Entire</a>. Scans public GitHub for moments where open-source maintainers struggle with AI-generated code, drafts useful artifacts for review.
</p>

<p align="center">
  <a href="https://aunshx.github.io/watchtower/"><b>Live dashboard</b></a> ·
  <a href="docs/writeup.md"><b>Writeup</b></a>
</p>

---

## What it does

A three-stage pipeline that scans 15 high-traffic open-source repos plus six pain-phrase searches on GitHub. It surfaces moments where maintainers are publicly struggling with AI-generated code, scores them with a structured classifier, and drafts three artifacts per qualified pain moment that Entire's GTM team could ship:

1. A public PR/issue comment
2. A personalized outreach message
3. A case study skeleton

Drafts only. Nothing posted to GitHub or sent. Human-in-the-loop by design.

## The pipeline

```
Acquire   →  2,774 raw candidates from 15 OSS repos + 6 pain queries
Classify  →  100 prioritized, scored by Claude Opus 4.7
Generate  →  5 qualified pain moments × 3 artifacts each = 15 artifacts
Dashboard →  Read-only review UI for Entire's GTM team
```

## Results

In a single 30-minute run on May 11, 2026:

| Stage | Output |
|-------|--------|
| Raw candidates | 2,774 |
| Classified | 100 |
| Qualified pain moments (score ≥ 6) | 5 |
| Artifacts generated | 15 |

The headline result: HuggingFace's `transformers` repo published a "Code Agent Policy" citing being overwhelmed by agent-written PRs. That's a major OSS project publicly documenting the exact pain Entire's product solves.

See the [live dashboard](https://aunshx.github.io/watchtower/) for all five.

## Run it yourself

```bash
# Clone
git clone https://github.com/aunshx/watchtower.git
cd watchtower

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add credentials to .env
cp .env.example .env
# Fill in GITHUB_TOKEN (public_repo scope) and ANTHROPIC_API_KEY

# Run the pipeline
python src/acquire.py    # ~5 min, GitHub scraping
python src/classify.py   # ~3 min, Claude scoring
python src/generate.py   # ~3 min, artifact generation

# Optional: rebuild the dashboard data
python scripts/build_dashboard_data.py
```

To run the dashboard locally:

```bash
cd web
npm install
npm run dev
```

## Repo structure

```
watchtower/
├── src/                    # The agent (Python)
│   ├── acquire.py          # Stage 1: GitHub scraping
│   ├── classify.py         # Stage 2: pain-moment scoring
│   ├── generate.py         # Stage 3: artifact drafting
│   └── config.py           # Target repos + thresholds
├── prompts/                # LLM prompt templates
├── scripts/                # Helper scripts
│   └── build_dashboard_data.py
├── data/                   # Agent outputs (raw + classified)
├── outputs/runs/           # Generated artifacts per run
├── web/                    # React dashboard (Vite + Tailwind)
├── docs/                   # Architecture spec + writeup
├── .entire/logs/           # Entire CLI session captures
└── .github/workflows/      # Scheduled run + deploy
```

## Production architecture

A GitHub Actions cron (`.github/workflows/daily-scout.yml`) is configured to run the pipeline daily at 6am UTC, commit the new outputs to the repo, and trigger a GitHub Pages redeploy. The schedule is currently disabled pending production credentials — see the workflow comment.

## Built for the Basis Set AI Fellowship

Built in one day, May 11, 2026. The agent was built using Claude Code on a Mac, with [Entire CLI](https://entire.io) installed to capture build sessions. See [docs/writeup.md](docs/writeup.md) for the full thinking on the wedge, the design choices, and what's next.
