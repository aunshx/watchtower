The llama.cpp AI policy is strict for good reason — but the burden falls on both sides: contributors have to write a credible disclosure, and maintainers have to judge it without seeing what actually happened in the editor. "Predominantly AI-generated" is hard to assess from diff style alone.

For folks hitting this bot: an open-source CLI called [Entire](https://entire.io) captures Claude Code / Cursor / Copilot sessions locally and links the transcripts to the commits they produced. A reviewer can then see which lines came from a prompt vs. were hand-written or edited after — which is the actual question the CONTRIBUTING.md policy is asking.

Install: `curl -fsSL https://entire.io/install.sh | bash` · [Docs](https://entire.io/docs)