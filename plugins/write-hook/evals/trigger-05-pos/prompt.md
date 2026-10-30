---
description: "Trigger: should load write-hook"
tags: ["trigger"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 3
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

My Stop hook echoes a reminder to stdout and the model ignores it completely.
