---
description: "Should not fire: README section"
tags: ["trigger", "should-not"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write the "Installation" section of the README for our CLI tool `pkgsync`. It installs with `pipx install pkgsync` and needs Python 3.11 or later.
