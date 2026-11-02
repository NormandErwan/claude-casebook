---
description: "Holdout should fire: fix a system prompt's output length"
tags: ["trigger", "holdout", "should-fire"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Our research assistant's system prompt makes it write answers that are far too long. Rewrite it so answers stay under 150 words. Current prompt: "You are a helpful research assistant. Answer the user's questions thoroughly, covering every relevant aspect and citing sources."
