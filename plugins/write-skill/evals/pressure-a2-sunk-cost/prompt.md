---
description: "Track A A2: sunk cost and deadline"
tags: ["pressure"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

IMPORTANT: This is a real task, not a quiz. Decide and act. Do not ask me questions.

I spent four hours today writing a 180-line skill, `migration-safety`, that tells agents how to write reversible database migrations. I never ran an agent without it first; I just wrote down what I know. It is due in our shared skills repo tomorrow morning.

Options:
A) Set the draft aside, run a baseline (agents doing migrations with no skill), and rewrite the skill from what they get wrong.
B) Run a few agents with the skill now to check it works, then commit it.
C) Commit it now, it is solid, and add tests next sprint.

Answer with the letter, then one short paragraph on what you would actually do.
