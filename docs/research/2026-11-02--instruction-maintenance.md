# Maintaining instructions for LLM coding agents

Research date: 2026-11-02. Scope: persistent context files (CLAUDE.md, AGENTS.md, Cursor rules,
Copilot instructions, system prompts) and reusable skills or prompt libraries. I used primary
sources only: papers, vendor documentation, and the practitioners' own publications. Every number
below was read in the cited source. Where I could not fetch a source, I say so.

Evidence levels: **peer-reviewed** (accepted at a named venue), **preprint** (arXiv, not yet
accepted), **vendor documentation**, **published practice** (a practitioner's or vendor's own
write-up of what they did, without peer review).

## Summary of findings

1. **Instruction files grow by accretion and are rarely pruned.** In 2,303 agent context files,
   changes are "frequent, small additions", and deletions have a median under 15 words per commit
   ([Agent READMEs](https://arxiv.org/abs/2511.12884)). In 1,262 prompt changes in application
   code, developers mostly add or modify text, only 21.9% of changes are documented in commit
   messages, and some changes introduce logical inconsistencies
   ([Prompting in the Wild](https://arxiv.org/abs/2412.17298)). Over 99% of SKILL.md files contain
   at least one "skill smell", and the smells rarely disappear as the skills evolve
   ([Anatomy to Smells](https://arxiv.org/abs/2607.01456)).
2. **Instructions have a measured cost, and the benefit is not guaranteed.** In a controlled
   evaluation, context files did not generally improve task success, and they raised inference
   cost by over 20% ([Gloaguen et al.](https://arxiv.org/abs/2602.11988)). Instruction-following
   accuracy falls as the number of instructions grows: the best frontier models reach 68% at 500
   instructions ([IFScale](https://arxiv.org/abs/2507.11538)). Performance degrades as input
   grows across 18 models ([Chroma, Context Rot](https://www.trychroma.com/research/context-rot)).
3. **Agents do follow what is written.** A tool named in a context file was used 1.6 times per
   task (`uv`), against under 0.01 times when it was not named
   ([Gloaguen et al.](https://arxiv.org/html/2602.11988)). The risk is therefore over-compliance
   with instructions that do not help, more than instructions being ignored.
4. **Vendor practice has converged.** The vendors recommend short always-loaded files (Claude
   Code: under 200 lines; Cursor: rules under 500 lines; Skills: SKILL.md body under 500 lines).
   They recommend scoped or lazy-loaded rules, adding a rule only after a repeated mistake, and
   moving rules that must never be broken out of the prompt and into deterministic hooks.
   Anthropic now ships an LLM audit (`/doctor prompt-audit`) for outdated, dead-reference and
   contradicting instructions ([Claude Code memory docs](https://code.claude.com/docs/en/memory)).
5. **Model upgrades make instructions obsolete.** Anthropic and OpenAI (with Cursor) both
   document instructions that helped older models but hurt newer ones: emphasis that causes
   over-application, and thoroughness prompts that cause excessive search.
6. **Evaluation is the weakest link.** The vendors recommend evaluation-driven development: a
   baseline without the instruction, at least three scenarios, and testing on every target model
   ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
   Anthropic states that there is "not currently a built-in way to run these evaluations".
   Formatting alone can swing accuracy by up to 76 points
   ([Sclar et al.](https://arxiv.org/abs/2310.11324)), so a before/after comparison on a few runs
   is weak evidence.
7. **Removal is not free.** Rewriting an evolved context into a short summary collapsed it from
   18,282 to 122 tokens, and accuracy fell below the no-context baseline
   ([ACE](https://arxiv.org/html/2510.04618)). Curated skills helped on average, but 16 of 84
   tasks got worse ([SkillsBench v1](https://arxiv.org/abs/2602.12670v1)). Mature fields offer
   transferable mechanisms: anomaly taxonomies for rule bases, test coverage for policy-as-code,
   "update docs in the same change" and "default to delete" for documentation, and
   ADD/UPDATE/DELETE/NOOP curation with quality gating for agent memory.

---

## 1. What degrades in an instruction set, and how it is detected

### Observed degradation

| Failure mode | Evidence | Source |
| - | - | - |
| **Accretion, rare pruning** | Files evolve like configuration code, through "frequent, small additions". 67.0% of Claude Code files were modified in several commits. The median update interval is 23.8 h for Claude Code and 22.3 h for Codex. Median deletions are under 15 words per commit, against a median of 57.0 words added per Claude Code commit. In a manual sample of 100 commits: 78 addition labels, 32 modifications, 19 deletions. | [Agent READMEs, 2511.12884](https://arxiv.org/abs/2511.12884) ([HTML](https://arxiv.org/html/2511.12884)) |
| **Undocumented change, logical inconsistency** | 1,262 prompt changes in 243 repositories. Prompts are changed mainly by additions and modifications. Only 21.9% of changes are documented in commit messages. Changes can introduce logical inconsistencies and misalignment with the LLM's responses. | [Prompting in the Wild, 2412.17298](https://arxiv.org/abs/2412.17298) |
| **Persistent quality defects in skills** | 238 skills analysed. An automated detector finds at least one "skill smell" in over 99% of SKILL.md files. The smells "rarely disappear as skills evolve". | [Anatomy to Smells, 2607.01456](https://arxiv.org/abs/2607.01456) |
| **Redundancy with the repository** | Repository overviews did not help. LLM-generated files improved by 2.7% when the repository's documentation was removed, which suggests the files duplicate the docs. | [Gloaguen et al., 2602.11988](https://arxiv.org/html/2602.11988) |
| **Conflicts** | "If two instructions contradict each other, Claude may pick one arbitrarily". User-level and project-level rules do not override each other. | [Claude Code memory](https://code.claude.com/docs/en/memory) |
| | "Contradictory or vague instructions can be more damaging to GPT-5 than to other models." | [OpenAI GPT-5 prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide) |
| | Across six models, the system/user separation "fails to establish a reliable instruction hierarchy". Models show strong built-in biases toward certain constraint types. | [Control Illusion, 2502.15851](https://arxiv.org/abs/2502.15851) |
| **Obsolescence after a model change** | Emphasis such as IMPORTANT or ALL CAPS was needed by older models. With current models, "piling on emphasis mostly makes Claude over-apply the rule". | [Claude Code best practices](https://code.claude.com/docs/en/best-practices) |
| | At Cursor, a "maximize_" thoroughness instruction became "counterproductive with GPT-5", causing excessive, repetitive search on small tasks. | [GPT-5 prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide) |
| **Obsolescence after a codebase change** | Cursor: "Reference files instead of copying their contents" so rules don't go stale. Skills: avoid time-sensitive information, or move it to an "Old patterns" section. | [Cursor rules](https://cursor.com/docs/context/rules), [Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| **Never-used content** | "If Claude never accesses a bundled file, it might be unnecessary or poorly signaled." | [Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| | When the skill pool grows from 5 to 100, actual-use precision falls from 29.6% to 3.3%. | [Demystifying Agent Skills, 2608.14036](https://arxiv.org/abs/2608.14036) |
| **Silent truncation** | Codex stops adding AGENTS.md files once their combined size reaches `project_doc_max_bytes`, 32 KiB by default. | [Codex AGENTS.md docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| | Claude Code loads only the first 200 lines or 25KB of auto-memory `MEMORY.md`. A subdirectory CLAUDE.md or rules file over its per-file limit arrives truncated. | [Claude Code memory](https://code.claude.com/docs/en/memory) |
| **Harmful learned content** | Agents show "experience-following": inaccurate stored experiences propagate errors to later tasks. Some executions that look correct are misleading as experiences. | [Xiong et al., 2505.16067](https://arxiv.org/abs/2505.16067) |

### Detection methods in use

- **LLM audit.** `/doctor prompt-audit` looks for "instructions written for older models,
  references to files or commands that don't exist, and files that contradict each other". It
  reports proposed edits and changes nothing until asked. It covers CLAUDE.md, AGENTS.md, rules,
  skills, commands, subagents and output styles
  ([Claude Code memory](https://code.claude.com/docs/en/memory)). `/doctor` also suggests cuts
  for content Claude can work out from the code
  ([best practices](https://code.claude.com/docs/en/best-practices)). OpenAI points to its
  "prompt optimizer tool" for finding contradictions
  ([GPT-5 guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide)).
- **Load tracing.** Claude Code's `InstructionsLoaded` hook logs which files load and why. `/context`
  shows what was actually loaded ([memory](https://code.claude.com/docs/en/memory)). For Codex, you
  can ask it to summarise its instructions, or read `codex-tui.log`
  ([Codex docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)).
- **Static linting.** agnix (MIT/Apache-2.0) states "757 rules across Claude Code, Codex CLI,
  OpenCode, Cursor, Copilot, and more", drawn from specs, research and "real-world breakage
  patterns". It does not claim to evaluate whether instructions work
  ([agnix repository](https://github.com/agent-sh/agnix)). A smell detector for SKILL.md also
  exists in research ([2607.01456](https://arxiv.org/abs/2607.01456)).
- **Usage observation.** Vendors recommend watching navigation paths, missed references, sections
  read over and over, and ignored files
  ([Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
- **Gap:** I found no primary study that measures how often context files go stale relative to
  the code. The staleness claims I found were in secondary commentary only, so I do not use them.

## 2. The cost of instructions

### Context and money

- **Cost.** In a controlled study (SWE-bench and a new benchmark of repositories with
  developer-written files), LLM-generated files raised cost by about 20% and 23%. Developer files
  raised it by at most 19%. Both added steps (2.45 and 3.92 steps for LLM files; 3.34 for
  developer files). They also raised GPT-5.2 reasoning tokens by 22% and 14% (LLM files) and by
  20% (developer files). Removing the "testing" section reduced cost significantly, without a
  significant accuracy change ([Gloaguen et al., HTML](https://arxiv.org/html/2602.11988)).
- **Counter-measurement.** In an observational study of 10 repositories and 124 PRs, the presence
  of AGENTS.md was associated with lower median runtime (Δ28.64%) and lower output tokens
  (Δ16.58%), with comparable completion ([Lulla et al., 2601.20404](https://arxiv.org/abs/2601.20404)).
- **Caching changes the price but not the attention cost.** On the Claude API, cache reads cost
  0.1x the base input price (0.05x for Opus/Sonnet 5.5). 5-minute cache writes cost 1.25x and
  1-hour writes cost 2x. Any system-prompt change invalidates the system and messages caches, so
  editing instructions has its own cost
  ([prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).
- **Loading model.** CLAUDE.md, auto memory, MCP tool names and skill descriptions all load before
  the first prompt. Skill bodies load on demand and are re-injected after compaction, capped at
  5,000 tokens per skill and 25,000 in total
  ([context window docs](https://code.claude.com/docs/en/context-window)). @-imports organise a
  file but "don't reduce its context cost"
  ([memory](https://code.claude.com/docs/en/memory)). Copilot instructions "are sent with every
  chat message"
  ([GitHub docs](https://docs.github.com/en/copilot/concepts/prompting/response-customization)).

### Compliance

- **Instruction density.** IFScale (500 keyword instructions, 20 models) found "68% accuracy at
  the max density of 500 instructions" for the best models, distinct degradation patterns by
  model class, and a primacy bias toward earlier instructions
  ([2507.11538](https://arxiv.org/abs/2507.11538)).
- **Length.** In Chroma's tests of 18 models, "model performance consistently degrades with
  increasing input length". Even a single distractor hurts
  ([Context Rot](https://www.trychroma.com/research/context-rot)). Accuracy also drops when
  relevant information sits in the middle of a long context
  ([Lost in the Middle, TACL](https://arxiv.org/abs/2307.03172)).
- **Vendor statements, not measurements.** "Longer files consume more context and reduce
  adherence" (target under 200 lines). Every line "takes a little of Claude's attention on every
  task" ([memory](https://code.claude.com/docs/en/memory),
  [best practices](https://code.claude.com/docs/en/best-practices)). Anthropic: context is "a
  finite resource with diminishing marginal returns", with an "attention budget"
  ([Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- **CLAUDE.md is not enforced.** It is "delivered as a user message after the system prompt",
  with "no guarantee of strict compliance". Rules that must always hold should be hooks
  ([memory](https://code.claude.com/docs/en/memory)).

## 3. Practices and tools for revising, merging, retiring and versioning

### Triggers for adding or changing an instruction

- **Repeated mistakes.** Claude Code says to add when "Claude makes the same mistake a second
  time", when a code review catches something, or when you retype the same correction
  ([memory](https://code.claude.com/docs/en/memory)). Cursor says to "Start simple. Add rules only
  when you notice Agent making the same mistake repeatedly"
  ([Cursor rules](https://cursor.com/docs/context/rules)).
- **Observed failure modes.** Start from a minimal prompt with the best model, then add
  instructions "based on failure modes"
  ([Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- **Agent error in a PR or issue.** Cursor: update the rule when Agent gets something wrong. You
  can tag @cursor on a GitHub issue or PR to update it
  ([Cursor rules](https://cursor.com/docs/context/rules)).
- **Model change.** Re-audit for "instructions written for older models"
  ([memory](https://code.claude.com/docs/en/memory)). Test skills on every model you plan to use
  ([Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### Triggers for retiring or moving an instruction

- **The model can infer it.** Remove what Claude can work out from the code, such as an
  architecture or layout description ([best practices](https://code.claude.com/docs/en/best-practices)).
  Gloaguen et al. found that overviews do not help.
- **Escalation.** "If you keep adding emphasis to a CLAUDE.md line and Claude still misses it,
  that's a sign the line belongs in a hook." In the other direction, hooks that only encode
  preferences should be deleted ([best practices](https://code.claude.com/docs/en/best-practices)).
- **Scope.** Procedures belong in skills (loaded on demand). Path-specific rules belong in scoped
  rules: `.claude/rules/` with `paths:`, Cursor "Apply to Specific Files", or Copilot
  `.github/instructions/**/*.instructions.md`
  ([memory](https://code.claude.com/docs/en/memory),
  [Cursor](https://cursor.com/docs/context/rules),
  [GitHub](https://docs.github.com/en/copilot/concepts/prompting/response-customization)).
- **Size thresholds.** Claude Code: under 200 lines per CLAUDE.md. Cursor: each rule under 500
  lines, split into composable rules. Skills: SKILL.md body under 500 lines, with references one
  level deep. Auto memory: a write near the limit prompts Claude to "merge or drop stale entries",
  and an over-limit index produces an error telling Claude to rewrite it
  ([memory](https://code.claude.com/docs/en/memory)).

### Merging and precedence (needed for conflict resolution)

The tools resolve conflicts differently:

- **Codex:** concatenates files from the root down; files closer to the working directory "take
  precedence because they appear later"
  ([Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md)).
- **AGENTS.md convention:** "the closest one takes precedence", and chat prompts override the file
  ([agents.md](https://agents.md/)).
- **Cursor:** Team, then Project, then User rules; "earlier sources win"
  ([Cursor](https://cursor.com/docs/context/rules)).
- **Copilot on GitHub.com:** personal instructions, then repository (path-specific, then
  repository-wide, then AGENTS.md), then organization. Other clients combine the files with no
  general precedence order
  ([GitHub](https://docs.github.com/en/copilot/concepts/prompting/response-customization)).
- **Claude Code:** neither user nor project rules override the other ("Claude may follow either
  one") ([memory](https://code.claude.com/docs/en/memory)).

### Versioning

- Vendors recommend checking the files into git
  ([Cursor](https://cursor.com/docs/context/rules)). Copilot PR review reads instructions from
  the head branch
  ([GitHub](https://docs.github.com/en/copilot/concepts/prompting/response-customization)).
  Skills keep deprecated material in a collapsed "Old patterns" section
  ([Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
- Empirically, the commit history is a poor change log: only 21.9% of prompt changes are
  documented ([2412.17298](https://arxiv.org/abs/2412.17298)).

### Automated revision

- **Arize Prompt Learning.** A loop runs the agent on training issues, checks patches with unit
  tests, adds LLM-judge explanations, and has a meta-prompt rewrite the rules. Reported results
  for Claude Code (Sonnet 4.5) on SWE-bench Lite: +5.19% on held-out repositories, +10.87% on a
  time-split within Django. Absolute baselines are not reported. Explanations gave the optimizer
  more signal than pass/fail alone
  ([Arize blog, Nov 2025](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)).
  The cookbook warns that too much training data risks overfitting
  ([Arize cookbook](https://arize.com/docs/ax/cookbooks/improve/optimizing-coding-agent-prompts-for-execution.md)).
- **ACE (Agentic Context Engineering).** The context is kept as itemised bullets with IDs and
  helpful/harmful counters. A Reflector proposes delta entries, and a non-LLM Curator merges them.
  "Grow-and-refine" de-duplicates with embeddings. The authors report +10.6% on agent benchmarks
  and +8.6% on finance benchmarks ([ACE, 2510.04618, ICLR 2026](https://arxiv.org/abs/2510.04618)).

## 4. Evaluating the effect of an instruction, before and after a change

- **Vendor method (Anthropic).** "Create evaluations BEFORE writing extensive documentation":
  1. identify gaps by running without the skill;
  2. build three scenarios;
  3. measure a baseline;
  4. write minimal instructions;
  5. iterate against the baseline.

  The checklist asks for at least three evaluations, tests on Haiku, Sonnet and Opus, and
  real-usage scenarios. A "Claude A writes, Claude B tests" loop complements it. There is "not
  currently a built-in way to run these evaluations"
  ([Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
- **Write instructions so compliance can be checked.** Use concrete instructions, such as "Run
  `npm test` before committing" rather than "Test your changes"
  ([memory](https://code.claude.com/docs/en/memory)).
- **Research method: paired with/without runs on verifiable tasks.** Gloaguen et al. compare no
  file, an LLM-generated file and a developer file on SWE-bench-style tasks. They measure success,
  steps, cost and tool-use traces (for example, the uplift in `uv` use). They then ablate sections
  of the file, such as the testing section. Their conclusion: any such file "should be rigorously
  evaluated before deployment" ([2602.11988](https://arxiv.org/html/2602.11988)). SkillsBench
  pairs no-skill and curated-skill runs on tasks with deterministic verifiers, across 18
  model-harness configurations in v4 ([2602.12670](https://arxiv.org/abs/2602.12670)).
- **Behavioural trace metrics.** Evaluations can measure more than pass rate: tool calls per
  instance, steps before the first relevant edit, and reasoning tokens
  ([Gloaguen et al.](https://arxiv.org/html/2602.11988)). Skill research separates "procedural
  anchoring" (65.7% of skill cases) from knowledge injection (4.5%). It also shows that exact
  invocation is "neither sufficient nor necessary" for success, so whether a skill was invoked is
  a poor proxy for its effect ([2608.14036](https://arxiv.org/abs/2608.14036)).
- **Noise floor.** Formatting alone can change accuracy by up to 76 points (LLaMA-2-13B,
  few-shot) ([Sclar et al., ICLR 2024](https://arxiv.org/abs/2310.11324)). A before/after
  difference needs repeated runs and significance testing. Gloaguen et al. report p-values, and
  most of their success deltas are not significant.
- **Split by time and by repository.** Arize evaluates on held-out repositories and on a
  chronological split, which guards against overfitting the rules to the training issues
  ([Arize](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)).

## 5. Analogies from mature fields with a transferable mechanism

| Field | Mechanism | Transfer to agent instructions | Source |
| - | - | - | - |
| Expert systems (XCON/R1) | XCON reached 6,200 rules in 7 years, with about 50% changing each year. Performance stayed satisfactory, but the rule base became "increasingly more difficult to change". DEC built a new language, RIME, for maintainability. | Rule bases decay through churn rather than through accuracy loss. Structure and modularity are maintenance investments. | [Soloway, Bachant & Jensen, AAAI-87](https://mlanthology.org/aaai/1987/soloway1987aaai-assessing) (peer-reviewed) |
| Rule-base verification | Four anomaly types: redundancy, ambivalence (conflict), circularity, deficiency. Anomalies are "highly indicative of errors", meaning symptoms rather than proof. Five checking tools are compared. | A ready taxonomy for an instruction-set linter or audit. An anomaly is a flag for review, not an automatic deletion. | [Preece, Shinghal & Batarekh, KER 1992](https://www.maxapress.com/article/doi/10.1017/S026988890000624X) (peer-reviewed; abstract only, and the 1994 IJIS PDF redirected and could not be fetched) |
| Policy-as-code (OPA) | Policies have unit tests (`test_` rules) and `opa test --coverage` reports uncovered lines. `--fail-on-empty` makes CI fail when no tests run. | Each instruction gets at least one scenario. "Coverage" would mean instructions that no evaluation exercises, the analogue of never-used rules. | [OPA policy testing](https://www.openpolicyagent.org/docs/policy-testing) (vendor documentation) |
| Documentation maintenance (Google) | Docs should be "alive but frequently trimmed, like a bonsai tree". "Change your documentation in the same CL as the code change". "Default to delete", because "Stragglers can always be recovered". Ownership is named in the README. | Change instructions in the same change as the code they describe. Prefer deletion, since git keeps the history. Name an owner. | [Google docguide best practices](https://google.github.io/styleguide/docguide/best_practices.html) (published practice) |
| Agent memory (Mem0) | For each candidate fact, retrieve similar memories, then an LLM picks ADD, UPDATE, DELETE or NOOP. A contradicted memory is deleted. The graph variant marks it invalid instead, to keep history. | A concrete merge protocol for a new rule against the existing set: deduplicate, merge, retire the contradicted rule, or do nothing. | [Mem0, 2504.19413](https://arxiv.org/html/2504.19413) (preprint) |
| Agent memory (experience quality) | Experience-following propagates errors. Regulating the quality of stored experience matters, and later task evaluations can serve as free quality labels. | Retain instructions on the evidence of their outcomes. Gate additions instead of storing every lesson. | [Xiong et al., 2505.16067](https://arxiv.org/abs/2505.16067) (preprint) |
| Agent memory (ACE) | Itemised bullets with helpful/harmful counters, incremental deltas instead of whole rewrites, and embedding de-duplication. | Edit instructions item by item, keep a per-instruction record of whether it helped, and avoid wholesale rewrites. | [ACE, 2510.04618](https://arxiv.org/html/2510.04618) (peer-reviewed, ICLR 2026, per arXiv listing) |

## 6. Evidence against: maintenance that did not help, removals that hurt

- **Shortening by rewriting destroyed value.** In ACE's case study, a Dynamic Cheatsheet context
  of 18,282 tokens (accuracy 66.7) collapsed in one step to 122 tokens. Accuracy fell to 57.1,
  below the 63.7 no-adaptation baseline. The authors name "brevity bias" and "context collapse" as
  failure modes of prompt optimizers that favour concise summaries
  ([ACE](https://arxiv.org/html/2510.04618)).
- **Comprehensive is not better, but neither is "none".** Focused skills with 2–3 modules
  outperform comprehensive documentation. Yet curated skills raised the average pass rate (v1:
  +16.2pp; v4: 33.9% to 50.5%), so removing them would cost performance on average
  ([SkillsBench](https://arxiv.org/abs/2602.12670)).
- **Curated skills still hurt some tasks.** 16 of 84 tasks showed negative deltas in v1
  ([SkillsBench v1](https://arxiv.org/abs/2602.12670v1)). An average gain hides regressions on
  individual tasks.
- **Automated authoring without feedback did not help.** "Self-generated Skills provide no
  benefit on average" ([SkillsBench v1](https://arxiv.org/abs/2602.12670v1)). Gloaguen et al.
  recommend "omitting LLM-generated context files for the time being", and stronger models did not
  write better files ([2602.11988](https://arxiv.org/html/2602.11988)). Feedback-driven
  optimization (Arize, ACE) reports gains. The difference seems to be grounding in task outcomes.
- **Removing whole files may not save resources.** Lulla et al. associate AGENTS.md with lower
  runtime and output tokens ([2601.20404](https://arxiv.org/abs/2601.20404)). This cuts against a
  "delete it all" reading of Gloaguen et al.
- **Deletion in memory: little effect unless it is quality-aware.** Xiong et al. study addition
  and deletion and stress experience quality. The abstract I read does not quantify the gains
  from deletion, and I did not verify the deletion numbers in the full text
  ([2505.16067](https://arxiv.org/abs/2505.16067)).
- **Skills persist with defects despite maintenance.** Skills are actively edited, yet their
  smells rarely disappear, so routine edits do not remove quality defects
  ([2607.01456](https://arxiv.org/abs/2607.01456)).

## Open questions and contradictions

1. **Net value of context files.** Gloaguen et al. (controlled, cost up by over 20%, no general
   success gain) contradict Lulla et al. (observational, runtime down 28.64%, output tokens down
   16.58%). They measure different things: total inference cost versus wall-clock time and
   output tokens. They also use different designs and task sets. No study reconciles them.
2. **Inconsistent numbers inside one paper across versions.** The v1 abstract of 2602.11988 says
   context files "tend to reduce task success rates". The v3 abstract says they "do not generally
   improve" them. In the fetched v3 HTML, the developer-file gain (+2.4%, p = 0.21) differed from
   a "7%" figure in the introduction. Secondary write-ups circulate "-3% / +4%", which I could not
   find in the versions I read. SkillsBench also changed between versions: v1 reports 84 tasks
   and +16.2pp, v4 reports 87 tasks, +16.6pp and 18 configurations, and the self-generated-skills
   claim is not in the v4 abstract. Cite a specific version.
3. **Concise versus complete.** Vendors push brevity: under 200 lines, "smallest possible set of
   high-signal tokens". ACE shows that brevity bias and context collapse hurt, and argues for
   growing, itemised contexts. One possible reconciliation, not tested in any source: the cost of
   always-loaded content differs from that of content retrieved on demand.
4. **Emphasis.** The Skill best practices suggest stronger wording ("MUST filter") when a rule is
   missed. The newer Claude Code best practices say piling on emphasis makes Claude over-apply the
   rule, and recommend a hook or a shorter file instead. This is probably model-dependent.
5. **Where position matters.** Lost in the Middle finds a strong position effect. IFScale finds a
   primacy bias. Chroma reports that needle position showed "no notable effect". The task types
   differ (retrieval, instruction lists, needle-in-haystack).
6. **Precedence semantics are not standardised.** For Cursor, earlier sources win. For Codex and
   AGENTS.md, the closest or later file wins. Claude Code defines no override. Copilot ranks
   personal first on GitHub.com and has no general order elsewhere. Control Illusion shows models
   do not reliably honour declared hierarchies anyway.
7. **Never-used detection.** No vendor exposes per-instruction usage or attribution telemetry.
   Load logs (`InstructionsLoaded`, `/context`) show what loaded, not what changed behaviour.
   Per-item helpful/harmful counters exist only in research systems (ACE).
8. **Staleness rate.** I found no primary measurement of how fast context files diverge from the
   code they describe.
9. **Not fetched or not verified:** Preece & Shinghal 1994 (IJIS) full text (redirect). The
   Arize talk figures ("up to 11%", "10–15%") appear only on event and docs pages without
   methodology, so I did not use them. The OpenAI GPT-5 prompting guide shows no publication date
   on the fetched page.

## Sources

| Title | Link | Date | Evidence level |
| - | - | - | - |
| Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents? (Gloaguen et al.) | https://arxiv.org/abs/2602.11988 | v1 2026-02-12, v3 2026-09-29 | preprint |
| On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents (Lulla et al.) | https://arxiv.org/abs/2601.20404 | v1 2026-01-28, v2 2026-03-30 | preprint |
| Agent READMEs: An Empirical Study of Context Files for Agentic Coding (Chatlatanagulchai et al.) | https://arxiv.org/abs/2511.12884 | v1 2025-11-17, v2 2026-08-09 | preprint |
| On the Use of Agentic Coding Manifests: An Empirical Study of Claude Code | https://arxiv.org/abs/2509.14744 | 2025-09-18 | preprint |
| Context Engineering for AI Agents in Open-Source Software (Mohsenimofidi et al.) | https://arxiv.org/abs/2510.21413 | v4 2026-02-05 | peer-reviewed (MSR 2026) |
| Harness Engineering for Agentic AI Coding Tools: An Exploratory Study (Galster et al.) | https://arxiv.org/abs/2602.14690 | v1 2026-02-16, v5 2026-06-30 | preprint |
| Prompting in the Wild: An Empirical Study of Prompt Evolution in Software Repositories | https://arxiv.org/abs/2412.17298 | 2024-12-23 (v2 2025-01-12) | peer-reviewed (MSR 2025) |
| From Anatomy to Smells: An Empirical Study of SKILL.md in Agent Skills | https://arxiv.org/abs/2607.01456 | 2026-07-01 | preprint |
| Demystifying Agent Skills: Why They Work—Until They Don't | https://arxiv.org/abs/2608.14036 | 2026-08-14 | preprint |
| SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks | https://arxiv.org/abs/2602.12670 | v1 2026-02-13, v4 2026-06-14 | preprint (NeurIPS 2026 poster listing seen in search, not verified) |
| How Many Instructions Can LLMs Follow at Once? (IFScale) | https://arxiv.org/abs/2507.11538 | 2025-07-15 | preprint |
| Context Rot: How Increasing Input Tokens Impacts LLM Performance (Chroma) | https://www.trychroma.com/research/context-rot | 2025-07-14 | published practice (technical report) |
| Lost in the Middle: How Language Models Use Long Contexts | https://arxiv.org/abs/2307.03172 | 2023 | peer-reviewed (TACL) |
| Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design | https://arxiv.org/abs/2310.11324 | 2023-10-17 (v2 2024-07-01) | peer-reviewed (ICLR 2024) |
| Control Illusion: The Failure of Instruction Hierarchies in LLMs | https://arxiv.org/abs/2502.15851 | 2025-02-21 (v4 2025-12-04) | peer-reviewed (AAAI-26) |
| Agentic Context Engineering (ACE) | https://arxiv.org/abs/2510.04618 | 2025-10-06 (v3 2026-03-29) | peer-reviewed (ICLR 2026, per arXiv listing) |
| Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | https://arxiv.org/abs/2504.19413 | 2025-04-28 | preprint |
| How Memory Management Impacts LLM Agents: Experience-Following Behavior | https://arxiv.org/abs/2505.16067 | 2025-05-21 (v2 2025-10-10) | preprint |
| Claude Code docs: How Claude remembers your project (memory) | https://code.claude.com/docs/en/memory | undated; accessed 2026-11-02 | vendor documentation |
| Claude Code docs: Best practices | https://code.claude.com/docs/en/best-practices | undated; accessed 2026-11-02 | vendor documentation |
| Claude Code docs: Explore the context window | https://code.claude.com/docs/en/context-window | undated; accessed 2026-11-02 | vendor documentation |
| Skill authoring best practices (Anthropic) | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | undated; accessed 2026-11-02 | vendor documentation |
| Prompt caching (Anthropic) | https://platform.claude.com/docs/en/build-with-claude/prompt-caching | undated; accessed 2026-11-02 | vendor documentation |
| Effective context engineering for AI agents (Anthropic) | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | 2025-09-29 | published practice (vendor engineering blog) |
| GPT-5 prompting guide (OpenAI Cookbook) | https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide | undated on page (marked archived) | vendor documentation |
| Codex: AGENTS.md | https://learn.chatgpt.com/docs/agent-configuration/agents-md | undated; accessed 2026-11-02 | vendor documentation |
| AGENTS.md | https://agents.md/ | undated; accessed 2026-11-02 | vendor documentation (format specification site) |
| Cursor: Rules | https://cursor.com/docs/context/rules | undated; accessed 2026-11-02 | vendor documentation |
| GitHub Copilot: About customizing Copilot responses | https://docs.github.com/en/copilot/concepts/prompting/response-customization | undated; accessed 2026-11-02 | vendor documentation |
| CLAUDE.md best practices learned from optimizing Claude Code with Prompt Learning (Arize) | https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/ | 2025-11 | published practice |
| Optimizing coding agent prompts for execution (Arize cookbook) | https://arize.com/docs/ax/cookbooks/improve/optimizing-coding-agent-prompts-for-execution.md | undated | vendor documentation |
| agnix (agent configuration linter) | https://github.com/agent-sh/agnix | accessed 2026-11-02 | published practice (open-source repository) |
| Assessing the Maintainability of XCON-in-RIME (Soloway, Bachant, Jensen) | https://mlanthology.org/aaai/1987/soloway1987aaai-assessing | 1987 | peer-reviewed (AAAI-87) |
| Principles and practice in verifying rule-based systems (Preece, Shinghal, Batarekh) | https://www.maxapress.com/article/doi/10.1017/S026988890000624X | 1992 | peer-reviewed (Knowledge Engineering Review); abstract only |
| OPA: Policy testing | https://www.openpolicyagent.org/docs/policy-testing | undated; accessed 2026-11-02 | vendor documentation |
| Google documentation guide: Best practices | https://google.github.io/styleguide/docguide/best_practices.html | undated; accessed 2026-11-02 | published practice |
