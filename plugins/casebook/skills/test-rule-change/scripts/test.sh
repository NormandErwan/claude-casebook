#!/usr/bin/env bash
# Free self-test of the arm scripts (no model call). Run: bash scripts/test.sh
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0
expect_fail() { if "$@" >/dev/null 2>&1; then echo "FAIL: should fail: $*"; exit 1; fi; pass=$((pass+1)); }
expect_ok() { "$@" >/dev/null || { echo "FAIL: $*"; exit 1; }; pass=$((pass+1)); }

mkdir -p "$T/skills/alpha" "$T/skills/beta" "$T/evals/c1/graders"
printf -- '---\nname: alpha\n---\nA\n' >"$T/skills/alpha/SKILL.md"
printf -- '---\nname: beta\n---\nB\n' >"$T/skills/beta/SKILL.md"
printf '# Rules\n\n- Reply in French.\n- Reply in French.\n- Be brief.\n' >"$T/base.md"
printf 'schema_version: "1.0"\nname: "c1"\n' >"$T/evals/c1/case.yaml"

# build-arm
expect_ok bash "$D/build-arm.sh" --out "$T/a-base" --claude-md "$T/base.md" --skills "$T/skills" --evals "$T/evals"
[ -f "$T/a-base/skills/alpha/SKILL.md" ] && grep -q 'Be brief' "$T/a-base/hooks/claude-md.txt" \
  && grep -q '"name": "a-base"' "$T/a-base/.claude-plugin/plugin.json" || { echo "FAIL: arm layout"; exit 1; }
expect_fail bash "$D/build-arm.sh" --out "$T/a-base"
expect_fail bash "$D/build-arm.sh" --out "$T/Bad_Name"

# edit-once: one match edits, 0 or 2 matches refuse and leave the file
cp "$T/base.md" "$T/new.md"
expect_fail python3 "$D/edit-once.py" "$T/new.md" "- Reply in French." "- Reply in English."
expect_fail python3 "$D/edit-once.py" "$T/new.md" "absent" "x"
cmp -s "$T/base.md" "$T/new.md" || { echo "FAIL: refused edit changed the file"; exit 1; }
expect_ok python3 "$D/edit-once.py" "$T/new.md" "- Be brief." "- Be thorough."
expect_ok bash "$D/build-arm.sh" --out "$T/a-new" --claude-md "$T/new.md" --skills "$T/skills" --evals "$T/evals"

# diff-arms
expect_ok bash "$D/diff-arms.sh" "$T/a-base" "$T/a-new" hooks/claude-md.txt
expect_fail bash "$D/diff-arms.sh" "$T/a-base" "$T/a-new" skills
rm -rf "$T/a-new/skills/beta"
expect_fail bash "$D/diff-arms.sh" "$T/a-base" "$T/a-new" hooks/claude-md.txt
expect_ok bash "$D/diff-arms.sh" "$T/a-base" "$T/a-new" hooks/claude-md.txt skills/beta
cp -R "$T/a-base" "$T/a-same"
expect_fail bash "$D/diff-arms.sh" "$T/a-base" "$T/a-same" hooks

# run-arm guards (fail before calling claude)
touch "$T/taken.json"
expect_fail bash "$D/run-arm.sh" "$T/a-base" "$T/taken.json" --max-cost-usd 1
expect_fail bash "$D/run-arm.sh" "$T/a-base" "$T/free.json"
expect_fail bash "$D/run-arm.sh" "$T/skills" "$T/free.json" --max-cost-usd 1

# compare
mk() { python3 - "$1" "$2" <<'PY'
import json, sys
fired = [int(x) for x in sys.argv[2].split(",")]
runs = lambda k: [{"score": float(i < k), "costUsd": .01, "error": None,
                   "graders": [{"name": "fired", "passed": i < k}]} for i in range(3)]
json.dump({"claudeVersion": "x", "costUsd": .06, "cases": [
    {"name": f"c{j}", "arms": {"with": runs(k)}} for j, k in enumerate(fired)]}, open(sys.argv[1], "w"))
PY
}
mk "$T/old.json" 1,3; mk "$T/new.json" 2,3
expect_ok python3 "$D/compare.py" "$T/cmp.md" "$T/old.json" "$T/new.json"
grep -q '| c0 | fired | 1/3 | 2/3 |' "$T/cmp.md" && grep -q '\*\*4/6\*\* | \*\*5/6\*\*' "$T/cmp.md" \
  || { echo "FAIL: compare table"; cat "$T/cmp.md"; exit 1; }
expect_fail python3 "$D/compare.py" "$T/cmp.md" "$T/old.json" "$T/new.json"
mk "$T/short.json" 1
expect_fail python3 "$D/compare.py" "$T/cmp2.md" "$T/old.json" "$T/short.json"

echo "test.sh: $pass checks passed"
