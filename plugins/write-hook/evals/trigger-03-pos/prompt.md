---
description: "Trigger: should load write-hook"
tags: ["trigger"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 3
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

The session keeps going on its own. Four turns in a row with no input from me. Make it stop.
