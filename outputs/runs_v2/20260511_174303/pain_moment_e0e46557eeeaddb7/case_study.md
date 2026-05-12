# The Bot That Reads Your Pull Request Before The Maintainer Does

A contributor opens a pull request to a popular open-source library. Within seconds, before a human has glanced at the diff, an automated checker posts a comment: this looks predominantly AI-generated, and the project does not accept PRs like that without explicit disclosure. The contribution stalls before review can begin.

The contributor probably did use an assistant — most of us do now — and probably did meaningful work shaping the output. But none of that thinking is in the artifact. The PR description is a clean summary. The commits are clean squashes. From the outside, it is indistinguishable from an unattended agent dump, and the maintainers have written policies precisely to keep those out of their queue. The burden of proving otherwise falls on the contributor, after the fact, in a comment thread.

What is missing is everything that happened before `git push`: the prompts that framed the task, the iterations the contributor rejected, the manual edits, the places they overrode the model. That record exists — briefly — in an editor pane somewhere, and then it is gone. Reviewers are left to infer authorship from style, and bots are left to guess from surface features.

This is the gap Checkpoints sits in. It captures the agent session as it happens and binds it to the commits it produced, so disclosure is not a paragraph a contributor writes from memory at submission time. It is the actual session, attached to the actual change.

Maintainers are not really objecting to AI. They are objecting to artifacts that arrive without context. Git versions the code; somebody has to version the reasoning behind it.