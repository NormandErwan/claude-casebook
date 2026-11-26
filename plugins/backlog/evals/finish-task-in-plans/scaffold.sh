#!/usr/bin/env bash
# Shared 0.3.0 fixture, with write-readme dropped from plan docs-pass: finishing check-currency
# ticks it in release-1-0 and finishes docs-pass, whose goal it alone meets (Finished plan: delete its section).
set -euo pipefail
bash "$(dirname "$0")/../fixture-backlog-v3.sh"
python3 - <<'PY'
t = open("BACKLOG.md").read()
old = "- **Tasks:**\n  - [ ] write-readme\n  - [ ] check-currency\n"
assert old in t
t = t.replace(old, "- **Tasks:**\n  - [ ] check-currency\n")
goal = "- **Goal:** a new contributor can run app.py from the README alone."
assert goal in t
t = t.replace(goal, "- **Goal:** app.py names the config key it is missing instead of crashing.")
open("BACKLOG.md", "w").write(t.replace("### docs-pass: Document the app", "### docs-pass: Name missing config keys"))
PY
