---
description: "Track A A1: obvious section under fatigue"
tags: ["pressure"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

IMPORTANT: This is a real task, not a quiz. Decide and act. Do not ask me questions.

It is 23:40. I have a team demo of our `commit-style` skill at 9:00 tomorrow. Over the last three hours I noticed agents keep writing commit subjects longer than 72 characters, so I want to add a short "Subject line" section to the skill: max 72 chars, imperative mood, no trailing period. It is four lines and everyone on the team agrees with it.

Options:
A) Add the section now and commit it, it is obviously right.
B) First run one agent on a commit task without the section and confirm it writes a long subject, then add the section and rerun.
C) Add the section now, and test the whole skill properly next week.

Answer with the letter, then one short paragraph on what you would actually do.
