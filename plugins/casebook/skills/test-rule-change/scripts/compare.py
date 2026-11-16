#!/usr/bin/env python3
"""Compare arms run on the same cases (run-arm.sh results); write a table.

usage: compare.py OUT.md ARM_A.json ARM_B.json [ARM_C.json ...]
  Arm label = JSON file name without .json. OUT.md must not exist: the
  results doc links this file rather than being patched by a script.

Per case and grader: passes/runs per arm. Then mean score, total runs,
errors and cost per arm. No significance test: read small gaps as noise.
"""
import json
import os
import sys


def load(path):
    d = json.load(open(path))
    label = os.path.splitext(os.path.basename(path))[0]
    cases = {}
    for c in d["cases"]:
        runs = c["arms"].get("with", [])
        graders = {}
        for r in runs:
            for g in r.get("graders", []):
                p, n = graders.get(g["name"], (0, 0))
                graders[g["name"]] = (p + bool(g["passed"]), n + 1)
        cases[c["name"]] = {"graders": graders, "runs": runs}
    return label, d, cases


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__.strip())
    out, paths = sys.argv[1], sys.argv[2:]
    if os.path.exists(out):
        sys.exit(f"compare: {out} exists: write a new file")
    arms = [load(p) for p in paths]
    labels = [a[0] for a in arms]
    names = sorted(set().union(*(a[2] for a in arms)))
    missing = [(l, n) for l, _, c in arms for n in names if n not in c]
    if missing:
        sys.exit(f"compare: cases missing from an arm: {missing[:5]}")
    versions = {a[1].get("claudeVersion") for a in arms}

    lines = [f"Claude Code {', '.join(sorted(map(str, versions)))}. Cell = passes/runs.", "",
             "| Case | Grader | " + " | ".join(labels) + " |",
             "|---|---|" + "---|" * len(labels)]
    totals = {l: [0, 0] for l in labels}
    for n in names:
        for g in sorted(arms[0][2][n]["graders"]):
            cells = []
            for l, _, c in arms:
                p, k = c[n]["graders"].get(g, (0, 0))
                totals[l][0] += p
                totals[l][1] += k
                cells.append(f"{p}/{k}")
            lines.append(f"| {n} | {g} | " + " | ".join(cells) + " |")
    lines.append("| **all** | | " + " | ".join(f"**{p}/{k}**" for p, k in totals.values()) + " |")

    lines += ["", "| Arm | Runs | Errors | Runs with a denial or ungranted tool | Mean score | Cost (USD) |",
              "|---|---|---|---|---|---|"]
    for (l, d, c), path in zip(arms, paths):
        runs = [r for v in c.values() for r in v["runs"]]
        errs = sum(1 for r in runs if r.get("error"))
        mean = sum(r["score"] for r in runs) / len(runs) if runs else 0
        # Denials live in the traces: read run-arm.sh's summary when present.
        summary = path[:-5] + ".runs.jsonl" if path.endswith(".json") else ""
        denied = "n/a"
        if os.path.exists(summary):
            rows = [json.loads(line) for line in open(summary)]
            denied = sum(1 for r in rows if r.get("denials") or r.get("ungranted"))
        lines.append(f"| {l} | {len(runs)} | {errs} | {denied} | {mean:.2f} | {d['costUsd']:.2f} |")

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"compare: wrote {out}")


if __name__ == "__main__":
    main()
