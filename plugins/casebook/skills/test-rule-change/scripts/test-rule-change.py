#!/usr/bin/env python3
"""A/B test a CLAUDE.md rule or a skill with `claude plugin eval`. Stdlib only.

plugin eval never loads a CLAUDE.md, so an arm is a plugin dir whose
SessionStart hook prints that arm's CLAUDE.md; skills come in as plugin
skills (roster name `<arm>:<skill>`). Each subcommand refuses a known way to
waste a paid run.

usage:
  test-rule-change.py edit FILE OLD NEW
      replace OLD by NEW only if OLD occurs exactly once ("@path" reads a file)
  test-rule-change.py build --out DIR [--claude-md FILE] [--skills DIR]... [--evals DIR]
      new arm dir; name = basename of DIR; later --skills wins
  test-rule-change.py diff ARM_A ARM_B PATH...
      arms must differ, and only under the named arm-relative paths
      (ignores .claude-plugin/plugin.json and evals/results/)
  test-rule-change.py preflight ARM CASE [plugin eval flags...]
      free checks, then a 1-run pilot of CASE; not --runs/--case/--max-cost-usd
  test-rule-change.py run ARM OUT.json [plugin eval flags...]
      scored run with fixed flags; also writes OUT.runs.jsonl
  test-rule-change.py compare OUT.md A.json B.json [C.json...]
      passes/runs per case, grader and arm, then per-arm totals
"""
import filecmp
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HEADER = "Contents of CLAUDE.md (project instructions, checked into the codebase):\n\n"
HOOKS_JSON = """{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "cat \\"${CLAUDE_PLUGIN_ROOT}/hooks/claude-md.txt\\"" } ] }
    ]
  }
}
"""
BASH_WRITE = re.compile(r"(^|[^>])>{1,2}\s*[^&\s]|\bsed\s+-i\b|\btee\b|\bmv\b|\bcp\b")
IGNORED = (".claude-plugin/plugin.json", "evals/results")


def die(cmd, msg):
    sys.exit(f"test-rule-change {cmd}: {msg}")


def usage():
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(2)


def has_flag(flags, name):
    """True for `--x val` and `--x=val`."""
    return any(f.split("=")[0] == name for f in flags)


# edit: arm text derived by one checked edit, never by regex.

