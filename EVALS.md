# Evals

How this repository runs its plugins' evals. The protocol (arms, pilot, recording) is
`test-rule-change`'s; this page only holds what is specific to these plugins. No case has been
run yet: every case below is written, load-checked, and unscored.

## Cases

Each plugin's cases sit in `plugins/<name>/evals/<case>/` (`prompt.md` + `graders/*.md`). The
older material under `plugins/<name>/skills/<name>/evals/` is the pre-casebook record, kept as
history: its numbers are not reproducible and are not compared with these.

| Plugin | Tag | Cases | Source |
|---|---|---|---|
| `write-hook` | `pressure`, `control` | s1-s5 | Scenario text copied from the `pressure-s*.txt` files |
| `write-hook` | `trigger` | 19 (12 positive, 7 negative) | `trigger-eval-set.json` |
| `write-skill` | `quality` | 3 | `evals.json`; eval 1 asks to print the file instead of writing it |
| `write-skill` | `pressure` | A1-A3 | Rebuilt from the scenario descriptions in `test-results.md` (the prompts were not kept) |
| `write-skill` | `trigger` | 12 (7 positive, 5 negative) | `trigger-evals.json` |
| `casebook` | `d1` | correction + control | New: does a user correction get a `casebook/retrospective.md` row? |
| `find-cause` | `recurrence`, `control` | 2 | New |
| `prevent-drift` | `drift` | 2 | New |

Every case runs `claude-sonnet-5-5`, 5 runs per arm. `llm` graders use the default judge
(`haiku`), stated with the results. A `tool_used: Skill` grader (`fired`, `skill-fired`) is a
plugin-fired indicator, not part of the score.

## Running

From the repository root, from a directory with no `.claude/skills/` copy of the plugin under
test and no ancestor `CLAUDE.md`:

```bash
# Pressure, quality, control: the default with-without ablation adds the no-plugin arm.
claude plugin eval plugins/write-hook --tag pressure --tag control --max-cost-usd <cap>

# Trigger cases: the question is whether the skill loads, so one arm only.
claude plugin eval plugins/write-skill --tag trigger --ablation none --max-cost-usd <cap>

# casebook writes its ledger: grant Write and Edit.
claude plugin eval plugins/casebook --allow-tools Write Edit --max-cost-usd <cap>
```

`--max-cost-usd 0` loads every case and stops before the first run, at no cost. It catches a
broken `prompt.md` frontmatter. It does not validate graders: a grader with an unknown `type`
loads.

## D1: the `SessionStart` hook versus the skill descriptions alone

The with-without ablation compares the plugin with no plugin. D1 compares the plugin with the
same plugin minus its hook, so it needs a second target, built at run time rather than kept as a
copy:

```bash
rm -rf /tmp/casebook-nohook && cp -r plugins/casebook /tmp/casebook-nohook && rm -r /tmp/casebook-nohook/hooks
claude plugin eval /tmp/casebook-nohook --tag d1 --allow-tools Write Edit --max-cost-usd <cap>
```

The `d1` correction case puts the correction in a single prompt. A correction that arrives
after a real exchange would need `context.history_file`, which this repository does not use yet.
