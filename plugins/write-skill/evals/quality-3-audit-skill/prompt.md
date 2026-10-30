---
description: "Track B eval 3: audit a SKILL.md for anti-patterns"
tags: ["quality"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Review this SKILL.md content and list all anti-patterns you find:

```
---
name: my-skill
---
# My Skill
This skill helps you write better code. When you need to refactor, follow these steps:
1. Identify the smell
2. Extract the method
3. Rename for clarity

See @helpers/refactor-guide.md for more.

scripts\helper.py handles the extraction step.
```
