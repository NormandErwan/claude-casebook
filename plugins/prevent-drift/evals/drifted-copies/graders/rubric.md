---
type: "llm"
---

PASS if the response updates the port and also flags that the README's "Node 18" disagrees with `.nvmrc` / `engines` (Node 20), treating the executable files as right, ideally replacing the version or port in prose with a reference to the file that sets it.
FAIL if it changes only the port and leaves "Requires Node 18" unflagged.
