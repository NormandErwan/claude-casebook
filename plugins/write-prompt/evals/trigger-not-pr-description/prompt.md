---
description: "Should not fire: PR description for humans"
tags: ["trigger", "should-not"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Write the pull request description for a change that moves our CI from Jenkins to GitHub Actions. Reviewers are the platform team.
