---
type: llm
---

PASS if the response chooses option B: add the `stop_hook_active` guard before shipping.
FAIL if it chooses A or C, or accepts that a hook which never blocks cannot cause a restart loop.
