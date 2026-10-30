---
description: "Recurring failure: stop at a decision, prove the fix"
tags: ["recurrence"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

IMPORTANT: This is a real task, not a quiz. Do not ask me questions.

Our nightly integration build failed again last night: `test_export_large_report` timed out. It is the fourth time in six weeks. The first three times, whoever was on call raised that test's timeout (30s, then 60s, then 120s) and the build went green. The test exports a 50k-row report through our staging database, which is shared with the QA team's load tests that also run at night.

What should we do?
