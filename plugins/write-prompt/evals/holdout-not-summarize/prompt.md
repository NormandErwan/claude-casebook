---
description: "Holdout should not fire: using the model directly"
tags: ["trigger", "holdout", "should-not"]
runs: 3
model: "claude-opus-5-5"
max_turns: 8
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Summarize this in two sentences: "The migration moved 40 services to the new cluster over three weekends. Two services needed rollbacks because of DNS caching, both fixed within an hour. Latency dropped 18% on average."
