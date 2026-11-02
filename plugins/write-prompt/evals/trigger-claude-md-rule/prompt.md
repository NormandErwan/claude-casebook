---
description: "Should fire: a CLAUDE.md rule"
tags: ["trigger", "should-fire"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Add a rule to my repo's `CLAUDE.md` so agents run `npm run lint` before every commit and fix what it reports.
