# Backlog

Work not done yet, one `###` section per task. Format and rules: the `backlog` skill.

## Conventions

- Tracker: BACKLOG.md
- New tasks: add without asking
- Finished task: delete its section
- Owner steps: on

## Tasks

### Decide when plugins get tagged, then tag them
- **Status:** owner steps pending
- **Context:** `git tag -l` is empty: no plugin has ever been released, `write-prompt` and `backlog` included although the marketplace lists them. `CLAUDE.md` "Releasing" says how to tag, not when; `casebook/retrospective.md` row 2026-11-03 "A repository rule says how to release but not when" proposes the fix and is settled by this task.
  2026-11-24: a cloud session merged PR#15 and ran `claude plugin tag plugins/backlog --push` from
  `main`: tag created locally, push refused (`HTTP 403` from the session's git proxy). Tagging stays
  an owner step until the CI workflow proposed in `casebook/retrospective.md` (2026-11-24 row) exists.
- **Next:** owner decided 2026-11-16: only marketplace-listed plugins (`CLAUDE.md` "Releasing", PR#10). After PR#10 merges, the owner runs the steps below; delete this task once both tags are on `origin`.
- **Done when:**
  - [x] `CLAUDE.md` "Releasing" says when a plugin is tagged
  - [x] The retrospective row is `applied`, `Landed in` PR#10
  - [ ] Every plugin the new rule covers has a `<name>--v<version>` tag on `origin`
- **Owner steps:** after merge, from an up-to-date `main` checkout. Shown for the two listed plugins; add one step per other plugin the decision covers.
  1. Tag `write-prompt`: `claude plugin tag plugins/write-prompt --push`
     - Check: `git ls-remote --tags origin` lists `refs/tags/write-prompt--v2.2.0`
     - Undo: `git push origin :refs/tags/write-prompt--v2.2.0 && git tag -d write-prompt--v2.2.0`
  2. Tag `backlog`: `claude plugin tag plugins/backlog --push`
     - Check: `git ls-remote --tags origin` lists `refs/tags/backlog--v0.2.0`
     - Undo: `git push origin :refs/tags/backlog--v0.2.0 && git tag -d backlog--v0.2.0`
- **Out of scope:** a workflow that tags automatically (file it as its own task if wanted).

### Run the casebook evals and decide its marketplace entry
- **Status:** ready
- **Context:** `plugins/casebook/evals/` has 2 cases (`correction-files-row`, `control-no-correction`), written and load-checked, never scored (`EVALS.md`). Retrospective row 2026-11-03 "An eval case grades a file the agent must write while the case grants no tool that writes files" asks for a pilot first; `EVALS.md` now passes `--allow-tools Write Edit`. A plugin enters the marketplace only once its evals pass (`CLAUDE.md`).
- **Next:** pilot one run per arm with the `EVALS.md` command and check that the no-plugin arm does not list the skill and that the correction case can write `casebook/retrospective.md`.
- **Done when:**
  - [ ] Pilot then full run (5 runs per arm, `claude-sonnet-5-5`) recorded in a `casebook/provenance.md` row, with cost
  - [ ] The Write-grant retrospective row is decided
  - [ ] `casebook` listed in `.claude-plugin/marketplace.json` if the evals pass, or the reason it is not in the provenance row
- **Out of scope:** the hook-versus-no-hook comparison (next task).

### Compare casebook with and without its SessionStart hook
- **Status:** ready
- **Blocked by:** Run the casebook evals and decide its marketplace entry
- **Context:** `EVALS.md` section "D1" describes the run: the `d1` cases against a copy of `plugins/casebook` without `hooks/`. It answers whether the hook earns its context cost in every session (`METHOD.md` principles).
- **Next:** build the no-hook copy and run the `d1` tag with the `EVALS.md` commands, pilot first.
- **Done when:**
  - [ ] Both arms scored at 5 runs per arm, results and cost in the `casebook` hook's provenance row
  - [ ] Hook kept, changed or removed according to the result, through `test-rule-change`
- **Out of scope:** multi-turn corrections via `context.history_file`.

### Run the find-cause evals
- **Status:** ready
- **Context:** `plugins/find-cause/evals/` has 2 cases (`recurring-ci-break`, `control-single-bug`), never scored (`EVALS.md`). Over ~100 agent runs, launch from a fresh session: retrospective row 2026-11-02 on the shared usage quota.
- **Next:** pilot one run per arm with `claude plugin eval plugins/find-cause --max-cost-usd <cap>`.
- **Done when:**
  - [ ] Pilot then full run recorded in a `casebook/provenance.md` row, with cost
  - [ ] `find-cause` listed in `.claude-plugin/marketplace.json` if the evals pass, or the reason it is not in the row

### Run the prevent-drift evals
- **Status:** ready
- **Context:** `plugins/prevent-drift/evals/` has 2 cases (`drifted-copies`, `restate-config`), never scored (`EVALS.md`).
- **Next:** pilot one run per arm with `claude plugin eval plugins/prevent-drift --max-cost-usd <cap>`.
- **Done when:**
  - [ ] Pilot then full run recorded in a `casebook/provenance.md` row, with cost
  - [ ] `prevent-drift` listed in `.claude-plugin/marketplace.json` if the evals pass, or the reason it is not in the row

### Run the write-hook evals
- **Status:** ready
- **Context:** `plugins/write-hook/evals/` has 5 pressure/control cases and 19 trigger cases, never scored (`EVALS.md`). Trigger cases run with `--ablation none`. Over ~100 agent runs, launch from a fresh session (retrospective row 2026-11-02 on the usage quota).
- **Next:** pilot one run per arm of the `pressure` and `control` tags with the `EVALS.md` command.
- **Done when:**
  - [ ] Pilot then full runs of both suites recorded in a `casebook/provenance.md` row, with cost
  - [ ] `write-hook` listed in `.claude-plugin/marketplace.json` if the evals pass, or the reason it is not in the row
- **Out of scope:** re-checking the harness claim dated 2026-08 (its own retrospective row).

### Run the write-skill evals
- **Status:** ready
- **Context:** `plugins/write-skill/evals/` has 3 quality, 3 pressure and 12 trigger cases, never scored (`EVALS.md`). Two retrospective rows of 2026-11-03 plan to re-run `pressure-a1`..`a3` after rewording the skill: this run is their baseline. Launch from a fresh session if over ~100 agent runs.
- **Next:** pilot one run per arm of the `pressure` and `quality` tags.
- **Done when:**
  - [ ] Pilot then full runs of all three suites recorded in a `casebook/provenance.md` row, with cost
  - [ ] `write-skill` listed in `.claude-plugin/marketplace.json` if the evals pass, or the reason it is not in the row

### Test the backlog plugin beyond its pilot
- **Status:** ready
- **Context:** `backlog` is listed in the marketplace on a pilot (1 run per arm) plus a trigger A/B on one case, a fuller run waived at the time (its `casebook/provenance.md` row). The owner now wants it tested properly. Untested behaviours include: extending a matching task instead of duplicating it, working a task (status, `Next` rewrite), deleting a done task, `Owner steps` listed in the reply, `Blocked by`, the archive and external-tracker conventions.
- **Next:** list the skill's rules and red flags with no case covering them, then write cases for the ones that matter most, with `scaffold.sh` fixtures like the existing ones.
- **Done when:**
  - [ ] New cases under `plugins/backlog/evals/`, listed in `EVALS.md`
  - [ ] Pilot, then every case at 5 runs per arm with-without on `claude-sonnet-5-5`, results and cost in the `backlog` provenance row
  - [ ] Any failure filed in `casebook/retrospective.md` or fixed with a version bump

### Move write-skill's eval procedure to claude plugin eval
- **Status:** ready
- **Context:** `plugins/write-skill/skills/write-skill/evaluating-skills-with-subagents.md` ("Isolate the arms") still runs each arm with headless `claude -p`, while `test-rule-change` and the write-prompt rebuild already use `claude plugin eval` (no-plugin arm, `--runs`, `--judge-model`, `--max-cost-usd`). Retrospective row 2026-11-01 "An eval procedure prescribes a hand-built harness". Untested: whether `claude plugin eval` keeps the isolation the file requires (no ancestor `CLAUDE.md`, no synced same-named skill) and covers the subagent-pressure scenarios.
- **Next:** pilot one pressure case under `claude plugin eval` with a probe that quotes an arm-specific passage; check no ancestor `CLAUDE.md` loads.
- **Done when:**
  - [ ] the file runs arms with `claude plugin eval`, `claude -p` kept as the fallback for what it cannot cover, plugin version bumped
  - [ ] NormandErwan/Claude `CONTRIBUTING.md` Testing step 2 points to the same runner
  - [ ] the retrospective row reads `applied` with this PR

### Reword write-skill's emphatic lines and its no-exception test rule
- **Status:** ready
- **Context:** two retrospective rows of 2026-11-03. `write-skill` keeps inherited `REQUIRED BACKGROUND: You MUST` lines, and `cso-guide.md` shows `You MUST` as the good form; current models over-apply that register (hypothesis, `code.claude.com/docs/en/best-practices`). Its "no skill without a failing test first, no exceptions" contradicts `test-rule-change`'s table (observe a narrow rule, waive with a reason); its evidence dates from Sonnet 4.6.
- **Next:** take the "Run the write-skill evals" baseline, then rewrite the lines in plain case with their reason and align the test rule with `test-rule-change`.
- **Done when:**
  - [ ] no unexplained MUST/REQUIRED left in `plugins/write-skill`, `cso-guide.md` examples included
  - [ ] the test rule matches `test-rule-change`, re-tested on Opus 5.5
  - [ ] `pressure-a1`..`a3` re-run against the baseline, results in the `write-skill` provenance row
  - [ ] both retrospective rows read `applied` with this PR
- **Blocked by:** Run the write-skill evals

### Re-check write-hook's observed hook behaviours on current Claude Code
- **Status:** ready
- **Context:** `plugins/write-hook/skills/write-hook/SKILL.md` states hook behaviours "observed in Claude Code web sessions, 2026-08-22 and 2026-08-23" with no Claude Code version; `transcripts/red-s2.md` disagrees on `additionalContext` for `Stop`. Retrospective row 2026-11-03 "A skill's central claim about harness behaviour carries an observation date but no harness version".
- **Next:** in a web session, run one minimal hook per event in the skill's table and record what reaches the model.
- **Done when:**
  - [ ] each table row confirmed or corrected, with the Claude Code version next to the date
  - [ ] `red-s2.md` disagreement resolved, plugin version bumped
  - [ ] the retrospective row reads `applied` with this PR

### Run the first maintenance pass
- **Status:** ready
- **Context:** `log-rule-incident` "Maintenance pass" (PR#10): on each new model generation and every three months, `/doctor prompt-audit` per plugin, then on the repository; each finding kept becomes a `retrospective.md` row. The last audits ran 2026-11-03 (PR #5), so the next pass is due by 2027-02-03, or earlier if a new model generation ships.
- **Next:** on the due date, run the audit on each plugin under `plugins/`, then on `.`.
- **Done when:**
  - [ ] every kept finding filed as a row in `casebook/retrospective.md`
  - [ ] this task's due date moved three months on, rather than the task deleted

### Express A/B test cost estimates as a share of the subscription limit
- **Status:** needs owner: whether any conversion is reliable enough to report (owner parked it 2026-11-24)
- **Context:** `test-rule-change` step 5 and `test-rule-change.py` report cost in USD (`--max-cost-usd`, compare table), which says little to a Pro subscriber whose limit is a 5-hour window. Owner measurement: resuming a 300k-token session on Opus moved the 5-hour gauge from 0 to 5%, about 6M tokens per window. Three reasons it does not convert as is: the gauge rounds (4.5-5.5% gives 5.5-6.7M); usage depends on model, message length and effort ([support article](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work)), and evals often run Haiku; a resume is uncached input, while an eval run is mostly cache reads, whose weight is unknown.
- **Next:** option kept on 2026-11-24 if resumed: sum tokens per run from the eval's `trace.jsonl`, divide by an owner-calibrated tokens-per-window rate per model, print "about X% of the 5-hour window" next to the USD figure. Ask the owner for a Haiku rate first.
- **Done when:**
  - [ ] the owner decides to build it or drops the task
  - [ ] if built: `test-rule-change.py` prints the estimate after the pilot, step 5 of `SKILL.md` asks to state it, plugin version bumped
- **Out of scope:** removing `--max-cost-usd`: it stays the only hard cap `plugin eval` offers.

### Decide where research and eval results live
- **Status:** needs owner: inside the skill dir, at the repository root, or in a plugin-level folder
- **Context:** interim: `test-rule-change`'s research and results sit in its skill dir,
  `research/` (owner, 2026-11-16), so they ship with each install (about 150 KB, no context cost).
  `docs/research/` holds one root-level note; `EVALS.md` keeps cases in `plugins/<name>/evals/`.
- **Next:** list each kind of file (research note, eval cases, run results JSON, comparison table) and ask the owner where each goes, with the install size of each option.
- **Done when:**
  - [ ] the rule written in `CLAUDE.md` "Layout"
  - [ ] existing research and result files moved to match it, and links updated

### Check backlog 0.2.0 on the next three unfinished tasks
- **Status:** blocked: waits until three sessions, in any repository using `backlog` 0.2.0, leave a task unfinished after a failed approach or an owner decision
- **Context:** `backlog` 0.2.0 adds `Ruled out:` and asks a session ending unfinished to record failed
  approaches there and owner decisions in `Context`. Owner, 2026-11-24: observe it instead of an A/B
  (`casebook/provenance.md`, row `backlog` 0.2.0). Origin: `session_01RGXu8XnXTwy41PoZB1yopT`.
- **Next:** on each session that leaves a task unfinished, check its `BACKLOG.md` diff for the failed
  approach and the owner's decisions; list the repository, session id and result here.
- **Done when:**
  - [ ] three sessions checked, each listed here with its id and whether the task carried both
  - [ ] a miss reported to the owner, or the provenance row noted "observed 3/3"
