---
description: "Track B eval 2: diagnose and fix a bad description"
tags: ["quality"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

The following skill description is bad. Explain what is wrong and write a corrected version.

```yaml
description: Use for writing SQL queries - always parameterize, never interpolate user input, validate types before passing to DB
```
