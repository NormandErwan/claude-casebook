# Skills with Executable Code

Checklist for a skill that bundles scripts. A markdown-only skill can skip this file.
Full guidance, with worked examples: Anthropic's [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
section "Advanced: Skills with executable code". This file is a summary in our own words.

## Scripts

- A script handles its own errors (missing file, no permission) and returns something usable.
  A script that crashes leaves the agent to guess.
- Every constant (timeout, retry count) carries a comment saying why that value. An
  unexplained number cannot be adjusted by the agent either.
- Ship a script for any deterministic operation (validation, extraction, packing). It costs
  no context until run, and gives the same result every time.
- Each reference to a script says whether to **run** it or **read** it as reference. Running
  is the default: only its output enters the context.

## Verifiable intermediate steps

For batch, destructive or high-stakes work: the agent writes a plan file, a script validates
it, then the plan is applied and the result checked. Validation errors name the faulty item
and the valid alternatives, so the agent can fix the plan without guessing.

## Environment

- List required packages in `SKILL.md`. Never assume one is installed: the platforms differ
  in network access and runtime installs (see the page above for each).
- MCP tools are named in full, `ServerName:tool_name`, or the agent may not find them.
- Paths use forward slashes. File names say what the file holds.

## Checklist - code and scripts

- [ ] Scripts handle errors instead of deferring them to the agent
- [ ] No unexplained constants
- [ ] Required packages listed and checked as available
- [ ] Run vs read intent explicit for every script reference
- [ ] Validation step before any batch or destructive operation
- [ ] Forward-slash paths only

---

_Summary of Anthropic's skill-authoring best practices. See `SOURCES.md`._
