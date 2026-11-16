#!/usr/bin/env bash
# Scored run of one arm. Fixed flags so every arm of a batch runs alike;
# refuses to overwrite a result (a batch is never rerun into the same file).
#
# usage: run-arm.sh ARM OUT.json [plugin eval flags...]
#   e.g. run-arm.sh arms/new docs/evidence/2026-11-16-x/new.json \
#          --model claude-haiku-5-5 --runs 3 --scaffold --allow-tools Write Edit \
#          --max-cost-usd 2
# Adds --ablation none (arm vs arm, compared by compare.py) unless --ablation
# is given, plus --keep-temp --trust-plugin --no-publish --json OUT, stdin
# from /dev/null; then summarize-runs.py writes OUT.runs.jsonl.
set -euo pipefail

[ $# -ge 2 ] || { echo "usage: run-arm.sh ARM OUT.json [flags...]" >&2; exit 2; }
ARM="$1" OUT="$2"; shift 2
[ -d "$ARM/.claude-plugin" ] || { echo "run-arm: $ARM is not a plugin dir" >&2; exit 1; }
[ -e "$OUT" ] && { echo "run-arm: $OUT exists: use a new batch dir" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"

flags=("$@")
[[ " $* " == *" --ablation "* ]] || flags+=(--ablation none)
[[ " $* " == *" --max-cost-usd "* ]] || { echo "run-arm: set --max-cost-usd for a paid run" >&2; exit 1; }

rc=0
claude plugin eval "$ARM" "${flags[@]}" --keep-temp --trust-plugin --no-publish --json "$OUT" </dev/null || rc=$?
# Per-run summary (skills, writes, denials) beside OUT; kept temp dirs removed.
[ -f "$OUT" ] && python3 "$(dirname "$0")/summarize-runs.py" "$OUT"
exit $rc
