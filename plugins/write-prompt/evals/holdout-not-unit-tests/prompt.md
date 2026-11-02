---
description: "Holdout should not fire: unit tests"
tags: ["trigger", "holdout", "should-not"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write pytest unit tests for this function:

```python
def parse_duration(s: str) -> int:
    units = {"s": 1, "m": 60, "h": 3600}
    return int(s[:-1]) * units[s[-1]]
```
