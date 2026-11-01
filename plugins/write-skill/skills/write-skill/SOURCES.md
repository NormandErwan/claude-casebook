# Sources

This skill merges three upstream skills and a summary of Anthropic's documentation.
Skills it only names are listed at the end.
Each file carries a brief inline citation; this document gives the full provenance.
Licence texts are in `LICENSES/`. Everything not listed here is original to this repository
(BSD 3-Clause, root `LICENSE`).

---

## obra/superpowers — writing-skills

- **URL:** https://github.com/obra/superpowers/tree/main/skills/writing-skills
- **License:** MIT, Copyright (c) 2025 Jesse Vincent — `LICENSES/MIT-obra-superpowers.txt`
- **Files contributed:**
  - `SKILL.md` (base content)
  - `testing-skills-with-subagents.md`
  - `graphviz-conventions.dot`
  - `render-graphs.js`
  - `examples/CLAUDE_MD_TESTING.md`

Earlier versions of this file attributed these to mattpocock/skills. That was wrong: its
history never held a `writing-skills` skill.

---

## mattpocock/skills — writing-great-skills

- **URL:** https://github.com/mattpocock/skills (added 2026-06-17, `bc4cf90`; renamed
  `writing-for-agents` on 2026-07-23, `1fc6573`, which dropped `GLOSSARY.md` upstream)
- **License:** MIT, Copyright (c) 2026 Matt Pocock — `LICENSES/MIT-mattpocock-skills.txt`
- **Files contributed:**
  - `references/GLOSSARY.md`

---

## anthropics/skills — skill-creator

- **URL:** https://github.com/anthropics/skills/tree/main/skills/skill-creator
- **License:** Apache-2.0, Copyright 2026 Anthropic, PBC —
  `LICENSES/Apache-2.0-anthropics-skill-creator.txt`
- **Files contributed:**
  - `scripts/` (all Python evaluation scripts)
  - `agents/` (grader.md, comparator.md, analyzer.md)
  - `eval-viewer/` (generate_review.py, viewer.html)
  - `assets/eval_review.html`
  - `references/schemas.md`
- **Changes:** internal references renamed from `skill-creator` to this skill; `quick_validate.py`
  accepts a `version` frontmatter field.

---

## Anthropic — Skill authoring best practices

- **URL:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- **Used for:** `executable-code-skills.md` summarises the page's "Advanced: Skills with
  executable code" section in our own words and links to it; two anti-patterns and three
  checklist items in `SKILL.md` follow the same page. No text of the page is reproduced.

---

## Referenced, not bundled

These skills are named in `SKILL.md`; none of their text ships here.

- **`craft-prompt`** (prompt-structure pass, Skill Creation Checklist): the author's renamed fork
  of `prompt-engineering` from
  [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/customaize-agent/skills/prompt-engineering)
  (GPL-3.0). Any prompt-engineering skill can play this role.
- **`agent-skills:test-driven-development`** (background reading): from
  [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills).
