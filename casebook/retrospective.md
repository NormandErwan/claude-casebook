# Retrospective

One row per incident: a correction, a rule or skill that failed to fire or to cover the case, a
tool block that forced another approach, a new preference. Filed by `log-rule-incident`, without
reading this file. `Class` names the kind of failure, not the instance. `Evidence` lets a later
session check the row: quoted `user:` words, a commit, PR or `file:line`; the agent's own reading
is marked `hypothesis:`. `Replaces` names the rule or clause the change removes or subsumes.

| Date | Events | Class | Evidence | Proposed change | Replaces | Decision | Landed in |
|---|---|---|---|---|---|---|---|
| 2026-11-01 | new-preference | An eval procedure prescribes a hand-built harness when the platform ships a runner covering the same arms | user: "Add a retro to check if write-skill should use Claude plugin eval instead"; `plugins/write-skill/skills/write-skill/evaluating-skills-with-subagents.md:71` prescribes headless `claude -p` per arm; `claude plugin eval --help` lists a no-plugin baseline arm (`--ablation with-without`), `--runs`, `--judge-model`, `--max-cost-usd`, skills-dir targets; hypothesis: it covers write-skill Track 2 arms, isolation and grading, untested for the subagent-pressure scenarios | Check against the craft-prompt rebuild run (first use of `claude plugin eval` on a skill); if it holds, extend `evaluating-skills-with-subagents.md` to run arms with `claude plugin eval` and keep `claude -p` as fallback; same swap in NormandErwan/Claude `CONTRIBUTING.md` Testing step 2 | `evaluating-skills-with-subagents.md` headless `claude -p` arm setup | proposed | - |
| 2026-11-02 | skill-gap, tool-blocked | A second arm added to an already-piloted eval goes to its full run without its own pilot, so a broken arm burns the whole budget | Full run of the craft-prompt 2.0.0 arm built its fixture with `rsync`, absent in the container (`rsync: command not found`); the arm held no skill, 0 of 69 runs fired, $5.98 lost; a 1-run probe afterwards fired at $0.11. `test-rule-change` step 4 (`plugins/casebook/skills/test-rule-change/SKILL.md:38`) asks for a pilot per arm; hypothesis: read as once per eval, not once per arm built | Extend step 4: every arm built later (a rebuilt treatment, a second model) gets its own pilot before its full run | - | proposed | - |
