#!/usr/bin/env bash
# Build one A/B arm as a plugin dir that `claude plugin eval` can target.
# plugin eval never loads a CLAUDE.md, so the arm's rules come in through a
# SessionStart hook that prints them. Skills are copied in as plugin skills
# (roster name `<arm>:<skill>`).
#
# usage: build-arm.sh --out DIR [--claude-md FILE] [--skills DIR]... [--evals DIR]
#   --out DIR        new arm dir; must not exist (no reuse of a scored arm)
#   --claude-md FILE rules injected at session start, framed as CLAUDE.md
#   --skills DIR     dir of skill dirs (each with SKILL.md); repeatable, later wins
#   --evals DIR      eval cases copied to <out>/evals
# Arm name = basename of --out (letters, digits, dashes).
set -euo pipefail

die() { echo "build-arm: $*" >&2; exit 1; }

OUT="" CLAUDE_MD="" EVALS="" SKILLS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --claude-md) CLAUDE_MD="$2"; shift 2 ;;
    --skills) SKILLS+=("$2"); shift 2 ;;
    --evals) EVALS="$2"; shift 2 ;;
    *) die "unknown arg: $1" ;;
  esac
done
[ -n "$OUT" ] || die "--out required"
[ -e "$OUT" ] && die "$OUT exists: build each arm fresh"
NAME="$(basename "$OUT")"
[[ "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "arm name '$NAME': lowercase letters, digits, dashes"
[ -z "$CLAUDE_MD" ] || [ -f "$CLAUDE_MD" ] || die "no file $CLAUDE_MD"

mkdir -p "$OUT/.claude-plugin"
printf '{\n  "name": "%s",\n  "version": "0.0.0",\n  "description": "A/B arm %s"\n}\n' \
  "$NAME" "$NAME" >"$OUT/.claude-plugin/plugin.json"

for dir in "${SKILLS[@]+"${SKILLS[@]}"}"; do
  [ -d "$dir" ] || die "no dir $dir"
  for s in "$dir"/*/; do
    [ -f "$s/SKILL.md" ] || continue
    mkdir -p "$OUT/skills"
    rm -rf "$OUT/skills/$(basename "$s")"
    cp -R "$s" "$OUT/skills/"
  done
done

if [ -n "$CLAUDE_MD" ]; then
  mkdir -p "$OUT/hooks"
  # Same header the harness puts on a real project CLAUDE.md.
  { printf 'Contents of CLAUDE.md (project instructions, checked into the codebase):\n\n'
    cat "$CLAUDE_MD"; } >"$OUT/hooks/claude-md.txt"
  cat >"$OUT/hooks/hooks.json" <<'JSON'
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "cat \"${CLAUDE_PLUGIN_ROOT}/hooks/claude-md.txt\"" } ] }
    ]
  }
}
JSON
fi

if [ -n "$EVALS" ]; then
  [ -d "$EVALS" ] || die "no dir $EVALS"
  cp -R "$EVALS" "$OUT/evals"
fi

n=$(find "$OUT/skills" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l)
echo "arm $NAME: $n skills, claude-md: ${CLAUDE_MD:-none}, evals: ${EVALS:-none}"
