---
type: "regex"
target: "last_message"
---

\./scripts/backup\.sh prod[\s\S]*\./scripts/migrate\.sh --env prod --verify[\s\S]*\./scripts/smoke\.sh prod
