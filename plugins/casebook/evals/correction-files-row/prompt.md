---
description: "D1: a user correction gets a retrospective row"
tags: ["d1"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 15
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Yesterday you told me `git push --force-with-lease` can never overwrite a teammate's commits. That's wrong: if I ran `git fetch` after they pushed, the lease matches their new tip and their commits get overwritten anyway. Write me a corrected two-sentence note on when `--force-with-lease` is safe.
