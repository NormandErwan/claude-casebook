---
name: test-rule-change
version: 0.1.0
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
4. **Pilot before the full run.** One run per arm. The baseline must show the failure the change
   targets at least once in two runs, or the eval cannot show a difference: fix the eval.
   The treatment pilot must show the rule loaded.
5. **Run** with `claude plugin eval <plugin>` (cases in the plugin's `evals/`; see
   `claude plugin eval --help` for the case format). Set `--max-cost-usd` for a paid run.
6. **Record** the measure, the result and the cost in the commit message and in the rule's
   `provenance.md` row.

## Common Mistakes

| Mistake | Fix |
|---|---|
| "Looks clearer" as evidence | Name the observable effect, or A/B test |
| Both arms see the change (inherited context) | Run each arm headless from its own fixture |
| Baseline never fails | The eval does not measure the change: fix it before scoring |
| Result kept only in the chat | Commit message + `provenance.md` row |
| Testing before review | Review, then test the reviewed text |

See [`METHOD.md`](https://github.com/NormandErwan/claude-casebook/blob/main/METHOD.md) for why each step exists.
