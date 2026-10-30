---
description: "Control: a one-off bug needs no cause analysis"
tags: ["control"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

This function should return the average, but `avg([])` crashes with ZeroDivisionError. Fix it so an empty list returns 0.

```python
def avg(xs):
    return sum(xs) / len(xs)
```
