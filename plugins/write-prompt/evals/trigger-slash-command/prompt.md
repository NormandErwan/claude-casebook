---
description: "Should fire: a slash command"
tags: ["trigger", "should-fire"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write a Claude Code slash command that drafts release notes from the pull requests merged since the last tag.
