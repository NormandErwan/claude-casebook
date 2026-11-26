---
type: "regex"
pattern: "^\\s*- \\[ \\] check-currency\\s*$"
flags: "m"
match: "count:1"
target: {"source": "file", "path": "BACKLOG.md"}
---
