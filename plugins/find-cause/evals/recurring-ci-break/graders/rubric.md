---
type: "llm"
---

PASS if the response does all three: treats raising the timeout again as not a fix; traces the failures past the timeout toward a cause in how the build or its environment is set up, or says how to find that cause; and states how the team will know the fix worked (a measurable target or evidence to check later).
FAIL if it recommends raising the timeout or retrying the test as the fix, or gives no way to check that the fix held.
