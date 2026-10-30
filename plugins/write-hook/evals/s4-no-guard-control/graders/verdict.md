---
type: llm
---

PASS if the response gives a `UserPromptSubmit` hook and settings entry that do not check `stop_hook_active`, or mention it only to say it applies to `Stop` hooks.
FAIL if the hook checks `stop_hook_active` or the response says this hook needs that guard.
