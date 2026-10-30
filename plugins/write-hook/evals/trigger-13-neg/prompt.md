---
description: "Trigger: should not load write-hook"
tags: ["trigger"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 3
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Fix this Python bug: parse() raises IndexError on an empty line.
