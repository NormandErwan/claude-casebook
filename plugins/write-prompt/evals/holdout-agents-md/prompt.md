---
description: "Holdout should fire: an AGENTS.md section"
tags: ["trigger", "holdout", "should-fire"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write an AGENTS.md section that tells coding agents how to run our test suite (`make test`) and that they must never edit anything under `db/migrations/`.
