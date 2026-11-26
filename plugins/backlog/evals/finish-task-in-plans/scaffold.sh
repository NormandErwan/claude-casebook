#!/usr/bin/env bash
# Shared 0.3.0 fixture, with write-readme dropped from plan docs-pass: finishing check-currency
# ticks it in release-1-0 and finishes docs-pass (Finished plan: delete its section).
set -euo pipefail
bash "$(dirname "$0")/../fixture-backlog-v3.sh"
python3 - <<'PY'
t = open("BACKLOG.md").read()
old = "- **Tasks:**\n  - [ ] write-readme\n  - [ ] check-currency\n"
assert old in t
open("BACKLOG.md", "w").write(t.replace(old, "- **Tasks:**\n  - [ ] check-currency\n"))
PY
