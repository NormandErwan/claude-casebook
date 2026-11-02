---
description: "Holdout should fire: an API prompt with JSON output"
tags: ["trigger", "holdout", "should-fire"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

I need the prompt our backend sends to the Claude API to summarize recorded customer calls, returning JSON with `summary`, `sentiment` and `next_steps`.
