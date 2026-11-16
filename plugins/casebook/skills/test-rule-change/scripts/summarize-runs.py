#!/usr/bin/env python3
"""Keep one summary line per run, then delete the kept eval temp dirs.

usage: summarize-runs.py OUT.json   -> writes OUT.runs.jsonl

plugin eval deletes transcripts unless --keep-temp; run-arm.sh keeps them and
calls this. Per run: case, score, cost, skills called, tools called, files
written (Write/Edit paths, plus Bash commands that look like writes), and
permission denials: what a later audit of the batch needs.
"""
import json
import os
import re
import shutil
import subprocess
import sys

BASH_WRITE = re.compile(r"(^|[^>])>{1,2}\s*[^&\s]|\bsed\s+-i\b|\btee\b|\bmv\b|\bcp\b")


def summarize(trace):
    """Tool use of one run. `ungranted`: calls to a tool plugin eval removed
    (no --allow-tools grant): they fail as "No such tool available", not as
    permission denials."""
    s = {"skills": [], "tools": [], "files": [], "bash_writes": [], "denials": [],
         "ungranted": []}
    names = {}
    for line in open(trace):
        e = json.loads(line)
        if e.get("type") == "result":
            s["denials"] = [d.get("tool_name") for d in e.get("permission_denials", [])]
        content = e.get("message", {}).get("content")
        if e.get("type") == "user" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_result" and "No such tool available" in str(c.get("content")):
                    s["ungranted"].append(names.get(c.get("tool_use_id"), "?"))
        if e.get("type") != "assistant":
            continue
        for c in e.get("message", {}).get("content", []):
            if c.get("type") != "tool_use":
                continue
            name, inp = c.get("name"), c.get("input", {})
            names[c.get("id")] = name
            s["tools"].append(name)
            if name == "Skill":
                s["skills"].append(inp.get("skill"))
            elif name in ("Write", "Edit", "NotebookEdit") and inp.get("file_path"):
                s["files"].append(inp["file_path"])
            elif name == "Bash" and BASH_WRITE.search(inp.get("command", "")):
                s["bash_writes"].append(inp["command"][:200])
    return s


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip())
    src = sys.argv[1]
    out = re.sub(r"\.json$", "", src) + ".runs.jsonl"
    if os.path.exists(out):
        sys.exit(f"summarize-runs: {out} exists")
    res = json.load(open(src))
    kept, n = set(), 0
    with open(out, "w") as f:
        for c in res["cases"]:
            for arm, runs in c["arms"].items():
                for i, r in enumerate(runs):
                    row = {"case": c["name"], "arm": arm, "run": i, "score": r.get("score"),
                           "cost_usd": r.get("costUsd"), "error": r.get("error")}
                    t = r.get("tracePath")
                    if t and os.path.exists(t):
                        row.update(summarize(t))
                        kept.add(os.path.dirname(os.path.dirname(t)))
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    n += 1
    for d in kept:
        if "claude-eval-" in os.path.basename(d):
            subprocess.run(["chmod", "-R", "u+rwX", d])
            shutil.rmtree(d, ignore_errors=True)
    print(f"summarize-runs: {n} runs -> {out}; {len(kept)} temp dirs removed")


if __name__ == "__main__":
    main()
