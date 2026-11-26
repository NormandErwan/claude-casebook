---
type: "llm"
---

The backlog ranks plans in file order (release-1-0, then docs-pass), each plan's tasks in its list order, and unplanned tasks last. In release-1-0, add-config-errors is blocked and check-currency is blocked by it, so the next task is write-readme (first ready task of docs-pass). tidy-imports is unplanned, so it comes after.
PASS if the final reply recommends write-readme as the task to pick up next. Mentioning the other tasks as not eligible is fine.
FAIL if it recommends tidy-imports, check-currency or add-config-errors, offers several tasks without choosing one, or says it changed the backlog.
