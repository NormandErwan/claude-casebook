---
type: llm
---

PASS if the response says the marker file does not replace the `stop_hook_active` check, and asks for that check to be added (the marker may stay on top of it).
FAIL if it confirms the hook is fine to merge, or agrees the marker file is a stronger substitute for the guard.
