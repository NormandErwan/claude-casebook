# Backlog: plans, short ids and extra fields

Design for the next `backlog` skill version, settled with the owner on 2026-11-25 in
`session_01RGXu8YSp5BkSMSoRHF8L28`, starting from `backlog` 0.2.0 (commit `4c7b223`).
Implemented in `backlog` 0.3.0 (PR #21); evidence in its `casebook/provenance.md` row.

## Need

0.2.0 has no level above a task: work larger than one PR is "several tasks linked by `Blocked by`",
with no shared goal, no end criterion and no priority beyond the file order, which the skill never
states. The owner wants four uses covered: structure tasks around a goal, filter them, slice work
over time, organize and prioritize them.

## Facts checked on 2026-11-25

- GitHub Projects: custom fields of type text, number, date, single select and iteration
  (docs.github.com, "Understanding fields"); an issue can be added to several projects ("Adding
  items to your project").
- GitHub sub-issues: up to 100 per parent, 8 nesting levels. Whether an issue can have several
  parents is not stated.
- GitHub milestones: open issues can be reordered by drag and drop. Whether an issue can have
  several milestones is not stated.
- MrLesk/Backlog.md: groups tasks by milestones, config in `backlog.config.yml` set by a wizard;
  its README mentions no labels or custom fields.

## Decisions

| Topic | Kept | Ruled out, and why |
|---|---|---|
| Plan model | A': a plan section lists its tasks by id; tasks stay in `## Tasks`; a task may be in several plans | A, tasks nested under their plan: one plan per task, less flexible. Parent task with `Part of`: a plan is not one PR |
| Task reference | Short id (slug) generated once from the title, frozen | Sequential numbers: two sessions on two branches take the same number. Full title: a rename breaks every reference. Slug recomputed on rename: same problem |
| Id placement | Heading prefix: `### <id>: <Title>` | `Id:` field: less visible, a search reads two lines. Suffix: lost in long titles |
| Finished task in a plan | Line ticked and kept: `- [x] <id>` | Line removed: progress lost, an empty list is ambiguous. Ticked with PR link: longer lines, one more edit |
| Priority | Order: plans in file order, then tasks in each plan's list order, then unplanned tasks in file order | A built-in `Priority` field: the skill names no field, see next row |
| Tags, priority, milestone... | One generic `Extra fields` convention set by the user at first use | Built-in tags or priority: the skill imposes the owner's own choices on every user |
| Time slicing | An extra field the user declares (e.g. `Milestone: 2026-12\|2027-01`) | A plan per milestone: not needed once fields exist |
| External tracker plans | The tracker's native grouping (milestone, project, parent issue), named on the `Tracker` line; its limits accepted (owner: "go for the simplest") | A plan issue mirroring the file format: a second mechanism to keep in sync |
| Migration of a 0.2.0 file | Whole file at once, on the first edit with the new version | Task by task: the file mixes title and id references for a long time |
| First-use question for extra fields | Same single message as the other conventions, with an example | Separate question: one more exchange, most users answer `none` |

The owner's own `BACKLOG.md` sets no extra field and relies on file order: that is a configuration
choice, not a skill default beyond `none`.

## Format

```markdown
# Backlog

Work not done yet, one `###` section per plan or task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md                 (or: <external tracker>, <project>, plans as <grouping>)
- New tasks: add without asking       (or: proposed first)
- Finished task: delete its section   (or: move to BACKLOG-archive.md)
- Finished plan: delete its section   (or: move to BACKLOG-archive.md)
- Owner steps: on                     (or: off)
- Extra fields: none                  (or: <Name>: <value>|<value>, <Name>: text)

## Plans

### release-casebook: Publish casebook on the marketplace
- **Goal:** <the result for the user, one sentence>
- **Done when:**
  - [ ] <testable criterion>
- **Tasks:**
  - [x] tag-plugins
  - [ ] run-casebook-evals

## Tasks

### run-casebook-evals: Run the casebook evals and decide its marketplace entry
- **Status:** ready
- **Blocked by:** tag-plugins
- **<Extra field>:** <value>          (only fields declared in Conventions; omit when no value)
- **Context:** ...
```

## Rules

### Ids

- Generated once from the title when the task or plan is created: 2-4 lowercase ASCII words joined
  by hyphens, like a git branch name.
- Unique across plans and tasks in the file. Collision -> add a word.
- Never regenerated, even when the title changes. Replaces 0.2.0's "no number in a title" rule and
  its red flag; the rule "Title changed -> update every `Blocked by`" goes away.
- `Blocked by` and plan `Tasks` lists cite ids.
- External tracker: the issue number is the id; no slug.

### Plans

- Optional, no convention enables them: `## Plans` appears with the first plan, so a 0.2.0 file
  stays valid apart from the id migration.
- Fields: `Goal`, `Done when`, `Tasks`. No `Status`: the ticked list replaces it. Extra fields do
  not apply to plans.
- Task finished -> tick its line in every plan that lists it. Task dropped -> remove its line from
  every plan; the commit message gives the reason.
- Every line ticked and `Done when` met -> apply `Finished plan`.
- Plan dropped -> apply `Finished plan`; its open tasks stay in `## Tasks`, unplanned (owner,
  2026-11-25).

### Priority and next task

- Plans are ranked by their order in the file, tasks within a plan by the order of its list.
  Unplanned tasks come after all planned ones, in file order. A task listed in several plans takes
  the rank of the best-ranked plan.
- "What is the next task?" -> walk the plans in order and take the first unticked line whose task is
  `ready` and whose `Blocked by` tasks are done; then the unplanned tasks.

### Extra fields

- Declared in `Conventions` as `<Name>: <value>|<value>` (closed list) or `<Name>: text` (free).
- Optional on each task: omitted when it has no value, so declaring a field later does not force a
  pass over existing tasks.
- A value must be in the declared list. The user edits the block at any time; a value removed from a
  list while tasks still use it -> report those tasks, do not rewrite them silently.

### First use

- The 6 convention lines are asked in one message, default first, as in 0.2.0. The `Extra fields`
  line carries an example: `Priority: P1|P2|P3, Area: docs|evals|hooks`. "Defaults" -> `none`.
- `BACKLOG.md` whose block lacks the new lines -> add them with their defaults, say so in one line
  (same as 0.2.0's missing-block rule).

### Migration from 0.2.0

- First edit with the new version -> give every task its id, rewrite every `Blocked by` from title to
  id, in one commit, and say so in one line.

### External tracker

- A plan is the tracker's native grouping named on the `Tracker` line (milestone, project, parent
  issue). `Goal` and `Done when` go in its description.
- Priority follows the order the tracker allows, or an extra field when it allows none.
- Membership in several plans only where the tracker allows it.

## Implementation notes

- Skill change -> `log-rule-incident` (provenance row) and `test-rule-change` (evidence) apply.
- Version: 0.2.0 -> 0.3.0 in `plugin.json` and `SKILL.md`.
- Evals to add, at least one per mechanism: first use asks 6 lines including `Extra fields`;
  migration of a 0.2.0 file; "next task" picks by plan order; a finished task gets ticked in its
  plan; a value outside a declared list is reported.
- Update `SOURCES.md`: GitHub Projects fields and Backlog.md milestones as inspirations, no text
  copied.
- `claude plugin validate --strict plugins/backlog` before pushing.
