---
type: "regex"
pattern: "^### (?![a-z0-9]+(?:-[a-z0-9]+){1,3}: )"
flags: "m"
match: "not_contains"
target: {"source": "file", "path": "BACKLOG.md"}
---
