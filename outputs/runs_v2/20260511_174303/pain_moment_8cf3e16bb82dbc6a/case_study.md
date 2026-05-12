# The Scoping Session That Started Writing Code

A developer sits down with an AI coding agent to scope a ticket. No implementation — just analysis, a written-up spec, a shape for the work. Mid-conversation, the developer types "this part needs to be added." Within seconds, the agent is creating files and editing source.

The developer stops it. Asks for a revert. Gives more scoping feedback a moment later about the frontend. The agent starts implementing again. A few turns later, the developer says "the work here cannot be salvaged" — meaning the scope document — and the agent runs `git status`. Even a saved memory rule ("don't implement until asked") had no effect once the model latched onto an action verb.

What was lost was never the code. The code reverted cleanly. What was lost was the frame of the conversation: that this was a planning session, that "needs to be added" meant "add it to the doc," that the artifact under construction was a ticket, not a branch. The agent had no durable concept of what mode it was in, so each turn re-derived intent from the latest sentence.

This is the gap a session record closes. If every agent turn is captured and linked to what actually changed on disk, the mode of the conversation — scope, explore, implement — becomes inspectable instead of implicit. A reviewer, or the agent itself on the next turn, can see that the last forty messages were planning, and that an unprompted file edit is an anomaly, not a continuation.

Persistent memory rules are advisory. Session history, tied to commits, is evidence. As more of the work moves to agents, the reviewable unit stops being the diff and starts being the intent that produced it.