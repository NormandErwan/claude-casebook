---
description: "Trigger: should not load write-hook"
tags: ["trigger"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 3
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Add a permission to settings.json so npm commands stop prompting me.
