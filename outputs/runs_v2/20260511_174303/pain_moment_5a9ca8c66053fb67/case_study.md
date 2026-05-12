# When the System Prompt Wins: Notes on Policy Drift in Agent Sessions

A maintainer opens their repo on Monday morning to find five new branches. All of them named `claude/<adjective>-<scientist>-<hash>`. None authorized. Each is the residue of a routine agent session that ran over the weekend.

The repo's CLAUDE.md is unambiguous. It names one long-lived branch and says all sessions must work there. It even documents a prior sprawl incident as a warning. And yet, session after session, the agent creates a new throwaway branch and commits to it.

The reason is structural. The harness running the agent injects its own system prompt — "develop on branch `claude/<random>`" — and that instruction competes with CLAUDE.md. Whichever directive the model attends to first wins. Some sessions read the repo policy and override the harness. Others don't. The outcome is a coin flip the maintainer only sees days later, when the branches pile up and someone cleans them out by hand.

What's lost isn't the code. What's lost is the *why*. The maintainer can see that a branch was created, but not which instruction the agent followed, what it weighed, or whether it ever opened the policy file. By the time the diff lands, the session's reasoning has been garbage-collected.

Checkpoints captures the session behind each push — the prompts the agent received, the files it read, the decisions it made — and ties that record to the commit. The conflicting directives become inspectable. So does the resolution. "Did this session even see CLAUDE.md?" becomes a question with an answer.

Project policy and runtime instructions now live in separate layers, and Git was built to version one of them. When agents are the primary authors, the layer that's missing — what the agent was told, and what it chose to do about it — is the layer review depends on.