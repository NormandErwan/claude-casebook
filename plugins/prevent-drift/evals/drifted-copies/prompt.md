---
description: "Copies that already drifted: flag them, the executable wins"
tags: ["drift"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

IMPORTANT: This is a real task, not a quiz. Do not ask me questions. Do not write files: print the change.

Update the "Run locally" section of our README: the dev server now listens on port 5173 instead of 3000.

README.md, "Run locally":

```markdown
## Run locally
Requires Node 18. Run `npm install`, then `npm run dev` and open http://localhost:3000.
```

`.nvmrc`:

```
20
```

`package.json` excerpt:

```json
"engines": { "node": ">=20" },
"scripts": { "dev": "vite --port 5173" }
```
