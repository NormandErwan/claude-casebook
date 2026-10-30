---
description: "Trigger: should load write-hook"
tags: ["trigger"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 3
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

My hook script runs - I see it in the debug log - but Claude never mentions what it printed. Why?
