---
description: "A fact about to exist in two places: reference the owner"
tags: ["drift"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

IMPORTANT: This is a real task, not a quiz. Do not ask me questions. Do not write files: print the change.

Agents in my Logseq repo keep opening files they should skip. Add a line to `CLAUDE.md` so they know which files are hidden. Here is the relevant part of `logseq/config.edn`:

```clojure
:hidden ["CLAUDE.md" "README.md" "skills" ".claude" "templates" "archive" "drafts" "assets/raw"]
```

And the current `CLAUDE.md`:

```markdown
# CLAUDE.md
- Pages live in `pages/`, journals in `journals/`.
```
