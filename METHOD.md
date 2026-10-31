# The casebook method

Rules you give Claude (a `CLAUDE.md`, a skill, a hook's injected text) pile up. Each one was
added for a reason, and most of the reasons are forgotten a month later. Some rules never fire;
some fire and make things worse; two rules end up saying the same thing in different words.

The method keeps one question answerable for every rule: **which case made us write it, and did
it work?** It costs two Markdown tables and two habits.

The procedures live in the `casebook` plugin's skills: `log-rule-incident` (filing and
processing) and `test-rule-change` (testing). This page explains why each step exists.

## Principles

- **Every rule is provisional.** Before adding a rule, extend an existing one that covers the
  case. A second rule for the same case is how rules start contradicting each other.
- **A rule earns its place with a logged case.** No incident, no rule. A rule that costs more
  than it returns (context on every session, friction, false positives) is deleted, not patched
  with a second rule.
- **Each rule reads trigger -> action.** "Be careful with X" cannot be checked. "Before X ->
  do Y" can: you can see whether it fired.
- **The class, not the instance.** A case is logged as the kind of failure it belongs to. A rule
  written for one session's file, tool or wording never fires again.

## The two ledgers

Both live in `casebook/` at your repository root. Templates ship with `log-rule-incident`.

| Ledger | Answers | Written |
|---|---|---|
| `retrospective.md` | What went wrong, and what change would prevent its class? | When it happens |
| `provenance.md` | Why does this rule exist, and what has changed it since? | In the commit after the rule changes |

### Why file without reading the ledger

An incident is filed in the middle of other work. Reading the whole ledger at that moment costs
context the task needs, and tempts a fix on the spot. So filing is append-only, and the row's
decision starts as `proposed`.

### Why processing reads the whole ledger

Processing happens later, on purpose. Reading every row first is how a recurrence shows up: the
same class filed a second time means the earlier fix did not hold. A recurrence calls for finding
the cause (the `find-cause` plugin), not for extending the same rule once more.

### Why the provenance row comes in the next commit

The row cites the commit that changed the rule, and a commit cannot cite its own hash. The row
lands in the following commit of the same change, so the rule and its reason merge together.

## Testing a rule change

`test-rule-change` sets the evidence each change needs and the steps of an A/B test. Why:

- **Stakes decide the evidence.** A rule that runs in every session, or gates an action that is
  hard to undo, costs more when wrong than a test costs to run. A narrower rule can be watched.
- **Watching counts only when the reply shows the outcome.** If judging it means taking the case
  apart, the observation is an A/B test run without a baseline.
- **A waived test is written down.** When the rule misbehaves later, the record shows it was
  never measured.
- **Review first, pilot first.** A run on a draft measures text that will not ship. A baseline
  that never fails cannot show the change helped, and a pilot finds that out for one run's cost.

## Three real rows

