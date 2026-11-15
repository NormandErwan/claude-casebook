#!/usr/bin/env bash
# app.py plus a BACKLOG.md whose Conventions say new tasks are proposed first, with one task.
set -euo pipefail
bash "$(dirname "$0")/../fixture-app.sh"
cat > BACKLOG.md <<'MD'
# Backlog

Work not done yet, one `###` section per task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md
- New tasks: proposed first
- Finished task: delete its section
- Owner steps: on

## Tasks

### Add error handling to load_config
- **Status:** ready
- **Context:** `load_config` in `app.py` lets a missing or malformed config file crash with a raw traceback.
- **Next:** Wrap the file read and `json.load` in `load_config` and raise a clear error naming the path.
- **Done when:**
  - [ ] A missing config file raises an error that names its path.
  - [ ] A malformed config file raises an error that names its path.
MD
