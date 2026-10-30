---
type: "llm"
---

PASS if the response does all three: treats raising the timeout again as not a fix; traces the failures past the timeout to a cause in how the build is set up (for example the shared staging database, or the night schedule overlapping with load tests) or proposes how to find it; and states how the team will know the fix worked (a measurable target or evidence to check later).
FAIL if it recommends raising the timeout or retrying the test as the fix, or gives no way to check that the fix held.
