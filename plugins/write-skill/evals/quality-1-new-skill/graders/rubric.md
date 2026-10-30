---
type: "llm"
---

PASS if the printed SKILL.md has all of: YAML frontmatter with `name` and `description`; a description that names when to use the skill and does not mention "parameterize" or "interpolate"; at least one fenced code block with a bad and a good example; an anti-patterns section.
FAIL if any of these is missing, or no SKILL.md is printed.
