---
description: "Track B eval 1: create a skill (defensive-sql)"
tags: ["quality"]
runs: 5
model: "claude-sonnet-5-5"
max_turns: 10
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Create a new skill called 'defensive-sql' that teaches agents to always use parameterized queries. Include a bad example and a good example, a description, and a brief anti-patterns section.

Do not write any files - print the complete SKILL.md in your reply.
