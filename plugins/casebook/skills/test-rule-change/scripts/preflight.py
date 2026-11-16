#!/usr/bin/env python3
"""Check one arm before any scored run; exit 1 on the first failed check.

usage: preflight.py ARM CASE [plugin eval flags...]
  ARM    arm dir (build-arm.sh); CASE  case name for the 1-run pilot
  flags  the case flags the scored run will use (--model, --scaffold,
         --allow-tools ...); not --runs, --case or --max-cost-usd

Checks, in order (all but the pilot are free):
  1. Bash granted -> the eval sandbox backends (bwrap, socat) exist
  2. each case's scaffold_script runs green in a temp dir, then its
     check.sh if present (fixture ready: deps installed, tests green)
  3. load check (--max-cost-usd 0): no case warning (tool not granted,
     scaffold skipped, bad frontmatter)
  4. pilot, 1 run of CASE: the arm's CLAUDE.md text reached the session,
     every arm skill is in the roster, no foreign memory or extra dir
     loaded, no permission denial; warns on calls to an ungranted tool
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
summarize = __import__("summarize-runs").summarize


def fail(msg):
    sys.exit(f"preflight: FAIL {msg}")


def ok(msg):
    print(f"preflight: ok   {msg}")


def eval_cmd(arm, flags, extra):
    return (["claude", "plugin", "eval", arm, *flags, "--ablation", "none",
             "--trust-plugin", "--no-publish", *extra])


def check_sandbox(flags):
    if "Bash" not in " ".join(flags):
        return ok("no Bash grant: sandbox not needed")
    missing = [b for b in ("bwrap", "socat") if not shutil.which(b)]
    if missing:
        fail(f"Bash granted but {', '.join(missing)} missing: plugin eval refuses Bash")
    ok("Bash sandbox backends present")


def check_scaffolds(arm):
    n = 0
    for case_yaml in sorted(glob.glob(os.path.join(arm, "evals", "*", "case.yaml"))):
        case_dir = os.path.dirname(case_yaml)
        m = re.search(r'scaffold_script:\s*"?([^"\n]+)"?', open(case_yaml).read())
        if not m:
            continue
        with tempfile.TemporaryDirectory() as ws:
            for step in (os.path.join(case_dir, m.group(1)), os.path.join(case_dir, "check.sh")):
                if not os.path.exists(step):
                    continue
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
    out = r.stdout + r.stderr
    warns = [l for l in out.splitlines()
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
        res = json.load(open(out))
        runs = [r for c in res["cases"] for r in c["arms"].get("with", [])]
        if not runs:
            fail(f"pilot ran no case named {case!r}")
        run = runs[0]
        if run.get("error"):
            fail(f"pilot run error: {run['error']}")
        trace = run["tracePath"]
        try:
            events = [json.loads(l) for l in open(trace)]
            use = summarize(trace)
        finally:
            keep = os.path.dirname(os.path.dirname(trace))
            if keep.startswith(tempfile.gettempdir()) and "claude-eval-" in keep:
                subprocess.run(["chmod", "-R", "u+rwX", keep])
                shutil.rmtree(keep, ignore_errors=True)

    hook_out = "".join(e.get("output", "") for e in events if e.get("subtype") == "hook_response")
    rules = os.path.join(arm, "hooks", "claude-md.txt")
    if os.path.exists(rules):
        # Whole text: two arms often differ only after the opening lines.
        if open(rules).read().strip() not in hook_out:
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
    run_root = os.path.dirname(os.path.dirname(trace))
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
        print(f"preflight: WARN pilot called ungranted tools {sorted(set(use['ungranted']))}: "
              "grant them, or confirm the case does not need them")
    print(f"preflight: pilot cost ${run['costUsd']:.4f}; skills called: {use['skills']}")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__.strip())
    arm, case, flags = sys.argv[1], sys.argv[2], sys.argv[3:]
    for bad in ("--runs", "--case", "--max-cost-usd"):
        if bad in flags:
            fail(f"{bad} is set by preflight; pass case flags only")
    check_sandbox(flags)
    check_scaffolds(arm)
    check_load(arm, flags)
    check_pilot(arm, case, flags)
    print("preflight: all checks passed")


if __name__ == "__main__":
    main()
