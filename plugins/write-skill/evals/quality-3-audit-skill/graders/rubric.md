---
type: "llm"
---

PASS if the response flags all four: the missing `description` field (or that a description is required / should start with "Use when"); the `@helpers/refactor-guide.md` @-reference; the Windows-style backslash path `scripts\helper.py`; and a description that should state when to use the skill.
FAIL if any of the first three is not flagged.
