"""Free self-test of test-rule-change.py (no model call; `claude` is a stub on PATH).

Run: python3 -m unittest discover -s plugins/casebook/skills/test-rule-change/scripts
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "test-rule-change.py")
# Hyphenated name: not importable by `import`.
_spec = importlib.util.spec_from_file_location("test_rule_change", CLI)
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)

# Stub `claude`: logs its args. With `--json OUT` it writes a result whose one
# run points at a trace in a new $TMPDIR/<STUB_PREFIX>* dir; the trace is
# STUB_EVENTS (a file, "@ROOT@" -> that dir) or one Skill call. Otherwise it
# prints STUB_LOAD (the load check). Exits STUB_RC.
STUB = r'''#!PYTHON
import json, os, sys, tempfile
e = os.environ
with open(e["STUB_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
a = sys.argv[1:]
if "--json" in a:
    root = tempfile.mkdtemp(prefix=e.get("STUB_PREFIX", "claude-eval-"))
    os.makedirs(os.path.join(root, "t"))
    trace = os.path.join(root, "t", "trace.jsonl")
    if e.get("STUB_EVENTS"):
        events = open(e["STUB_EVENTS"]).read().replace("@ROOT@", root)
    else:
        events = json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "1", "name": "Skill", "input": {"skill": "a:alpha"}}]}}) + "\n"
    with open(trace, "w") as f:
        f.write(events)
    with open(a[a.index("--json") + 1], "w") as f:
        json.dump({"claudeVersion": "x", "costUsd": 0.01, "cases": [{"name": "c1", "arms": {
            "with": [{"score": 1.0, "costUsd": 0.01, "error": None, "tracePath": trace}]}}]}, f)
else:
    print(e.get("STUB_LOAD", "1 case loaded"))
sys.exit(int(e.get("STUB_RC", "0")))
'''.replace("PYTHON", sys.executable)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def read(path):
    with open(path) as f:
        return f.read()


def result(path, fired, graders=("fired",), score=True):
    """Result JSON: case c<j> has 3 runs, the first fired[j] pass each grader."""
    runs = lambda k: [{"score": float(i < k) if score else None, "costUsd": .01, "error": None,
                       "graders": [{"name": g, "passed": i < k} for g in graders]}
                      for i in range(3)]
    with open(path, "w") as f:
        json.dump({"claudeVersion": "x", "costUsd": .06, "cases": [
            {"name": f"c{j}", "arms": {"with": runs(k)}} for j, k in enumerate(fired)]}, f)


class Base(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.t, True)
        self.bin = os.path.join(self.t, "bin")
        write(os.path.join(self.bin, "claude"), STUB)
        os.chmod(os.path.join(self.bin, "claude"), 0o755)
        self.log = self.p("claude.log")
        self.tmp = self.p("tmp")  # TMPDIR of the CLI and the stub
        os.makedirs(self.tmp)
        # self.tmp may sit under /tmp: CASEBOOK_EVAL_TMPDIR keeps move_tmpdir on it.
        self.env = dict(os.environ, PATH=self.bin + os.pathsep + os.environ.get("PATH", ""),
                        STUB_LOG=self.log, TMPDIR=self.tmp, CASEBOOK_EVAL_TMPDIR=self.tmp)
        write(self.p("skills/alpha/SKILL.md"), "---\nname: alpha\n---\nA\n")
        write(self.p("skills/beta/SKILL.md"), "---\nname: beta\n---\nB\n")
        write(self.p("base.md"), "# Rules\n\n- Reply in French.\n- Reply in French.\n- Be brief.\n")
        write(self.p("evals/c1/case.yaml"), 'schema_version: "1.0"\nname: "c1"\n')

    def p(self, rel):
        return os.path.join(self.t, rel)

    def cli(self, *args, **env):
        return subprocess.run([sys.executable, CLI, *args], env=dict(self.env, **env),
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def ok(self, *args, **env):
        r = self.cli(*args, **env)
        self.assertEqual(r.returncode, 0, f"{args}: {r.stdout}{r.stderr}")
        return r

    def refused(self, *args, **env):
        r = self.cli(*args, **env)
        self.assertNotEqual(r.returncode, 0, f"should fail: {args}: {r.stdout}")
        return r

    def build(self, name, md="base.md"):
        return self.ok("build", "--out", self.p(name), "--claude-md", self.p(md),
                       "--skills", self.p("skills"), "--evals", self.p("evals"))

    def claude_calls(self):
        if not os.path.exists(self.log):
            return []
        return [json.loads(l) for l in read(self.log).splitlines()]


class AbTest(Base):
    def test_help(self):
        for args in (["-h"], ["build", "--help"], ["run", "x", "y", "-h"]):
            r = self.cli(*args)
            self.assertEqual(r.returncode, 0, args)
            self.assertIn("usage:", r.stdout)
        self.assertEqual(self.claude_calls(), [])

    # build

    def test_build_layout(self):
        self.build("a-base")
        self.assertTrue(os.path.isfile(self.p("a-base/skills/alpha/SKILL.md")))
        hook = read(self.p("a-base/hooks/claude-md.txt"))
        self.assertEqual(hook, cli.HEADER + read(self.p("base.md")))
        self.assertIn('"name": "a-base"', read(self.p("a-base/.claude-plugin/plugin.json")))
        hooks = json.loads(read(self.p("a-base/hooks/hooks.json")))
        cmd = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertEqual(cmd, 'cat "${CLAUDE_PLUGIN_ROOT}/hooks/claude-md.txt"')
        self.assertTrue(os.path.isfile(self.p("a-base/evals/c1/case.yaml")))

    def test_build_refuses_existing_out(self):
        self.build("a-base")
        self.refused("build", "--out", self.p("a-base"))

    def test_build_refuses_bad_name(self):
        self.refused("build", "--out", self.p("Bad_Name"))
        self.assertFalse(os.path.exists(self.p("Bad_Name")))

    def test_build_later_skills_win(self):
        write(self.p("skills2/alpha/SKILL.md"), "---\nname: alpha\n---\nA2\n")
        self.ok("build", "--out", self.p("arm"), "--skills", self.p("skills"),
                "--skills", self.p("skills2"))
        self.assertIn("A2", read(self.p("arm/skills/alpha/SKILL.md")))
        self.assertTrue(os.path.isfile(self.p("arm/skills/beta/SKILL.md")))

    # edit: one match edits; 0 or 2 matches refuse and leave the file

    def test_edit(self):
        new = self.p("new.md")
        shutil.copy(self.p("base.md"), new)
        self.refused("edit", new, "- Reply in French.", "- Reply in English.")
        self.refused("edit", new, "absent", "x")
        self.assertEqual(read(new), read(self.p("base.md")), "refused edit changed the file")
        self.ok("edit", new, "- Be brief.", "- Be thorough.")
        self.assertIn("- Be thorough.", read(new))
        self.build("a-new", "new.md")

    def test_edit_at_path(self):
        new = self.p("new.md")
        shutil.copy(self.p("base.md"), new)
        write(self.p("old.txt"), "- Be brief.")
        write(self.p("rep.txt"), "- Be thorough.")
        self.ok("edit", new, "@" + self.p("old.txt"), "@" + self.p("rep.txt"))
        self.assertIn("- Be thorough.", read(new))

    # diff

    def test_diff(self):
        self.build("a-base")
        shutil.copy(self.p("base.md"), self.p("new.md"))
        self.ok("edit", self.p("new.md"), "- Be brief.", "- Be thorough.")
        self.build("a-new", "new.md")
        self.ok("diff", self.p("a-base"), self.p("a-new"), "hooks/claude-md.txt")
        self.refused("diff", self.p("a-base"), self.p("a-new"), "skills")
        shutil.rmtree(self.p("a-new/skills/beta"))
        self.refused("diff", self.p("a-base"), self.p("a-new"), "hooks/claude-md.txt")
        self.ok("diff", self.p("a-base"), self.p("a-new"), "hooks/claude-md.txt", "skills/beta")

    def test_diff_arm_name_prefix(self):
        self.build("a-base")
        shutil.copytree(self.p("a-base"), self.p("a-base-2"))
        write(self.p("a-base-2/extra/g"), "")
        self.ok("diff", self.p("a-base"), self.p("a-base-2"), "extra")

    def test_diff_refuses_identical(self):
        self.build("a-base")
        shutil.copytree(self.p("a-base"), self.p("a-same"))
        self.refused("diff", self.p("a-base"), self.p("a-same"), "hooks")

    def test_diff_ignores_name_and_results(self):
        self.build("a-base")
        self.build("a-other")
        write(self.p("a-other/evals/results/r.json"), "{}")
        r = self.refused("diff", self.p("a-base"), self.p("a-other"), "hooks")
        self.assertIn("identical", r.stderr)

    # run

    def test_run_guards(self):
        self.build("a-base")
        write(self.p("taken.json"), "")
        write(self.p("summed.runs.jsonl"), "")
        self.refused("run", self.p("a-base"), self.p("taken.json"), "--max-cost-usd", "1")
        self.refused("run", self.p("a-base"), self.p("summed.json"), "--max-cost-usd", "1")
        self.refused("run", self.p("a-base"), self.p("free.json"))
        self.refused("run", self.p("skills"), self.p("free.json"), "--max-cost-usd", "1")
        self.assertEqual(self.claude_calls(), [])

    def test_run_flags_summary_cleanup(self):
        self.build("a-base")
        out = self.p("batch/a-base.json")
        r = self.cli("run", self.p("a-base"), out, "--allow-tools", "Write", "Edit",
                    "--max-cost-usd", "2", STUB_RC="3")
        self.assertEqual(r.returncode, 3, r.stderr)  # plugin eval's code
        (args,) = self.claude_calls()
        self.assertEqual(args[:3], ["plugin", "eval", self.p("a-base")])
        self.assertEqual(args[3:], ["--allow-tools", "Write", "Edit", "--max-cost-usd", "2",
                                    "--ablation", "none", "--keep-temp", "--trust-plugin",
                                    "--no-publish", "--json", out])
        (row,) = [json.loads(l) for l in read(self.p("batch/a-base.runs.jsonl")).splitlines()]
        self.assertEqual((row["case"], row["arm"], row["run"], row["skills"]),
                         ("c1", "with", 0, ["a:alpha"]))
        self.assertEqual(os.listdir(self.tmp), [], "kept temp dir not removed")

    def test_run_equals_flags(self):
        self.build("a-base")
        self.ok("run", self.p("a-base"), self.p("o.json"), "--ablation=all", "--max-cost-usd=1")
        (args,) = self.claude_calls()
        self.assertNotIn("--ablation", args)
        self.assertIn("--ablation=all", args)

    def test_run_keeps_non_eval_dir(self):
        self.build("a-base")
        self.ok("run", self.p("a-base"), self.p("o.json"), "--max-cost-usd", "1",
                STUB_PREFIX="keep-")
        (kept,) = os.listdir(self.tmp)
        self.assertTrue(kept.startswith("keep-"))

    # compare

    def test_compare(self):
        result(self.p("old.json"), [1, 3])
        result(self.p("new.json"), [2, 3])
        self.ok("compare", self.p("cmp.md"), self.p("old.json"), self.p("new.json"))
        table = read(self.p("cmp.md"))
        self.assertIn("| c0 | fired | 1/3 | 2/3 |", table)
        self.assertIn("**4/6** | **5/6**", table)
        self.assertIn("| old | 6 | 0 | n/a | 0.67 | 0.06 |", table)
        self.refused("compare", self.p("cmp.md"), self.p("old.json"), self.p("new.json"))
        result(self.p("short.json"), [1])
        self.refused("compare", self.p("cmp2.md"), self.p("old.json"), self.p("short.json"))

    def test_compare_counts_denials(self):
        result(self.p("old.json"), [1])
        result(self.p("new.json"), [1])
        write(self.p("new.runs.jsonl"), "\n".join(json.dumps(r) for r in (
            {"denials": ["Bash"], "ungranted": []}, {"denials": [], "ungranted": ["Bash"]},
            {"denials": [], "ungranted": []})) + "\n")
        self.ok("compare", self.p("cmp.md"), self.p("old.json"), self.p("new.json"))
        self.assertIn("| new | 3 | 0 | 2 |", read(self.p("cmp.md")))

    def test_compare_grader_union_and_none_score(self):
        result(self.p("old.json"), [1])
        result(self.p("new.json"), [2], graders=("fired", "extra"), score=False)
        self.ok("compare", self.p("cmp.md"), self.p("old.json"), self.p("new.json"))
        table = read(self.p("cmp.md"))
        self.assertIn("| c0 | extra | 0/0 | 2/3 |", table)
        self.assertIn("| new | 3 | 0 | n/a | 0.00 |", table)


    def test_compare_refuses_duplicate_label(self):
        os.makedirs(self.p("out1"))
        os.makedirs(self.p("out2"))
        result(self.p("out1/new.json"), [1])
        result(self.p("out2/new.json"), [2])
        r = self.refused("compare", self.p("cmp.md"), self.p("out1/new.json"), self.p("out2/new.json"))
        self.assertIn("same arm label", r.stderr)
        self.assertFalse(os.path.exists(self.p("cmp.md")))

    def test_compare_errored_run_counts_as_fail(self):
        result(self.p("old.json"), [1])
        result(self.p("new.json"), [2])
        d = json.loads(read(self.p("new.json")))
        d["cases"][0]["arms"]["with"][0].update(graders=[], error="boom", score=0.0)
        write(self.p("new.json"), json.dumps(d))
        self.ok("compare", self.p("cmp.md"), self.p("old.json"), self.p("new.json"))
        table = read(self.p("cmp.md"))
        self.assertIn("| c0 | fired | 1/3 | 1/3 |", table)
        self.assertIn("| new | 3 | 1 |", table)

    def test_compare_reads_summary_of_any_result_name(self):
        result(self.p("old.json"), [1])
        result(self.p("new.result"), [1])
        write(self.p("new.result.runs.jsonl"), json.dumps({"denials": ["Bash"]}) + "\n")
        self.ok("compare", self.p("cmp.md"), self.p("old.json"), self.p("new.result"))
        self.assertIn("| new | 3 | 0 | 1 |", read(self.p("cmp.md")))

    def test_skill_md_test_command_from_repo_root(self):
        root = os.path.abspath(os.path.join(HERE, *[".."] * 5))
        rel = os.path.relpath(HERE, root)
        skill = read(os.path.join(HERE, "..", "SKILL.md"))
        self.assertIn(f"python3 -m unittest discover -s {rel}", " ".join(skill.split()))
        self.assertTrue(os.path.isdir(os.path.join(root, ".git")) or os.path.isfile(
            os.path.join(root, "README.md")), root)


class PreflightTest(Base):
    def setUp(self):
        super().setUp()
        self.build("a-base")
        self.arm = self.p("a-base")
        self.rules = read(self.p("a-base/hooks/claude-md.txt"))

    def events(self, hook=None, skills=("alpha", "beta"), memory="@ROOT@/memory",
               denials=(), ungranted=False, readonly=False):
        ev = [{"type": "system", "subtype": "hook_response",
               "output": self.rules if hook is None else hook},
              {"type": "system", "subtype": "init",
               "skills": [f"a-base:{s}" for s in skills] + ["other:x"],
               "memory_paths": {"auto": memory}}]
        if ungranted:
            ev += [{"type": "assistant", "message": {"content": [
                       {"type": "tool_use", "id": "w", "name": "WebFetch", "input": {}}]}},
                   {"type": "user", "message": {"content": [
                       {"type": "tool_result", "tool_use_id": "w",
                        "content": "No such tool available: WebFetch"}]}}]
        if readonly:
            ev.append({"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "b", "is_error": True,
                 "content": "Exit code 1\n/bin/bash: @ROOT@/tmp/cwd-1: Read-only file system"}]}})
        ev.append({"type": "result", "permission_denials": [{"tool_name": d} for d in denials]})
        path = self.p("events.jsonl")
        write(path, "".join(json.dumps(e) + "\n" for e in ev))
        return path

    def preflight(self, *flags, events=None, **env):
        return self.cli("preflight", self.arm, "c1", *flags,
                       STUB_EVENTS=events or self.events(), **env)

    def assert_fails(self, r, text):
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn(text, r.stderr)

    def test_happy_path(self):
        write(self.p("a-base/evals/c1/case.yaml"), 'name: "c1"\nscaffold_script: "setup.sh"\n')
        write(self.p("a-base/evals/c1/setup.sh"), "touch ready\n")
        write(self.p("a-base/evals/c1/check.sh"), "test -f ready\n")
        r = self.preflight("--model", "m", STUB_LOAD="⚠ cost ceiling $0: no run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("1 scaffolds green", r.stdout)
        self.assertIn("all checks passed", r.stdout)
        load, pilot = self.claude_calls()
        self.assertIn("--max-cost-usd", load)
        self.assertEqual(pilot[pilot.index("--case") + 1], "c1")
        self.assertIn("--keep-temp", pilot)
        self.assertEqual(os.listdir(self.tmp), [], "kept temp dir not removed")

    def test_refuses_set_flags(self):
        for bad in ("--runs", "--case", "--max-cost-usd", "--runs=3"):
            self.refused("preflight", self.arm, "c1", bad, "1")
        self.assertEqual(self.claude_calls(), [])

    def test_bash_without_sandbox(self):
        r = self.preflight("--allow-tools", "Bash", PATH=self.bin)
        self.assert_fails(r, "apt-get install -y bubblewrap socat")
        self.assertEqual(self.claude_calls(), [])

    def test_red_scaffold(self):
        write(self.p("a-base/evals/c1/case.yaml"), 'name: "c1"\nscaffold_script: "setup.sh"\n')
        write(self.p("a-base/evals/c1/setup.sh"), "echo broken >&2; exit 4\n")
        self.assert_fails(self.preflight(), "setup.sh exit 4: broken")

    def test_load_warning(self):
        self.assert_fails(self.preflight(STUB_LOAD="⚠ c1: tool Bash not granted"), "load check")

    def test_claude_md_not_whole(self):
        r = self.preflight(events=self.events(hook=self.rules.splitlines()[0]))
        self.assert_fails(r, "not in SessionStart hook output")

    def test_skill_missing(self):
        self.assert_fails(self.preflight(events=self.events(skills=["alpha"])), "['beta']")

    def test_foreign_memory(self):
        r = self.preflight(events=self.events(memory="/home/someone/.claude/memory"))
        self.assert_fails(r, "foreign context loaded (memory_paths)")

    def test_permission_denial(self):
        self.assert_fails(self.preflight(events=self.events(denials=["Edit"])),
                          "permission denials: ['Edit']")

    def test_readonly_workspace(self):
        # anthropics/claude-code#104631: the run is scored, not errored.
        self.assert_fails(self.preflight(events=self.events(readonly=True)),
                          "pilot hit 'Read-only file system'")

    def test_ungranted_warns(self):
        r = self.preflight(events=self.events(ungranted=True))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("WARN pilot called ungranted tools ['WebFetch']", r.stdout)


    def test_missing_scaffold_script(self):
        write(self.p("a-base/evals/c1/case.yaml"),
              'name: "c1"\nscaffold_script: setup.sh  # builds the fixture\n')
        self.assert_fails(self.preflight(), "setup.sh named in case.yaml does not exist")
        self.assertEqual(self.claude_calls(), [])

    def test_bash_grant_by_token(self):
        # "Bash" outside an --allow-tools value is no grant: no sandbox needed.
        r = self.preflight("--allow-tools", "BashOutput", "--model", "Bash", PATH=self.bin)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("no Bash grant", r.stdout)
        r = self.preflight("--allow-tools", "Write", "Bash(git:*)", PATH=self.bin)
        self.assert_fails(r, "Bash granted")


class SummarizeTest(unittest.TestCase):
    def test_trace(self):
        events = [
            {"type": "system", "subtype": "init", "skills": ["a:alpha"]},
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "hi"},
                {"type": "tool_use", "id": "t1", "name": "Skill", "input": {"skill": "a:alpha"}},
                {"type": "tool_use", "id": "t2", "name": "Write", "input": {"file_path": "/w/a.md"}},
                {"type": "tool_use", "id": "t3", "name": "Bash", "input": {"command": "echo x > b.md"}},
                {"type": "tool_use", "id": "t4", "name": "Bash", "input": {"command": "ls 2>&1"}},
                {"type": "tool_use", "id": "t5", "name": "WebFetch", "input": {"url": "u"}},
            ]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "t5",
                 "content": "<tool_use_error>Error: No such tool available: WebFetch</tool_use_error>"},
            ]}},
            {"type": "result", "permission_denials": [{"tool_name": "Edit", "tool_input": {}}]},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write("".join(json.dumps(e) + "\n" for e in events))
        self.addCleanup(os.remove, f.name)
        s = cli.summarize(f.name)
        self.assertEqual(s["skills"], ["a:alpha"])
        self.assertEqual(s["tools"], ["Skill", "Write", "Bash", "Bash", "WebFetch"])
        self.assertEqual(s["files"], ["/w/a.md"])
        self.assertEqual(s["bash_writes"], ["echo x > b.md"])
        self.assertEqual(s["ungranted"], ["WebFetch"])
        self.assertEqual(s["denials"], ["Edit"])

    def test_bash_write_pattern(self):
        writes = ["a >> f", "sed -i s/a/b/ f", "x | tee f", "mv a b", "cp a b"]
        reads = ["ls 2>&1", "cat f", "grep -n x f"]
        for c in writes:
            self.assertTrue(cli.BASH_WRITE.search(c), c)
        for c in reads:
            self.assertFalse(cli.BASH_WRITE.search(c), c)

    def test_scaffold_script_parse(self):
        cases = {'scaffold_script: setup.sh\n': "setup.sh",
                 'scaffold_script: "s p.sh"  # quoted\n': "s p.sh",
                 "scaffold_script: 'a#b.sh'\n": "a#b.sh",
                 'scaffold_script: setup.sh   # comment\n': "setup.sh",
                 'name: x\n': None}
        for text, want in cases.items():
            self.assertEqual(cli.scaffold_script(text), want, text)

    def test_granted(self):
        self.assertEqual(cli.granted(["--model", "m", "--allow-tools", "Write", "Bash", "--runs", "3"]),
                         ["Write", "Bash"])
        self.assertEqual(cli.granted(["--allow-tools=Read,Bash(git:*)"]), ["Read", "Bash(git:*)"])
        self.assertEqual(cli.granted(["--model", "Bash"]), [])

    def move_tmpdir(self, tmpdir, **env):
        """move_tmpdir() in-process from TMPDIR=tmpdir; returns the TMPDIR it leaves."""
        saved = dict(os.environ)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(saved),
                                 setattr(tempfile, "tempdir", None)))
        os.environ.pop("CASEBOOK_EVAL_TMPDIR", None)
        os.environ.update(TMPDIR=tmpdir, **env)
        tempfile.tempdir = None
        cli.move_tmpdir()
        self.assertEqual(tempfile.gettempdir(), os.environ["TMPDIR"])
        return os.environ["TMPDIR"]

    def test_move_tmpdir_leaves_tmp(self):
        # Under /tmp: the sandbox's //tmp write deny would make the run read-only.
        t = tempfile.mkdtemp(dir="/tmp")
        self.addCleanup(shutil.rmtree, t, True)
        moved = self.move_tmpdir(t, XDG_CACHE_HOME=os.path.join(t, "cache"))
        self.assertEqual(moved, os.path.realpath(os.path.join(t, "cache", "claude-eval-tmp")))
        self.assertTrue(os.path.isdir(moved))
        self.assertEqual(self.move_tmpdir(t, CASEBOOK_EVAL_TMPDIR=os.path.join(t, "x")),
                         os.path.realpath(os.path.join(t, "x")))

    def test_move_tmpdir_keeps_tmpdir_outside_tmp(self):
        here = os.path.realpath(HERE)
        self.assertEqual(self.move_tmpdir(here), here)

    def test_remove_kept_only_eval_dirs_in_tempdir(self):
        tmp = tempfile.gettempdir()
        eval_dir = tempfile.mkdtemp(prefix="claude-eval-")
        nested = tempfile.mkdtemp()
        inner = os.path.join(nested, "claude-eval-x")
        other = tempfile.mkdtemp(prefix="keep-")
        os.makedirs(inner)
        os.makedirs(os.path.join(eval_dir, "ro"))
        write(os.path.join(eval_dir, "ro", "f"), "x")
        os.chmod(os.path.join(eval_dir, "ro"), 0o500)  # read-only tree still removed
        self.addCleanup(shutil.rmtree, nested, True)
        self.addCleanup(shutil.rmtree, other, True)
        self.assertTrue(cli.remove_kept(os.path.join(tmp, os.path.basename(eval_dir))))
        self.assertFalse(os.path.exists(eval_dir))
        self.assertFalse(cli.remove_kept(inner))
        self.assertFalse(cli.remove_kept(other))
        self.assertTrue(os.path.isdir(inner) and os.path.isdir(other))


if __name__ == "__main__":
    unittest.main()
