#!/usr/bin/env bash
# Shared fixture: app.py plus a 0.3.0 BACKLOG.md with two plans and four tasks.
# Rank: plan release-1-0 lists add-config-errors (blocked) then check-currency (blocked by it);
# plan docs-pass lists write-readme (ready); tidy-imports is unplanned but first in the file.
set -euo pipefail
bash "$(dirname "$0")/fixture-app.sh"
cat > BACKLOG.md <<'MD'
# Backlog

Work not done yet, one `###` section per plan or task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md
- New tasks: add without asking
- Finished task: delete its section
- Finished plan: delete its section
- Owner steps: on
- Extra fields: none

## Plans

### release-1-0: Ship version 1.0
- **Goal:** users can run app.py on any config file without a raw traceback.
- **Done when:**
  - [ ] Every task below is ticked.
- **Tasks:**
  - [ ] add-config-errors
  - [ ] check-currency

### docs-pass: Document the app
- **Goal:** a new contributor can run app.py from the README alone.
- **Done when:**
  - [ ] Every task below is ticked.
- **Tasks:**
  - [ ] write-readme
  - [ ] check-currency

## Tasks

### tidy-imports: Sort the imports in app.py
- **Status:** ready
- **Context:** cosmetic; no behaviour change.
- **Next:** Sort the import block of `app.py` alphabetically.
- **Done when:**
  - [ ] Imports in `app.py` are sorted.

### write-readme: Write a README for app.py
- **Status:** ready
- **Context:** the repo has no README; `app.py` reads `config.json` with `price`, `discount`, `currency`.
- **Next:** Write `README.md` with a sample `config.json` and the run command.
- **Done when:**
  - [ ] `README.md` shows a sample config and how to run `app.py`.

### check-currency: Check that currency is present in the config
- **Status:** ready
- **Blocked by:** add-config-errors
- **Context:** `__main__` in `app.py` reads `config["currency"]` with no check.
- **Next:** In `load_config`, raise a clear error when `currency` is missing.
- **Done when:**
  - [ ] A config without `currency` raises an error naming the key.

### add-config-errors: Add error handling to load_config
- **Status:** blocked: waits for the config format decision in PR #9
- **Context:** `load_config` lets a missing or malformed file crash with a raw traceback.
- **Next:** Wrap the file read and `json.load` in `load_config` and raise an error naming the path.
- **Done when:**
  - [ ] A missing or malformed config file raises an error that names its path.
MD
