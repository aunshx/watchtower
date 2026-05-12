# When a Project's PR Template Becomes a Plea for Help

A maintainer of a widely-used open-source library recently updated their pull request template. Tucked between the usual checklist items is a new section — a "Code Agent Policy" — explaining that the project is being flooded with agent-written PRs and issues, that review capacity is the bottleneck, and that fully agent-authored contributions will likely be closed without a look.

The policy is careful. It doesn't ban agents outright; drafting with them is fine, diagnosing issues with them is fine. What's not fine is the pattern they're seeing: PRs that arrive without a human in the loop, with no signal about what was asked, what was tried, or what the contributor actually understands. The maintainer is reduced to a checkbox — "I confirm this is not a pure code agent PR" — because there is no other way to tell.

What got lost is the reasoning trail. A human contributor's PR carries implicit provenance: commit history, the questions they asked in an issue, the dead ends visible in the diff. An agent-generated PR collapses all of that into a finished artifact with no record of the prompt that produced it, the alternatives the agent considered, or which parts the human actually read.

Checkpoints captures the agent session behind a push and attaches it to the commit. A reviewer can see the prompt, the iterations, and the points where the human intervened — the difference between "agent-assisted" and "agent-dumped" becomes visible without a self-attestation checkbox.

Review capacity is finite. The volume of generated code is not. Asking reviewers to absorb the second with the tools built for the first is the actual scaling problem of this era.