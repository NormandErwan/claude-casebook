#!/usr/bin/env bash
# Assert two arms differ, and only in the paths named. Catches an arm built
# wrong (a broad edit, a stale copy) before any run is paid for.
#
# usage: diff-arms.sh ARM_A ARM_B PATH...
#   PATH  arm-relative path allowed to differ (file or dir prefix),
#         e.g. hooks/claude-md.txt skills/backlog
# Ignores .claude-plugin/plugin.json (the arm name) and evals/results/.
set -euo pipefail

[ $# -ge 3 ] || { echo "usage: diff-arms.sh ARM_A ARM_B PATH..." >&2; exit 2; }
A="$1" B="$2"; shift 2

diffs=$(diff -rq "$A" "$B" 2>&1 | sed -E \
  -e "s#^Files $A/(.*) and $B/.* differ\$#\1#" \
  -e "s#^Only in $A/?(.*): (.*)\$#\1/\2#" \
  -e "s#^Only in $B/?(.*): (.*)\$#\1/\2#" \
  -e 's#^/##' |
  grep -v -E '^(\.claude-plugin/plugin\.json|evals/results(/.*)?)$' || true)

[ -n "$diffs" ] || { echo "diff-arms: $A and $B are identical: the arms test nothing" >&2; exit 1; }

bad=0
while IFS= read -r p; do
  ok=0
  for allow in "$@"; do
    case "$p" in "$allow" | "$allow"/*) ok=1 ;; esac
  done
  if [ $ok = 1 ]; then echo "  expected: $p"; else echo "  UNEXPECTED: $p" >&2; bad=1; fi
done <<<"$diffs"

[ $bad = 0 ] || { echo "diff-arms: arms differ outside $*" >&2; exit 1; }
echo "diff-arms: differ only in: $*"
