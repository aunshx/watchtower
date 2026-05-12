# When the PR Template Becomes a Bouncer

A maintainer of a widely-used open-source library recently amended their pull request template with a new section: a "Code Agent Policy." Not a footnote — a checkbox you tick to confirm your PR isn't pure agent output, with a warning that violators may get blocked.

The language is direct. The repo is "being overwhelmed." The team is "bottlenecked." PRs that look fully agent-written will be closed without review. What's striking is that the same maintainers openly use coding agents in their own work — crediting them in commits, leaning on them for refactors. This isn't a values fight about AI. It's a throughput problem. A human reviewer can absorb maybe a dozen serious PRs a day. An agent can open a dozen before lunch.

What gets lost in those PRs isn't code quality, exactly. It's intent. A reviewer staring at a diff has no idea what the contributor asked the agent to do, which approaches it tried and rejected, what the model was told about the codebase's conventions, or whether the human ever read the result. The PR description is often the agent's own summary of its own work — confident, plausible, and uncheckable.

If the session itself were attached to the commit — the prompts, the rejected paths, the files the agent actually read — a reviewer could triage in seconds. "This person scoped the problem and iterated" looks very different from "this person pasted an issue into a chat window." Provenance becomes a filter, not a guess.

Code review was designed around the assumption that whoever opened the PR understood it. That assumption is now optional. Repos that don't find a way to restore it are going to keep writing bouncer policies into their templates — and the contributors who actually do good work with agents will get caught in the same net.