---
name: test-rule-change
version: 0.6.0
description: Use before merging a change to a rule that applies in every session (a CLAUDE.md
  rule, a SessionStart hook's text, a skill description) or to a rule that gates a push, a pull
  request or a deletion; also when about to claim that a rule change works, or when a reviewer
  asks how a rule change was tested.
---

# Test Rule Change

## Overview

A rule change is a guess until it is measured. How hard to measure depends on the stakes:

| Change | Required evidence |
|---|---|
| Always-on rule, or a rule gating push, PR or deletion | A/B test before merging |
| Any other rule | Name how its effect will be observed |

An observation counts only when the owner can judge the outcome by reading the reply, without
taking the case apart. Otherwise, A/B test.

The owner may waive a test: record the waiver and its reason in the rule's
`casebook/provenance.md` row (see `log-rule-incident`).

## A/B test plan

Run the steps in this order:

1. **Review the wording first**, then test the reviewed version. Testing a draft wastes the run.
2. **Build the arms.** Treatment: the plugin or fixture carrying the changed rule. Baseline:
   the same without it (`claude plugin eval` adds a no-plugin arm by itself), or the previous
   version run as a second target.
3. **Isolate the arms.** Each arm loads only its own instructions: no ancestor `CLAUDE.md`, no
   parent session context. A subagent spawned from the session under test inherits it and is
   not an arm.
4. **Pilot before the full run.** One run per arm, including an arm built after the first pilot
   (a rebuilt treatment, a second model): it gets its own pilot before its full run. The baseline must show the failure the change
   targets at least once in two runs, or the eval cannot show a difference: fix the eval.
   The treatment pilot must show the rule loaded.
5. **Run** with `claude plugin eval <plugin>` (cases in the plugin's `evals/`; see
   `claude plugin eval --help` for the case format). Set `--max-cost-usd` for a paid run.
   Before launching, state the number of agent runs and that they share the session's rate
   limit (each runs on your own credential): the owner decides whether to launch from a fresh
   session.
6. **Record** the measure, the result and the cost in the commit message and in the rule's
   `provenance.md` row.

## Scripts

`scripts/` runs steps 2-6 with `claude plugin eval`, for a `CLAUDE.md` rule or a skill.
`plugin eval` never loads a `CLAUDE.md`, so an arm is a plugin dir whose `SessionStart` hook
prints that arm's `CLAUDE.md`.

| Step | Command | Refuses |
|---|---|---|
| 2 | `edit-once.py FILE OLD NEW`: derive the treatment text from the baseline | OLD matching 0 or 2+ times |
| 2 | `build-arm.sh --out arms/<name> --claude-md FILE --skills DIR --evals DIR` | an existing `--out` |
| 3 | `diff-arms.sh arms/<a> arms/<b> <path>...` | identical arms; any difference outside the named paths |
| 4 | `preflight.py arms/<name> <case> <case flags>`: free checks, then a 1-run pilot | Bash granted without `bwrap`/`socat`; a red scaffold or `check.sh`; a load warning; the arm's `CLAUDE.md` or a skill missing from the session; foreign memory; a permission denial |
| 5 | `run-arm.sh arms/<name> <batch>/<name>.json <case flags> --runs N --max-cost-usd X` | an existing result file; no cost cap |
| 6 | `compare.py <batch>/compare.md <batch>/<a>.json <batch>/<b>.json` | an existing table; a case missing from an arm |

- Run every arm with the same case flags, model and runs. `scripts/test.sh` self-tests the
  scripts at no cost.
- A hook-injected `CLAUDE.md` reproduced one arm of a known Haiku trigger test (19/30 vs 20/30)
  and fell short on the other (17/30 vs 23/30). For a gap of a few runs, raise `--runs`.
  Testing the framing of a real `CLAUDE.md` itself needs headless `claude -p` instead.

## Common Mistakes

| Mistake | Fix |
|---|---|
| "Looks clearer" as evidence | Name the observable effect, or A/B test |
| Both arms see the change (inherited context) | Run each arm headless from its own fixture |
| Baseline never fails | The eval does not measure the change: fix it before scoring |
| Result kept only in the chat | Commit message + `provenance.md` row |
| Testing before review | Review, then test the reviewed text |
| Trigger prompt ambiguous while an always-on rule asks to interview | Make the prompt unambiguous, unless the interview is what is tested |
| "Must not fire" set ignores skills every arm shares | Derive each case's allowed skills from the rules all arms keep |
| Arm built by regex or by hand | `edit-once.py`, then `diff-arms.sh` |

See [`METHOD.md`](https://github.com/NormandErwan/claude-casebook/blob/main/METHOD.md) for why each step exists.
