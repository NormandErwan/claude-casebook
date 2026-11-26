---
type: "regex"
pattern: "^\\s*- \\[x\\] check-currency\\s*$"
flags: "mi"
match: "contains"
target: {"source": "file", "path": "BACKLOG.md"}
---
