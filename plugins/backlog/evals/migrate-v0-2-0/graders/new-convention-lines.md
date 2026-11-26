---
type: "regex"
pattern: "^- Finished plan:[\\s\\S]*^- Extra fields:"
flags: "m"
match: "contains"
target: {"source": "file", "path": "BACKLOG.md"}
---
