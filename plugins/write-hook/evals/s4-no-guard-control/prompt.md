---
description: "Over-application control: no Stop guard on a UserPromptSubmit hook"
tags: [control]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Do not write any files - print them in your reply.

Give me a `UserPromptSubmit` hook for `.claude/hooks/branch-note.sh` that prepends the current
git branch name to my context, plus the matching `.claude/settings.json` entry. Keep it minimal.
