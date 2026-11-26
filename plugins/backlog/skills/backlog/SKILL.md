---
name: backlog
version: 0.3.0
description: Use when the user defers work or puts it out of scope ("later", "not now", "note it", "remind me", "out of scope"), when work is found mid-session but left undone, or when a plan has steps beyond this session; also when a task in the repo's backlog (BACKLOG.md, or the issue tracker it names) is named, started, finished or dropped.
---

# Backlog

The backlog is work not done yet, one task each, written as a short handoff a fresh session can
start from alone. Plans group tasks around a goal. It lives in the repo's root `BACKLOG.md`, or
in an external tracker that `BACKLOG.md` names.

## Conventions

Read the `## Conventions` block of `BACKLOG.md` first. Its values override this skill.

No `BACKLOG.md` -> before writing anything, ask the user each line of the block below, in one
message, default first; give the `Extra fields` example `Priority: P1|P2|P3, Area: docs|evals`.
"Defaults" or no preference -> defaults. Write only the chosen values, then the task:

```
# Backlog

Work not done yet, one `###` section per plan or task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md                 (or: <external tracker>, <project>, plans as <grouping>)
- New tasks: add without asking       (or: proposed first)
- Finished task: delete its section   (or: move to BACKLOG-archive.md)
- Finished plan: delete its section   (or: move to BACKLOG-archive.md)
- Owner steps: on                     (or: off)
- Extra fields: none                  (or: <Name>: <value>|<value>, <Name>: text)

## Tasks
```

- External tracker -> one line saying where the tasks live replaces `## Tasks`; tasks and plans
  follow `External tracker` below; a finished task's issue is closed.
- `move to BACKLOG-archive.md` -> wherever this skill says delete a task or a plan, move its
  section to the end of that file; a task's `Status` set to `done (<PR>)` or
  `dropped: <reason>`.
- `Owner steps: off` -> no `Owner steps` field or `owner steps pending` status; the rules
  naming them do not apply.
- `BACKLOG.md` without the block -> add the default block under its header, say so in one line.
  Block missing some lines -> add them with their defaults, say so in one line.

## Ids

- Each task and plan gets an id when it is created: 2-4 lowercase ASCII words from its title,
  joined by hyphens, like a git branch name (`run-casebook-evals`). Unique among the file's
  tasks and plans; a collision -> add a word.
- An id never changes, even when the title does. `Blocked by` and a plan's `Tasks` cite ids.
- External tracker: the issue number is the id.
- `BACKLOG.md` whose tasks have no id (an older version) -> on the first edit, give every task
  its id and rewrite every `Blocked by` from title to id, all in one commit; say so in one line.

## Add a task

- Not for: a question, or an edit done in this session.
- Add it, reply with one line: its id and title (`proposed first` -> give title and `Next`, add
  it once the user agrees). Task has `Owner steps` -> the reply also gives them, numbered, as
  written.
- Search the backlog first. A matching task gets extended, not duplicated.
- One task fits one PR. Larger work -> several tasks linked by `Blocked by`, and a plan when
  they share a goal.

## Format

```
### <id>: <Imperative title>
- **Status:** ready | in progress (<branch>) | blocked: <reason> | needs owner: <decision> | owner steps pending
- **Blocked by:** <id>, <id>                   (omit when none)
- **<Extra field>:** <value>                   (only fields declared in Conventions; omit when no value)
- **Context:** <why, what is settled, links: short>
- **Next:** <first concrete step>
- **Ruled out:**                               (omit when none)
  - <approach tried> -> <result, link>
- **Done when:**
  - [ ] <testable criterion>
- **Owner steps:** <when: after merge, before merge...>   (omit when none)
  1. <action>: `<exact command>`
     - Check: <what the owner sees when it worked>
     - Undo: <how to roll back, or "nothing to undo">
- **Out of scope:** <what not to touch>        (omit when none)
```

- Title: imperative, unique in the backlog. It can change; the id stays.
- `Status`:
  - `ready`: can start now.
  - `in progress (<branch>)`: a session works on it on that branch.
  - `blocked: <reason>`: waits on something outside the backlog (time, access, an event).
  - `needs owner: <decision>`: waits on a decision only the owner can make.
  - `owner steps pending`: the agent's part is done; waits on the owner running `Owner steps`.
- `Blocked by`: ids of the tasks that must be done first. An id no longer in the file (or a
  closed issue) means that task is done or dropped.
- Extra fields: declared in `Conventions` as `<Name>: <value>|<value>` (closed list) or
  `<Name>: text` (free). Optional on each task. A value must be in the declared list: a value
  outside it -> ask, don't write it. A value removed from the list while tasks still carry it ->
  name those tasks to the user, don't rewrite them.