def edit(args):
    if len(args) != 3:
        usage()

    def arg(s):
        if s.startswith("@"):
            with open(s[1:], encoding="utf-8") as f:
                return f.read()
        return s

    path, old, new = args[0], arg(args[1]), arg(args[2])
    with open(path, encoding="utf-8") as f:
        text = f.read()
    n = text.count(old)
    if n != 1:
        die("edit", f"{path}: expected 1 match, found {n}: {old[:60]!r}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))
    print(f"test-rule-change edit: {path}: 1 edit")


# build

def build(args):
    opts = {"--out": None, "--claude-md": None, "--evals": None}
    skills = []
    while args:
        if len(args) < 2 or (args[0] not in opts and args[0] != "--skills"):
            die("build", f"unknown or incomplete arg: {args[0]}")
        if args[0] == "--skills":
            skills.append(args[1])
        else:
            opts[args[0]] = args[1]
        args = args[2:]
    out, claude_md, evals = opts["--out"], opts["--claude-md"], opts["--evals"]
    if not out:
        die("build", "--out required")
    if os.path.lexists(out):
        die("build", f"{out} exists: build each arm fresh")
    name = os.path.basename(os.path.normpath(out))
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        die("build", f"arm name '{name}': lowercase letters, digits, dashes")
    if claude_md and not os.path.isfile(claude_md):
        die("build", f"no file {claude_md}")
    for d in skills + ([evals] if evals else []):
        if not os.path.isdir(d):
            die("build", f"no dir {d}")

    os.makedirs(os.path.join(out, ".claude-plugin"))
    with open(os.path.join(out, ".claude-plugin", "plugin.json"), "w") as f:
        f.write(f'{{\n  "name": "{name}",\n  "version": "0.0.0",\n  "description": "A/B arm {name}"\n}}\n')

    for d in skills:
        for s in sorted(glob.glob(os.path.join(d, "*", "SKILL.md"))):
            src = os.path.dirname(s)
            dst = os.path.join(out, "skills", os.path.basename(src))
            shutil.rmtree(dst, ignore_errors=True)  # later --skills wins
            shutil.copytree(src, dst, symlinks=True)

    if claude_md:
        os.makedirs(os.path.join(out, "hooks"))
        # Same header the harness puts on a real project CLAUDE.md.
        with open(claude_md, "rb") as f:
            body = f.read()
        with open(os.path.join(out, "hooks", "claude-md.txt"), "wb") as f:
            f.write(HEADER.encode() + body)
        with open(os.path.join(out, "hooks", "hooks.json"), "w") as f:
            f.write(HOOKS_JSON)

    if evals:
        shutil.copytree(evals, os.path.join(out, "evals"), symlinks=True)

    n = len(glob.glob(os.path.join(out, "skills", "*", "SKILL.md")))
    print(f"arm {name}: {n} skills, claude-md: {claude_md or 'none'}, evals: {evals or 'none'}")


# diff

def tree_diff(a, b, rel=""):
    """Top-most differing paths: only on one side, file vs dir, or content."""
    names = set(os.listdir(a) if os.path.isdir(a) else []) | set(os.listdir(b) if os.path.isdir(b) else [])
    for n in sorted(names):
        p, pa, pb = f"{rel}{n}", os.path.join(a, n), os.path.join(b, n)
        if not (os.path.exists(pa) and os.path.exists(pb)):
            yield p
        elif os.path.isdir(pa) and os.path.isdir(pb):
            yield from tree_diff(pa, pb, p + "/")
        elif os.path.isdir(pa) or os.path.isdir(pb) or not filecmp.cmp(pa, pb, shallow=False):
            yield p


def under(p, prefix):
    return p == prefix or p.startswith(prefix + "/")


def diff(args):
    if len(args) < 3:
        usage()
    a, b, allowed = args[0].rstrip("/"), args[1].rstrip("/"), [p.rstrip("/") for p in args[2:]]
    for arm in (a, b):
        if not os.path.isdir(arm):
            die("diff", f"no dir {arm}")
    diffs = [p for p in tree_diff(a, b) if not any(under(p, i) for i in IGNORED)]
    if not diffs:
        die("diff", f"{a} and {b} are identical: the arms test nothing")
    bad = False
    for p in diffs:
        if any(under(p, x) for x in allowed):
            print(f"  expected: {p}")
        else:
            print(f"  UNEXPECTED: {p}", file=sys.stderr)
            bad = True
    if bad:
        die("diff", f"arms differ outside {' '.join(allowed)}")
    print(f"test-rule-change diff: differ only in: {' '.join(allowed)}")


# summarize: per-run audit line from a kept trace.

def summarize(trace):
    """Tool use of one run. `ungranted`: calls to a tool plugin eval removed
    (no --allow-tools grant): they fail as "No such tool available", not as
    permission denials."""
    s = {"skills": [], "tools": [], "files": [], "bash_writes": [], "denials": [],
         "ungranted": []}
    names = {}
    with open(trace) as f:
        events = [json.loads(line) for line in f if line.strip()]
    for e in events:
        if e.get("type") == "result":
            s["denials"] = [d.get("tool_name") for d in e.get("permission_denials", [])]
        content = e.get("message", {}).get("content")
        if e.get("type") == "user" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_result" and "No such tool available" in str(c.get("content")):
                    s["ungranted"].append(names.get(c.get("tool_use_id"), "?"))
        if e.get("type") != "assistant" or not isinstance(content, list):
            continue
        for c in content:
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


def remove_kept(d):
    """Delete a kept eval dir: only <tempdir>/claude-eval-*, never elsewhere."""
    d = os.path.realpath(d)
    if (os.path.dirname(d) != os.path.realpath(tempfile.gettempdir())
            or not os.path.basename(d).startswith("claude-eval-")):
        return False
    def writable(path):  # chmod u+rwX, so a read-only tree still goes
        if not os.path.islink(path):
            os.chmod(path, os.stat(path).st_mode | (0o700 if os.path.isdir(path) else 0o600))

    writable(d)
    for root, dirs, files in os.walk(d):
        for n in dirs + files:
            writable(os.path.join(root, n))
    shutil.rmtree(d, ignore_errors=True)
    return True


def summary_path(src):
    return re.sub(r"\.json$", "", src) + ".runs.jsonl"


def write_summaries(src):
    """OUT.json -> OUT.runs.jsonl, then delete the kept eval temp dirs."""
    out = summary_path(src)
    if os.path.exists(out):
        die("run", f"{out} exists")
    with open(src) as f:
        res = json.load(f)
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
    removed = sum(remove_kept(d) for d in kept)
    print(f"test-rule-change run: {n} runs -> {out}; {removed} temp dirs removed")


# preflight

def eval_cmd(arm, flags, extra):
    return ["claude", "plugin", "eval", arm, *flags, "--ablation", "none",
            "--trust-plugin", "--no-publish", *extra]


def fail(msg):
    sys.exit(f"test-rule-change preflight: FAIL {msg}")


def ok(msg):
    print(f"test-rule-change preflight: ok   {msg}")


def granted(flags):
    """Tool names after --allow-tools (or --allow-tools=X), up to the next flag."""
    tools, on = [], False
    for f in flags:
        if f.startswith("--allow-tools="):
            tools += f.split("=", 1)[1].split(",")
        elif f.startswith("-"):
            on = f == "--allow-tools"
        elif on:
            tools += f.split(",")
    return [t.strip() for t in tools]


def check_sandbox(flags):
    if not any(t == "Bash" or t.startswith("Bash(") for t in granted(flags)):
        return ok("no Bash grant: sandbox not needed")
    missing = [b for b in ("bwrap", "socat") if not shutil.which(b)]
    if missing:
        fail(f"Bash granted but {', '.join(missing)} missing: plugin eval refuses Bash; "
             "install (Debian/Ubuntu): apt-get update && apt-get install -y bubblewrap socat")
    ok("Bash sandbox backends present")


def scaffold_script(yaml_text):
    """scaffold_script value: quotes stripped, trailing `# comment` dropped."""
    m = re.search(r"^\s*scaffold_script:[ \t]*(.*)$", yaml_text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    q = re.match(r"""(["'])(.*?)\1""", v)
    return q.group(2) if q else re.sub(r"\s+#.*$", "", v).strip() or None


def check_scaffolds(arm):
    n = 0
    for case_yaml in sorted(glob.glob(os.path.join(arm, "evals", "*", "case.yaml"))):
        case_dir = os.path.dirname(case_yaml)
        with open(case_yaml) as f:
            script = scaffold_script(f.read())
        if not script:
            continue
        scaffold = os.path.join(case_dir, script)
        if not os.path.isfile(scaffold):
            fail(f"{os.path.relpath(scaffold, arm)} named in case.yaml does not exist")
        with tempfile.TemporaryDirectory() as ws:
            for step in (scaffold, os.path.join(case_dir, "check.sh")):
                if not os.path.exists(step):
                    continue  # check.sh is optional
                # plugin eval gives a scaffold PATH only: a tool found through
                # another inherited var here would be missing in the run.
                r = subprocess.run(["bash", os.path.abspath(step)], cwd=ws,
                                   env={"PATH": os.environ.get("PATH", "")},
                                   capture_output=True, text=True, stdin=subprocess.DEVNULL)
                if r.returncode:
                    fail(f"{os.path.relpath(step, arm)} exit {r.returncode}: {r.stderr.strip()[-300:]}")
        n += 1
    ok(f"{n} scaffolds green")


def check_load(arm, flags):
    r = subprocess.run(eval_cmd(arm, flags, ["--max-cost-usd", "0"]),
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    warns = [l for l in (r.stdout + r.stderr).splitlines()
             if (l.startswith("⚠") or "not granted" in l) and "cost ceiling $0" not in l]
    if warns:
        fail("load check:\n  " + "\n  ".join(warns[:10]))
    ok("load check: no case warning")


def check_pilot(arm, case, flags):
    name = os.path.basename(os.path.normpath(arm))
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "pilot.json")
        subprocess.run(eval_cmd(arm, flags, ["--case", case, "--runs", "1", "--keep-temp",
                                             "--max-cost-usd", "1", "--json", out]),
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if not os.path.exists(out):
            fail(f"pilot produced no result (case {case!r} exists?)")
        with open(out) as f:
            res = json.load(f)
    runs = [r for c in res["cases"] for r in c["arms"].get("with", [])]
    if not runs:
        fail(f"pilot ran no case named {case!r}")
    run = runs[0]
    if run.get("error"):
        fail(f"pilot run error: {run['error']}")
    trace = run["tracePath"]
    run_root = os.path.dirname(os.path.dirname(trace))
    try:
        with open(trace) as f:
            events = [json.loads(l) for l in f if l.strip()]
        use = summarize(trace)
    finally:
        remove_kept(run_root)

    hook_out = "".join(e.get("output", "") for e in events if e.get("subtype") == "hook_response")
    rules = os.path.join(arm, "hooks", "claude-md.txt")
    if os.path.exists(rules):
        # Whole text: two arms often differ only after the opening lines.
        with open(rules) as f:
            if f.read().strip() not in hook_out:
                fail("arm CLAUDE.md text not in SessionStart hook output, or not whole")
        ok("arm CLAUDE.md reached the session, whole")

    init = next((e for e in events if e.get("subtype") == "init"), None)
    if not init:
        fail("no init event in trace")
    want = {os.path.basename(os.path.dirname(p))
            for p in glob.glob(os.path.join(arm, "skills", "*", "SKILL.md"))}
    have = {s.split(":", 1)[1] for s in init.get("skills", []) if s.startswith(name + ":")}
    if want - have:
        fail(f"arm skills missing from roster: {sorted(want - have)}")
    ok(f"{len(want)} arm skills in roster")
    # The run's own auto-memory dir sits in its temp config: not foreign.
    for key in ("memory_paths", "additional_directories"):
        val = init.get(key) or {}
        paths = val.values() if isinstance(val, dict) else val
        foreign = [p for p in paths if not str(p).startswith(run_root)]
        if foreign:
            fail(f"foreign context loaded ({key}): {foreign}")
    ok("no foreign memory or extra dir")

    if use["denials"]:
        fail(f"permission denials: {use['denials']}")
    ok("no permission denial")
    if use["ungranted"]:
        print(f"test-rule-change preflight: WARN pilot called ungranted tools {sorted(set(use['ungranted']))}: "
              "grant them, or confirm the case does not need them")
    print(f"test-rule-change preflight: pilot cost ${run['costUsd']:.4f}; skills called: {use['skills']}")


def preflight(args):
    if len(args) < 2:
        usage()
    arm, case, flags = args[0], args[1], args[2:]
    for bad in ("--runs", "--case", "--max-cost-usd"):
        if has_flag(flags, bad):
            fail(f"{bad} is set by preflight; pass case flags only")
    check_sandbox(flags)
    check_scaffolds(arm)
    check_load(arm, flags)
    check_pilot(arm, case, flags)
    print("test-rule-change preflight: all checks passed")


# run: fixed flags so every arm of a batch runs alike.

def run(args):
    if len(args) < 2:
        usage()
    arm, out, flags = args[0], args[1], args[2:]
    if not os.path.isdir(os.path.join(arm, ".claude-plugin")):
        die("run", f"{arm} is not a plugin dir")
    for taken in (out, summary_path(out)):
        if os.path.lexists(taken):
            die("run", f"{taken} exists: use a new batch dir")
    if not has_flag(flags, "--max-cost-usd"):
        die("run", "set --max-cost-usd for a paid run")
    if not has_flag(flags, "--ablation"):
        flags += ["--ablation", "none"]  # arm vs arm, compared by `compare`
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    rc = subprocess.run(["claude", "plugin", "eval", arm, *flags, "--keep-temp", "--trust-plugin",
                         "--no-publish", "--json", out], stdin=subprocess.DEVNULL).returncode
    if os.path.exists(out):
        write_summaries(out)
    sys.exit(rc)


# compare

def load(path):
    with open(path) as f:
        d = json.load(f)
    cases = {}
    for c in d["cases"]:
        runs = c["arms"].get("with", [])
        # Denominator = all runs: an errored run (no grader result) is a fail.
        names = {g["name"] for r in runs for g in r.get("graders", [])}
        graders = {g: (sum(any(x["name"] == g and x["passed"] for x in r.get("graders", []))
                           for r in runs), len(runs)) for g in names}
        cases[c["name"]] = {"graders": graders, "runs": runs}
    return os.path.splitext(os.path.basename(path))[0], d, cases


def compare(args):
    """No significance test: read small gaps as noise."""
    if len(args) < 3:
        usage()
    out, paths = args[0], args[1:]
    if os.path.exists(out):
        die("compare", f"{out} exists: write a new file")
    arms = [load(p) for p in paths]
    labels = [a[0] for a in arms]
    dup = sorted({l for l in labels if labels.count(l) > 1})
    if dup:
        die("compare", f"same arm label from two files: {dup}: rename one")
    names = sorted(set().union(*(a[2] for a in arms)))
    missing = [(l, n) for l, _, c in arms for n in names if n not in c]
    if missing:
        die("compare", f"cases missing from an arm: {missing[:5]}")
    versions = {a[1].get("claudeVersion") for a in arms}

    lines = [f"Claude Code {', '.join(sorted(map(str, versions)))}. Cell = passes/runs.", "",
             "| Case | Grader | " + " | ".join(labels) + " |",
             "|---|---|" + "---|" * len(labels)]
    totals = {l: [0, 0] for l in labels}
    for n in names:
        for g in sorted(set().union(*(c[n]["graders"] for _, _, c in arms))):
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
        scores = [r["score"] for r in runs if r.get("score") is not None]
        mean = sum(scores) / len(scores) if scores else 0
        # Denials live in the traces: read `run`'s summary when present.
        summary = summary_path(path)
        denied = "n/a"
        if os.path.exists(summary):
            with open(summary) as f:
                rows = [json.loads(line) for line in f if line.strip()]
            denied = sum(1 for r in rows if r.get("denials") or r.get("ungranted"))
        lines.append(f"| {l} | {len(runs)} | {errs} | {denied} | {mean:.2f} | {d['costUsd']:.2f} |")

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"test-rule-change compare: wrote {out}")


COMMANDS = {"edit": edit, "build": build, "diff": diff, "preflight": preflight,
            "run": run, "compare": compare}


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        sys.exit(0)
    if not argv or argv[0] not in COMMANDS:
        usage()
    COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
