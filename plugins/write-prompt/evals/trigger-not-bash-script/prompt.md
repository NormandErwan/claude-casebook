---
description: "Should not fire: a shell script"
tags: ["trigger", "should-not"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write a bash script that dumps our Postgres database `shop` every night with `pg_dump`, keeps the last 7 dumps, and deletes older ones.
