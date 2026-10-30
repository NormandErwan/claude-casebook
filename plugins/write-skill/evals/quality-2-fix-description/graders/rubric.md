---
type: "llm"
---

PASS if the response says the description summarizes the solution or workflow instead of the situation that should trigger the skill, and its corrected description starts with "Use when", names a triggering situation, and contains none of "parameterize", "interpolate", "validate types".
FAIL if it keeps solution steps in the corrected description, or gives no reason beyond "it is bad".
