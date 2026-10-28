# claude-casebook

[![validate](https://github.com/NormandErwan/claude-casebook/actions/workflows/validate.yml/badge.svg)](https://github.com/NormandErwan/claude-casebook/actions/workflows/validate.yml)

Skills for writing the rules, skills and hooks you give Claude, and a method that keeps each
rule backed by a logged case.

## What this is

When you work with Claude Code for a while, you write rules: a `CLAUDE.md`, a few skills, a hook
or two. A month later, nobody remembers why half of them exist, some never fire, and two say the
same thing differently.

This repository holds two things:

1. **The casebook method** ([`METHOD.md`](METHOD.md)). Every rule cites the incident that
   justified it. Claude logs its own failures as they happen, one line each. A recurring kind of
   failure goes to a root-cause analysis instead of one more rule. A change to an always-on rule
   gets an A/B test before it merges.
2. **Skills for writing rules well**, each built and tested with that method.

It was extracted from [NormandErwan/Claude](https://github.com/NormandErwan/Claude), the
author's personal setup, where the method has run since 2026-08 (over a hundred logged
incidents). The full history of each skill came along.

## Plugins

| Plugin | Contents |
|---|---|
| `casebook` | The method: `log-rule-incident` (file incidents, record why a rule exists), `test-rule-change` (A/B test a rule change), and a `SessionStart` hook that reminds Claude of both |
| `write-skill` | Write and test Agent Skills: baseline-first (RED-GREEN-REFACTOR for documentation), A/B evals, trigger tuning |
| `write-hook` | Write Claude Code hooks whose output reaches the model, without a `Stop` hook restart cascade |
| `write-guide` | Write a method guide someone else will follow: framing gates, evidence labels, review checklist |
| `write-french` | French that does not read as translated English: six defects, each with worked examples |

Each plugin carries its own version in `plugins/<name>/.claude-plugin/plugin.json`. Releases are
tagged `<plugin>--v<version>`.

## Install

**Not in the marketplace yet.** The marketplace (`.claude-plugin/marketplace.json`) lists a
plugin only once its evals pass. Until then:

- One skill, with the [`skills`](https://github.com/vercel-labs/skills) installer:
  `npx skills add NormandErwan/claude-casebook -s write-skill -a claude-code`
- A whole plugin, hook included, from a clone:
  `claude --plugin-dir plugins/casebook`

Once listed:

```
/plugin marketplace add NormandErwan/claude-casebook
/plugin install casebook@claude-casebook
```

`write-skill` names `agent-skills:test-driven-development` as background reading; it comes from
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills).

## Related projects

Each covers part of this ground. Descriptions are the projects' own, quoted from GitHub (checked
2026-10-26).

| Project | Its description | Overlap |
|---|---|---|
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | "The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond." | Learns from sessions: hooks observe them and record "instincts" with a confidence score |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | "380 Claude Code skills & agent skills & plugins [...]" | Evolves skills nightly from real sessions behind a gate; `CLAUDE.md` changes need a human adopt step |
| [aviadr1/claude-meta](https://github.com/aviadr1/claude-meta) | "Self-improving AI: Transform CLAUDE.md into a learning system. One prompt makes Claude learn from every mistake. Meta-rules + reflection = continuous improvement." | Turns each mistake into a `CLAUDE.md` rule through a reflection prompt; no ledger, no test |

## Licence

BSD 3-Clause ([`LICENSE`](LICENSE)). `write-skill` bundles third-party files under MIT and
Apache-2.0: see its `SOURCES.md` and `LICENSES/`.

## Contributing

[`CLAUDE.md`](CLAUDE.md) holds the rules for changing this repository. It governs this
repository only: don't copy it into another project.
