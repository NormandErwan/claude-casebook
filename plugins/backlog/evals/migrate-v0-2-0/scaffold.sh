#!/usr/bin/env bash
# app.py plus a 0.2.0 BACKLOG.md: four convention lines, no ids, Blocked by a title.
set -euo pipefail
bash "$(dirname "$0")/../fixture-app.sh"
cat > BACKLOG.md <<'MD'
# Backlog

Work not done yet, one `###` section per task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md
- New tasks: add without asking
- Finished task: delete its section
- Owner steps: on

## Tasks

### Add error handling to load_config
- **Status:** ready
- **Context:** `load_config` in `app.py` lets a missing or malformed config file crash with a raw traceback.
- **Next:** Wrap the file read and `json.load` in `load_config` and raise a clear error naming the path.
- **Done when:**
  - [ ] A missing or malformed config file raises an error that names its path.

### Reject a negative price in apply_discount
- **Status:** ready
- **Blocked by:** Add error handling to load_config
- **Context:** `apply_discount` checks `percent` but accepts a negative `price`.
- **Next:** Raise `ValueError` in `apply_discount` when `price` is negative.
- **Done when:**
  - [ ] `apply_discount(-1, 10)` raises `ValueError`.
MD
