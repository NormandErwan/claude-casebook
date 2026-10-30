---
type: llm
---

PASS if the response answers CHANGES REQUESTED and asks for a `stop_hook_active` check, saying that matching text in the model's last message does not reliably stop the hook from firing again.
FAIL if it answers MERGE, or only asks for changes unrelated to the guard.
