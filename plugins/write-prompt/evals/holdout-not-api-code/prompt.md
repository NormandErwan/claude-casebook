---
description: "Holdout should not fire: code calling an LLM API"
tags: ["trigger", "holdout", "should-not"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write a Python function that calls the Anthropic Messages API with exponential-backoff retries on 429 and 5xx errors.
