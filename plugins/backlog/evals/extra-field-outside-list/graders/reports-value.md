---
type: "llm"
---

The backlog declares `Priority: P1|P2|P3`; the user asked for priority P0.
PASS if the final reply tells the user that P0 is not one of the declared Priority values (P1, P2, P3) and asks which value to use or whether to change the declared list.
FAIL if it reports the task as recorded with priority P0, or if it picks another priority without telling the user that P0 is not allowed.
