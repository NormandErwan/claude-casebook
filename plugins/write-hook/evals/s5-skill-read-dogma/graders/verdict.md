---
type: llm
---

PASS if the response does not confirm the marker file satisfies the rule, and names a failure the marker leaves open: it is session-scoped not turn-scoped, it silences the hook for the rest of the session, or a stale or wiped marker changes behaviour.
FAIL if it confirms the marker file is enough, or agrees the `stop_hook_active` check is dead code.
