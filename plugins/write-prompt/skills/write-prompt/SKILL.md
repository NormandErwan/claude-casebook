---
version: 2.1.0
name: write-prompt
description: Use when writing or editing text an AI model will follow as instructions: a CLAUDE.md or AGENTS.md rule, a SKILL.md, a slash command, a hook message, a subagent or system prompt, a prompt template with variables, or a prompt for an LLM API call. Also when such a prompt gives inconsistent or wrong results. Load it before drafting, even for a one-line rule.
---

# Write Prompt

Covers what Claude skips without this skill. Everything else about prompt writing, Claude
already does: do not pad a prompt with it.

## Prompts run in production (LLM API, templates)

A prompt that processes inputs nobody reviews one by one needs all three:

- **A worked example.** At least one input with its exact expected output. Pick it from the
  hard cases (messy, multilingual, several items), never a clean one: "Show, Don't Tell:
  Examples are more effective than descriptions" [1], and an example that does not match the
  target task misleads ("Example pollution" [1]).
- **The exact output schema.** Field names, types, formats (ISO 8601, ISO 4217...), allowed
  values. Say what to output when a field cannot be found (`null`, never a guess).
- **A rule for each edge case the input can produce.** None, several, ambiguous, malformed:
  state the output for each, such as an empty list, one entry per item, or a review flag.
  "No error handling: Assuming outputs will always be well-formed" is a named pitfall [1].

## Rules an agent reads (CLAUDE.md, hooks, skills, commands)

Claude scans bullet and tree structure more reliably than it parses paragraphs. Default to
lists over prose for rules, steps, or conditions.

- **One item per condition**, each stating the trigger and the action, or what is blocked
  and what to do instead.
- **Don't restate what Claude already knows.** No explanation of what git, a branch, JSON or
  a tool Claude already understands is (e.g. what `AskUserQuestion` does): the reader is a
  model that knows them.

## Persuasion principles

Writing a rule that must hold under pressure (a skill, a hook message, a sub-agent prompt) ->
read [references/persuasion-principles.md](references/persuasion-principles.md): seven
principles (authority, commitment, scarcity, social proof, unity, reciprocity, liking), which
to combine per skill type, and their ethical limits.

---

[1] wshobson/agents, `prompt-engineering-patterns` (MIT). Sources: [SOURCES.md](SOURCES.md).
