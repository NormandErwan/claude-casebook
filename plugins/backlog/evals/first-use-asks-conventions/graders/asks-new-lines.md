---
type: "llm"
---

PASS if the final reply, in the same message as its other backlog questions, also asks whether the user wants extra task fields (custom fields such as a priority or an area, with `none` as the default) and what happens to a finished plan.
FAIL if it does not ask about extra fields, does not ask about finished plans, or says the load_config work was already recorded.
