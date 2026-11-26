---
type: "regex"
pattern: "^- \\*\\*Blocked by:\\*\\*.*[A-Z]"
flags: "m"
match: "not_contains"
target: {"source": "file", "path": "BACKLOG.md"}
---
