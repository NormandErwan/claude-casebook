---
description: "Should not fire: fixing code"
tags: ["trigger", "should-not"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

This Python function should return the last day of a month but crashes in December. Fix it.

```python
import datetime
def last_day(year, month):
    return datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
```