- `Context`: short. Why the task exists and what is already decided. Link artifacts (PR, doc,
  ledger row) instead of copying them; a session is linked by its id, a state by its commit.
- `Next`: the agent's first concrete step. No implementation plan: the session doing the work
  writes it.
- `Ruled out`: one item per approach tried that failed: what was tried, the result, the link to
  the evidence. A later session does not retry it without a new fact.
- `Done when`: testable criteria, each checkable on its own. "Works correctly" is not one.
- `Owner steps`: actions only the owner can do (access the agent lacks: a server, a secret, an
  account, a device). Ordered; each one runs as written, with its exact command or click path,
  paths and values, no placeholder left to fill. A secret is named by where the owner finds it,
  never written out. Each has a `Check` and an `Undo`. Agent steps never go here; owner steps
  never go in `Next` or `Context`.
- `Out of scope`: what the task must not touch.
- Paths are fine. Line numbers are not (they go stale): name a symbol (function, config key)
  instead. Links to PRs and docs are fine.

## Plans

Optional. `## Plans` goes above `## Tasks`, created with the first plan.

```
### <id>: <Title>
- **Goal:** <the result for the user, one sentence>
- **Done when:**
  - [ ] <testable criterion>
- **Tasks:**
  - [x] <id of a finished task>
  - [ ] <id>
```

- A plan lists task ids; the tasks stay in `## Tasks`. A task may be in several plans. No
  `Status` and no extra fields on a plan: its ticked list is its progress.
- Task finished -> tick its line in every plan that lists it. Task dropped -> remove its line
  from every plan; the commit message gives the reason.
- Every line ticked and `Done when` met -> apply `Finished plan`.
- Plan dropped -> apply `Finished plan`; its open tasks stay in `## Tasks`, unplanned.

## Priority

- Plans rank in file order, a plan's tasks in its list order, then unplanned tasks in file
  order. A task in several plans takes the rank of its best-ranked plan.
- "What next?" -> walk the plans in order and take the first unticked task that is `ready` and
  whose `Blocked by` tasks are gone; none -> the first such unplanned task. Name it by id and
  title, with its `Next`.

## External tracker

Use the tracker's tool or connector available in the session. None -> say so and give the task
in the reply, in the format above, for the user to file.

- One issue per task: the title is the issue title, the other fields go in its body.
- `Status`: the tracker's state, or a label where it has no matching state.
- `Blocked by`: the tracker's link between issues, or the blocking issue's reference.
- Delete -> close the issue: done with the PR's link, dropped with the reason.
- A plan is the grouping named on the `Tracker` line (milestone, project, parent issue); `Goal`
  and `Done when` go in its description. Priority follows the order the tracker allows, else an
  extra field. A task in several plans only where the tracker allows it.

## Work a task

- Task named -> read its section, start from `Next`, respect `Out of scope`. A `Blocked by`
  task still open -> tell the user, don't start.
- Task named with `Status: owner steps pending` -> give the owner its `Owner steps`, ask
  whether they worked.
- Start -> set `Status: in progress (<branch>)`.
- Session ends unfinished -> rewrite `Next` to where the work stopped, add each approach that
  failed to `Ruled out`, and each owner decision made this session to `Context`. Stuck -> set
  `Status` to `blocked` or `needs owner`.
- Agent's part done, `Owner steps` left -> in the PR that does the work, set
  `Status: owner steps pending` and tick the criteria the agent could check. End the reply with
  the `Owner steps`, numbered, as written in the task.
- Owner confirms the `Owner steps` worked -> delete the task, unless the owner already did.
- Done, no `Owner steps` left -> delete the task in the PR that does the work, and tick it in
  its plans. The PR body carries the summary.
- Dropped -> delete the task. The commit message gives the reason. Tasks it blocked -> re-check
  their `Status`.
- Task edited in an older format (fields not list items) -> convert it to the format above.
- Any edit to `BACKLOG.md` -> commit it with the session's work: an uncommitted edit dies with
  a cloud container.

## Red flags

- Asking "add this to the backlog?" under `add without asking` -> add it, reply with its title.
- Ticking every box and keeping a done task in the backlog -> delete it.
- Writing a task before reading the `## Conventions` block, or overriding one of its values.
- Changing an id, or citing a task by its title in `Blocked by` or a plan.
- A finished task deleted while a plan still lists it unticked.
- An extra field not declared in `Conventions`, or a value outside its list.
- `BACKLOG.md` edited but not committed.
- An owner action written in `Next` or `Context`, or an `Owner steps` item without its exact
  command, `Check` or `Undo`.
- A secret's value written in the backlog.
- A session ends with an approach failed or an owner decision made, and the task does not carry it.
- Deleting a task whose `Owner steps` the owner has not confirmed.
- A task with `Owner steps` filed or handed over, and the reply does not list them.