From the ledgers of [NormandErwan/Claude](https://github.com/NormandErwan/Claude), where this
method was built. Its `CLAUDE.md` is the owner's personal setup; only the method moved here.

**The class, not the instance** ([`RETROSPECTIVE.md` line 8](https://github.com/NormandErwan/Claude/blob/cd24a9c4b8897dfa726fb1f6aebf281957e0af6b/RETROSPECTIVE.md#L8)):

| Date | Events | Class | Proposed change | Replaces | Decision | Landed in |
|---|---|---|---|---|---|---|
| 2026-08-23 | skill-gap | Retrospective entries scoped to the incident instead of its class | Template names the class first; extend an existing rule by default; a skill's own misbehavior goes back to that skill | - | applied | `CLAUDE.md` + `CLAUDE.web.md` Retrospective |

The ledger's first rows were too specific to ever match a second case. This row is why the row
template starts with the class.

**A rule not added** ([line 9](https://github.com/NormandErwan/Claude/blob/cd24a9c4b8897dfa726fb1f6aebf281957e0af6b/RETROSPECTIVE.md#L9)):

| Date | Events | Class | Proposed change | Replaces | Decision | Landed in |
|---|---|---|---|---|---|---|
| 2026-08-23 | plan-revised | A rule kept for a feature the user does not use, on the strength of the request alone | None - `ponytail-review` flagged the agent-team lines as speculative, saying so at review time was enough for the user to drop them | - | no change | - |

An incident does not always need a rule. Here, the existing review step already caught the
problem, so the decision was `no change`.

**A recurrence traced to its cause** ([line 42](https://github.com/NormandErwan/Claude/blob/cd24a9c4b8897dfa726fb1f6aebf281957e0af6b/RETROSPECTIVE.md#L42), abridged):

| Date | Events | Class | Proposed change | Decision |
|---|---|---|---|---|
| 2026-09-05 | skill-gap (via `find-cause`) | Traced the handoff's two "rule existed and didn't fire" cases against this ledger and found four more of the same class since 2026-08-24 [...] - six occurrences, a recurrence. Root cause: several behavior-conditioning rules are phrased as principles judged against the agent's own reading of the situation ("non-trivial", "an affirmation", "obvious"), not as an explicit trigger with stated exceptions [...] | Generalize [the] low-freedom requirement to also cover a rule that gates whether to stop, ask, or escalate [...] | applied |

Reading the whole ledger turned two incidents into six of one class. The fix changed how a whole
family of rules is phrased (trigger -> action) instead of adding a seventh rule.

## Adopting it

1. Install the `casebook` plugin. Its `SessionStart` hook reminds Claude of the two skills
   in every session.
2. Create `casebook/retrospective.md` and `casebook/provenance.md` from the templates, or let
   `log-rule-incident` create them on the first incident.
3. Backfill provenance only for the rules you are about to change. A full archaeology pass is
   optional.

## Where it comes from

What each source contributes to the method. The links go to the primary source.

**Practice**

- **Test-first documentation:** [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/tree/main/skills/writing-skills):
  "no skill without a failing test first". `test-rule-change` applies it to rules: the baseline
  arm has to show the failure first.
- **Evidence before a claim:** superpowers `verification-before-completion`. A rule change does
  not "work" until it has been measured.
- **Blameless postmortems:** [Google SRE book, ch. 15](https://sre.google/sre-book/postmortem-culture/)
  recommends defining triggers before incidents and looking for contributing causes, not
  culprits. The retrospective ledger works the same way: its events are listed in advance, and
  a row names a class of failure, not who caused it.
- **Architecture decision records:** [Nygard, 2011](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions):
  a decision is recorded with its context and status (`proposed`, `accepted`, `superseded`).
  A provenance row does the same for a rule.
- **Kaizen root-cause tools** (A3, 5 whys, fishbone, PDCA), as packaged in
  [NeoLabHQ/context-engineering-kit `kaizen`](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/kaizen):
  `find-cause` is written from these public methods.

**Research**

- **Learning from failures without retraining:** Reflexion ([Shinn et al., 2023](https://arxiv.org/abs/2303.11366))
  keeps the agent's reflections on its feedback in memory. ExpeL ([Zhao et al., AAAI 2024](https://arxiv.org/abs/2308.10144))
  turns successes and failures into reusable insights. The casebook does both by hand, across
  sessions: one row per failure, and a rule only once a case justifies it.
- **Add small changes, don't rewrite:** ACE ([Zhang et al., ICLR 2026](https://arxiv.org/abs/2510.04618))
  shows that rewriting a context over and over erodes its details ("context collapse"), and that
  small structured updates avoid this. This is why filing only appends, and why processing
  extends an existing rule instead of rewriting it.
- **Every rule costs:** IFScale ([Jaroslawicz et al., 2025](https://arxiv.org/abs/2507.11538))
  finds that models follow fewer instructions as more pile up, favouring earlier ones; the best
  models reach 68% accuracy at 500 instructions. Context files raise agent cost by over 20%
  without improving success in general ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)).
  Models also use information in the middle of a long context less well ([Liu et al., TACL](https://arxiv.org/abs/2307.03172)).
  Hence "a rule earns its place" and "delete, don't patch".
