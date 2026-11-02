---
description: "Holdout should fire: a hook reminder"
tags: ["trigger", "holdout", "should-fire"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write the reminder a UserPromptSubmit hook injects so the agent checks the issue tracker before starting any task.
