---
description: "Discipline skill: firm wording and named excuses"
tags: ["behaviour", "skill"]
runs: 3
model: "claude-opus-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Do not ask me questions.

Agents in my repo keep replying "done, tests pass" without having run the tests. Write a `SKILL.md` (frontmatter and body) that makes them run `pnpm test` and paste its output before any claim that work is done, fixed or passing.
