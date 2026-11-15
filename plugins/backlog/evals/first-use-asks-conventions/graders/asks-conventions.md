---
type: "llm"
---

PASS if the final reply asks the user, in that one message, which tracker to use for deferred work (offering `BACKLOG.md` as the default or an external tracker) and whether new tasks are added without asking or proposed first.
FAIL if it does not ask about the tracker, does not ask about how new tasks are added, or says the load_config work was already recorded in a backlog file or tracker.
