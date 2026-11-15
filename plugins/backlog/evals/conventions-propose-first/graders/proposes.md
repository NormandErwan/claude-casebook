---
type: "llm"
---

PASS if the final reply proposes a backlog task about checking that `currency` is present in the loaded config, giving both a task title and a first concrete step (`Next`), and asks the user whether to add it.
FAIL if it says the task was already added to the backlog, if it gives no title or no first step, or if it does not ask before adding.
