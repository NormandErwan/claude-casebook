# CLAUDE.md

Rules for changing this repository. They govern this repository only: don't copy this file into
another project.

## Layout

- One plugin per directory: `plugins/<name>/.claude-plugin/plugin.json`, skills in
  `plugins/<name>/skills/<skill>/`. The `casebook` plugin also holds `hooks/`.
- `METHOD.md` explains why; the `casebook` skills say how. A procedure step lives in a skill,
  never restated in `METHOD.md`: link to it.
- `casebook/` holds this repository's own ledgers, kept with its own `casebook` skills.

## Changing a skill

- Bump `version` per `write-skill` semver. A plugin has one version: its `plugin.json` and every
  `SKILL.md` in it carry the same value (CI checks). The marketplace entry carries no version.
- Rule or skill change -> `log-rule-incident` (provenance row) and `test-rule-change` (evidence)
  apply here as anywhere.
- Third-party content added or changed -> update the skill's `SOURCES.md` and `LICENSES/`.
- Code, docs, commits and PRs -> English.

## Before pushing

- `claude plugin validate --strict plugins/<name>` passes for every changed plugin.
- A plugin enters `.claude-plugin/marketplace.json` only once its evals pass.

## Releasing

- `claude plugin tag plugins/<name> --push` creates and pushes `<name>--v<version>`.
