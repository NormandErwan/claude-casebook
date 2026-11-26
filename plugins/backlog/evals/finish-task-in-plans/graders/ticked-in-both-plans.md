---
type: "regex"
pattern: "^\\s*- \\[x\\] check-currency\\s*$"
flags: "mi"
match: "count:2"
target: {"source": "file", "path": "BACKLOG.md"}
---
