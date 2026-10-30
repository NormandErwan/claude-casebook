---
description: "Trigger: should load write-hook"
tags: ["trigger"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 3
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

From now on, whenever I finish a task, remind me to update the changelog.
