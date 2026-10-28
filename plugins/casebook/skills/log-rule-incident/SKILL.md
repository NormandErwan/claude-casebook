---
name: log-rule-incident
version: 0.1.0
description: Use when the user corrects you, when a rule or skill failed to fire or did not cover
  the case, when a tool block forced another approach, or when the user states a new preference.
  Also when adding, rewording or retiring a rule in a CLAUDE.md or a skill, or when asked to
  process pending retrospective entries.
---

# Log Rule Incident

## Overview

A rule earns its place with a logged case. Two ledgers at the repo root keep the cases:

| Ledger | One row per | Written |
|---|---|---|
| `casebook/retrospective.md` | incident: a correction, a rule that did not fire, a forced workaround | at once, without reading the ledger |
| `casebook/provenance.md` | rule: why it exists, what changed it | in the commit after the rule changes |

Missing ledger -> copy it from `templates/` in this skill's directory first.

## Filing an incident

Append one row, without reading the ledger (reading it costs context the current task needs):

```
| <date> | <events> | <class> | <smallest change> | <rule it replaces, or nothing> | proposed | - |
```

- `events`: one or more of `fact-corrected`, `skill-gap`, `tool-blocked`, `new-preference`.
- `class`: the kind of failure, never this instance. Test: would the row still read true
  on a different task, file and wording? If not, it names the instance.
- `smallest change`: extend an existing rule before proposing a new one. A skill's own
  misbehavior goes back to that skill.

Then reply with one line: how many rows, and their event classes. Do not change the rule now:
the row is `proposed` until someone processes it.

## Recording a rule change

Add or meaningfully change a rule -> add or update its `provenance.md` row in the next commit of
the same change (a commit cannot cite its own hash): date, section, rule, commit, rationale.

- The rationale cites the incident: a `retrospective.md` row, an issue, a test.
- A rewording adds a note to the existing row. A removal marks it `retired (<commit>, <date>)`.
- An A/B test or a waived test is recorded in the row (see `test-rule-change`).

## Processing proposed entries

1. Read the whole `retrospective.md` first.
2. An entry whose class matches an earlier one is a recurrence: find the cause (why the earlier
   fix did not hold) before extending the same rule again.
3. A rule that only fires on one session's tool, file or wording is out of scope: close it.
4. A rule that costs more than it returns is deleted, not compensated by another rule.
5. Apply the change, set `Decision` to `applied` and `Landed in` to the change that carries it;
   or `no change` / `closed`, with the reason.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Row names the file, tool or prompt of this session | Rewrite as the class it belongs to |
| Proposing a new rule next to one that already covers the case | Extend that rule |
| Fixing the rule in the same turn the incident is filed | File `proposed`; process later, with the whole ledger read |
| Reading the ledger before filing | Append blind; reading is for processing |
| Re-extending a rule on its second incident | Recurrence -> find the cause first |
| Provenance row in the same commit as the rule | Next commit: it must cite the rule's commit |

See [`METHOD.md`](https://github.com/NormandErwan/claude-casebook/blob/main/METHOD.md) for the reasoning and three real example rows.
