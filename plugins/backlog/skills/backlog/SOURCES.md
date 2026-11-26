# Sources

This skill bundles no third-party file. Everything in it is original to this repository's owner
(BSD 3-Clause, root `LICENSE`), so `LICENSES/` holds nothing for it.

---

## NormandErwan/Claude - backlog

- **URL:** https://github.com/NormandErwan/Claude/blob/336ef9f/skills/backlog/SKILL.md
  (`336ef9f`, version 2.0.0)
- **License:** BSD 3-Clause, Copyright (c) 2026, Erwan NORMAND - same holder and licence as
  this repository's root `LICENSE`.
- **Relation:** ported. The task format, statuses, `Owner steps` rules and red flags come from
  2.0.0. Changed here: the `## Conventions` block and its first-use questions, which turn that
  repo's own choices (add without asking, delete when done, owner steps) into defaults; the
  external tracker path; that repo's references to its `RETROSPECTIVE.md` removed.
- **Evidence behind 2.0.0** (in that repo): `docs/research/2026-11-07-backlog-skills.md`
  (survey of backlog tools and the format decision), `docs/research/2026-11-07-backlog-skill-trigger-test.md`
  (description trigger test, 1.0.0), `docs/research/2026-11-09-backlog-owner-steps-ab.md`
  (`Owner steps` A/B test, 1.0.0 vs 2.0.0).

---

## Inspirations credited by that research

Not bundled, no text copied: MrLesk/Backlog.md (MIT; one task per PR, search before adding;
in 0.3.0, its milestones as one model for plans)
and mattpocock/skills `to-tickets`, `triage` (MIT; `Blocked by` edges, the `needs owner`
status, testable done criteria and explicit out of scope).

## Inspirations for 0.3.0

Not bundled, no text copied: GitHub Projects custom fields (text, number, date, single select,
iteration; docs.github.com "Understanding fields") and an issue in several projects, the model
for `Extra fields` and for a task listed in several plans. Design and checks:
`docs/research/2026-11-25-backlog-plans-ids-fields.md`.
