---
description: "Trigger: should load write-hook"
tags: ["trigger"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 3
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Add a SessionStart hook to this repo so the test runner is installed before I start.
