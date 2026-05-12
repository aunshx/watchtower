<p align="center">
  <img src="https://i.postimg.cc/QxPgwKb1/logo.png" alt="Watchtower logo" width="120" />
</p>

<h1 align="center">Watchtower</h1>

<p align="center">
  A GTM agent for <a href="https://entire.io">Entire</a>. Watchtower finds public AI-coding pain moments in OSS and drafts useful artifacts at the moment a developer or maintainer is articulating the problem.
</p>

<p align="center">
  <a href="https://aunshx.github.io/watchtower"><b>Live dashboard</b></a> ·
  <a href="https://www.notion.so/Watchtower-Agentic-GTM-for-Entire-io-35e1660b323b801ca273f53a29c870b2"><b>Writeup</b></a> ·
  <a href="https://www.notion.so/Prioritization-Framework-35e1660b323b80d08739c69f43231150"><b>Prioritization framework</b></a>
</p>

---

## What it does

Three Python stages plus an agentic generator at the end.

Acquire pulls candidates from GitHub across 15 high-traffic OSS repos and six pain-phrase searches. Classify scores 100 prioritized candidates through Claude Opus on a structured rubric. Generate produces three artifacts per qualified pain moment using a ReAct loop with four tools: a public PR comment, a personalized outreach DM, and a case study skeleton.

Drafts only. Nothing posted to GitHub or sent. A human at Entire reviews everything before it ships.

## The agent

The generator runs as a real ReAct loop using the Anthropic tool-use API. Four tools available to the agent:

- fetch_full_thread(url): full PR or issue conversation
- fetch_repo_context(repo): README, CONTRIBUTING.md, AI policy files
- fetch_maintainer_recent_comments(username): maintainer's recent public writing
- critique_self(draft, plan): separate Claude call as critic

Bounded at 10 tool calls per artifact and one refine cycle. Every step saved as a JSON trace.

## Results

One 30-minute:

| Stage | Output |
|---|---|
| Raw candidates | 2,774 |
| Classified | 100 |
| Qualified (score >= 6) | 5 |
| Artifacts generated | 15 |
| Total v2 cost | $2.29 |
| Fallbacks / errors | 0 / 0 |

The headline result is the rmurdough Claude Code intent-drift incident, where Entire's product addresses the exact failure mode (session context collapse, violated memory rules, mode confusion across turns).

See the live dashboard for all five qualified moments and their artifacts: https://aunshx.github.io/watchtower/

## Run it yourself

Clone the repo:

git clone https://github.com/aunshx/watchtower.git
cd watchtower

Set up the Python environment:

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Add credentials:

cp .env.example .env
# Fill in GITHUB_TOKEN (public_repo scope) and ANTHROPIC_API_KEY

Run the pipeline:

python src/acquire.py
python src/classify.py
python scripts/run_agent_generator.py --all
python scripts/build_dashboard_data.py

To run the dashboard locally:

cd web
npm install
npm run dev

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

Built in one day, May 11, 2026. The agent was built using Claude Code on a Mac, with [Entire CLI](https://entire.io) installed to capture build sessions. See [docs/build_up.md](docs/build_up.md) for the full thinking on the wedge, the design choices, and what's next.