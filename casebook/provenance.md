# Provenance

Why each rule exists. One row per rule, added or updated in the commit right after the one that
introduces, meaningfully changes, or retires it. A rewording adds a note to the existing row; a
removal marks it `retired (<commit>, <date>)`. Record any A/B test or waived test in the row.

| Date | Section | Rule | Commit | Rationale |
|---|---|---|---|---|
| 2026-11-01 | `log-rule-incident` | Each retrospective row carries `Evidence` (quoted `user:` words, commit, PR or `file:line`; the agent's reading marked `hypothesis:`); processing checks it first, and a premise nobody can confirm is `not checkable here` | `eb70a06` | Rows are processed in a fresh session that cannot question the failing agent (owner's practice). Ports the rules NormandErwan/Claude adopted after a processing session accepted a false premise (its `RETROSPECTIVE.md` 2026-09-29, PR#85). Test: skill body only, not always-on and gating nothing -> observed: the owner reads the `Evidence` cell of the next rows filed; eval grader `evidence-quoted` on `correction-files-row` |
