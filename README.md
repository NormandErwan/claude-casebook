# claude-casebook

[![validate](https://github.com/NormandErwan/claude-casebook/actions/workflows/validate.yml/badge.svg)](https://github.com/NormandErwan/claude-casebook/actions/workflows/validate.yml)

Claude Code plugins that keep your `CLAUDE.md`, skills and hooks short and trustworthy. Every
rule cites the incident that justified it, and any change to a rule that runs in every session
is A/B tested before it merges.

## Why

Rules you give Claude pile up. A month later nobody remembers why half of them exist, some
never fire, and two say the same thing in different words. Each one also costs context in every
session: research finds that context files raise agent cost by over 20% without improving task
success in general ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)). A rule has to
earn its place.

## What you get

| Plugin | What it does for you |
|---|---|
| `casebook` | Claude files its own failures as one-line rows while it works, and records why each rule exists. A failure that comes back goes to root-cause analysis instead of becoming one more rule. A `SessionStart` hook keeps this active. See [`METHOD.md`](METHOD.md). |
| `write-skill` | Write a skill test-first: see the agent fail without it, then write it, then A/B test it and tune when it triggers |
| `write-hook` | Write hooks whose output actually reaches the model, without a `Stop` hook that keeps restarting the turn |
| `find-cause` | Trace a failure that keeps coming back to the decision that allowed it, then check the fix against evidence named in advance |
| `prevent-drift` | Keep each fact in one file; find copies that have already drifted apart |

## How it differs

Other projects also learn from Claude's mistakes. They turn a mistake into a rule right away;
casebook asks for a logged case before a rule, and a test before a rule change.

| Project | How it learns | What casebook adds |
|---|---|---|
| [aviadr1/claude-meta](https://github.com/aviadr1/claude-meta) | A reflection prompt turns each mistake into a `CLAUDE.md` rule | A ledger that links each rule to its incident; recurrences get root-cause analysis instead of a new rule |
| [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) `reflexion` | `/memorize` curates reflections into `CLAUDE.md` (the [ACE](https://arxiv.org/abs/2510.04618) method) | The same, with a test before merging any change to an always-on rule |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | Hooks observe sessions and record "instincts" with a confidence score | Readable ledgers you review and commit, rather than automatic recording |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | Skills evolve every night from sessions, behind a gate | Each change cites a case, and changes to always-on rules are measured with an A/B test |

## Built on

| Source | What we reuse |
|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) (MIT) | `writing-skills` is the base of `write-skill`. Its rule "no skill without a failing test first" became the method's "no rule without a case" and its baseline-first A/B tests |
| [anthropics/skills](https://github.com/anthropics/skills) `skill-creator` (Apache-2.0) | Eval scripts, grader agents and viewer, bundled in `write-skill` |
| [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) | The glossary bundled in `write-skill`; `find-cause` calls `grilling` when a problem is too vague to write down |
| [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) (GPL-3.0) | Its `kaizen` plugin inspired `find-cause`, which was rewritten from the public methods (A3, 5 whys, fishbone, PDCA): no code or text was copied. `write-skill` recommends a prompt-structure pass with its `prompt-engineering` skill (forked elsewhere as `craft-prompt`), which is not bundled |
| Research and engineering practice | Reflexion, ExpeL, ACE, studies on instruction load and context files, blameless postmortems, ADRs: see [`METHOD.md`](METHOD.md#where-it-comes-from) |

Per-file details: each skill's `SOURCES.md` and `LICENSES/`.

## Install

The marketplace lists a plugin only once its evals pass, and none has passed yet. Until then:

- One skill: `npx skills add NormandErwan/claude-casebook -s write-skill -a claude-code`
  (with the [`skills`](https://github.com/vercel-labs/skills) installer)
- A whole plugin, hook included, from a clone: `claude --plugin-dir plugins/casebook`

Once listed:

```
/plugin marketplace add NormandErwan/claude-casebook
/plugin install casebook@claude-casebook
```

## Licence

BSD 3-Clause ([`LICENSE`](LICENSE)), except the third-party files `write-skill` bundles under MIT
and Apache-2.0. Rules for changing this repository: [`CLAUDE.md`](CLAUDE.md).
