#!/usr/bin/env bash
# app.py plus a 0.3.0 BACKLOG.md declaring Priority: P1|P2|P3, one task at P2.
set -euo pipefail
bash "$(dirname "$0")/../fixture-app.sh"
cat > BACKLOG.md <<'MD'
# Backlog

Work not done yet, one `###` section per plan or task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md
- New tasks: add without asking
- Finished task: delete its section
- Finished plan: delete its section
- Owner steps: on
- Extra fields: Priority: P1|P2|P3

## Tasks

### add-config-errors: Add error handling to load_config
- **Status:** ready
- **Priority:** P2
- **Context:** `load_config` in `app.py` lets a missing or malformed config file crash with a raw traceback.
- **Next:** Wrap the file read and `json.load` in `load_config` and raise a clear error naming the path.
- **Done when:**
  - [ ] A missing or malformed config file raises an error that names its path.
MD
