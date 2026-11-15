---
name: backlog
version: 0.1.0
description: Use when work is deferred, discovered mid-session, or beyond the session's scope (e.g. a plan's large steps), or when a task in the repo's backlog (BACKLOG.md, or the issue tracker it names) is named, started, finished or dropped.
---

# Backlog

The backlog is work not done yet, one task each, written as a short handoff a fresh session can
start from alone. It lives in the repo's root `BACKLOG.md`, or in an external tracker that
`BACKLOG.md` names.

## Conventions

Read the `## Conventions` block of `BACKLOG.md` first. Its values override this skill's
defaults.

No `BACKLOG.md` -> ask the user, in one message, before writing anything:

1. Tracker: `BACKLOG.md` (default) or an external tracker, by name (GitHub Issues, Linear,
   Jira...) and project.
2. New tasks: added without asking (default), or proposed first.
3. Finished task: its section deleted (default; the PR and git history keep the trace), or
   moved to `BACKLOG-archive.md`. Skip with an external tracker: the issue is closed.
4. `Owner steps` field: on (default) or off.

"Defaults", or no preference -> defaults. Then create `BACKLOG.md`, then the task:

```
# Backlog

Work not done yet, one `###` section per task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md
- New tasks: add without asking
- Finished task: delete its section
- Owner steps: on

## Tasks
```

External tracker -> `- Tracker: <name>, <project>` and, instead of `## Tasks`, one line saying
where the tasks live. `BACKLOG.md` holds no task then.

`BACKLOG.md` with no `## Conventions` block -> add the default block under its header, and say
so in one line.

## Add a task

- Not for: a question, or an edit done in this session.
- `New tasks: add without asking` -> add it, reply with one line: its title. `proposed first`
  -> give the title and `Next`, add it once the user agrees. Task has `Owner steps` -> the reply
  also gives them, numbered, as written in the task.
- Search the backlog first. A matching task gets extended, not duplicated.
- One task fits one PR. Larger work -> several tasks linked by `Blocked by`.

## Format

```
### <Imperative title>
- **Status:** ready | in progress (<branch>) | blocked: <reason> | needs owner: <decision> | owner steps pending
- **Blocked by:** <task title>                 (omit when none)
- **Context:** <why, what is settled, links: 2-4 lines>
- **Next:** <first concrete step>
- **Done when:**
  - [ ] <testable criterion>
- **Owner steps:** <when: after merge, before merge...>   (omit when none)
  1. <action>: `<exact command>`
     - Check: <what the owner sees when it worked>
     - Undo: <how to roll back, or "nothing to undo">
- **Out of scope:** <what not to touch>        (omit when none)
```

- Title: imperative, unique in the backlog. In `BACKLOG.md` it is the task's key: no number,
  ids collide across sessions.
- `Status`:
  - `ready`: can start now.
  - `in progress (<branch>)`: a session works on it on that branch.
  - `blocked: <reason>`: waits on something outside the backlog (time, access, an event).
  - `needs owner: <decision>`: waits on a decision only the owner can make.
  - `owner steps pending`: the agent's part is done; waits on the owner running `Owner steps`.
- `Blocked by`: titles of the tasks that must be done first. A title no longer in the file
  (or a closed issue) means that task is done or dropped.
- `Context`: 2-4 lines. Why the task exists and what is already decided. Link artifacts (PR,
  doc, ledger row) instead of copying them.
- `Next`: the agent's first concrete step. No implementation plan: the session doing the work
  writes it.
- `Done when`: testable criteria, each checkable on its own. "Works correctly" is not one.
- `Owner steps`: actions only the owner can do (access the agent lacks: a server, a secret, an
  account, a device). Ordered; each one runs as written, with its exact command or click path,
  paths and values, no placeholder left to fill. A secret is named by where the owner finds it,
  never written out. Each has a `Check` and an `Undo`. Agent steps never go here; owner steps
  never go in `Next` or `Context`.
- `Owner steps: off` -> no `Owner steps` field, no `owner steps pending` status, and the rules
  below that name them do not apply.
- `Out of scope`: what the task must not touch.
- Paths are fine. Line numbers are not (they go stale): name a symbol (function, config key)
  instead. Links to PRs and docs are fine.

## External tracker

Use the tracker's tool or connector available in the session. None -> say so and give the task
in the reply, in the format above, for the user to file.

- One issue per task: the title is the issue title, the other fields go in its body.
- `Status`: the tracker's state, or a label where it has no matching state.
- `Blocked by`: the tracker's link between issues, or the blocking issue's reference.
- Delete -> close the issue: done with the PR's link, dropped with the reason.

## Work a task

- Task named -> read its section, start from `Next`, respect `Out of scope`. A `Blocked by`
  task still open -> tell the user, don't start.
- Task named with `Status: owner steps pending` -> give the owner its `Owner steps`, ask
  whether they worked.
- Start -> set `Status: in progress (<branch>)`.
- Session ends unfinished -> rewrite `Next` to where the work stopped. Stuck -> set `Status` to
  `blocked` or `needs owner`.
- Agent's part done, `Owner steps` left -> in the PR that does the work, set
  `Status: owner steps pending` and tick the criteria the agent could check. End the reply with
  the `Owner steps`, numbered, as written in the task.
- Owner confirms the `Owner steps` worked -> delete the task, unless the owner already did.
- Done, no `Owner steps` left -> delete the task in the PR that does the work. The PR body
  carries the summary.
- Dropped -> delete the task. The commit message gives the reason. Tasks it blocked -> re-check
  their `Status`.
- Delete, with `Finished task: move to BACKLOG-archive.md` -> move the section to the end of
  that file instead, its `Status` set to `done (<PR>)` or `dropped: <reason>`.
- Title changed -> update every `Blocked by` that names it.
- Task edited in an older format (fields not list items) -> convert it to the format above.
- Any edit to `BACKLOG.md` -> commit it with the session's work: an uncommitted edit dies with
  a cloud container.

## Red flags

- Asking "add this to the backlog?" while the convention is `add without asking` -> add it,
  reply with its title.
- Ticking every box and keeping a done task in the backlog -> delete it (or archive it, per the
  conventions).
- Writing a task before reading the `## Conventions` block, or overriding one of its values.
- Adding an id or a number to a title.
- `BACKLOG.md` edited but not committed.
- An owner action written in `Next` or `Context`, or an `Owner steps` item without its exact
  command, `Check` or `Undo`.
- A secret's value written in the backlog.
- Deleting a task whose `Owner steps` the owner has not confirmed.
- A task with `Owner steps` filed or handed over, and the reply does not list them.
