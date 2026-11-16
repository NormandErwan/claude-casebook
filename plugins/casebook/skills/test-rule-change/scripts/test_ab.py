"""Free self-test of ab.py (no model call; `claude` is a stub on PATH).

Run: python3 -m unittest discover -s plugins/casebook/skills/test-rule-change/scripts
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AB = os.path.join(HERE, "ab.py")
sys.path.insert(0, HERE)
import ab  # noqa: E402

# Stub `claude`: logs its args; for `--json OUT` writes a result whose one run
# points at a trace kept in a fake claude-eval-* temp dir. Exit code 3.
STUB = r'''#!/usr/bin/env python3
import json, os, sys, tempfile
log = os.environ["STUB_LOG"]
with open(log, "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
a = sys.argv[1:]
if "--json" in a:
    root = tempfile.mkdtemp(prefix="claude-eval-", dir=os.environ["STUB_TMP"])
    os.makedirs(os.path.join(root, "t"))
    trace = os.path.join(root, "t", "trace.jsonl")
    with open(trace, "w") as f:
        f.write(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "1", "name": "Skill", "input": {"skill": "a:alpha"}}]}}) + "\n")
    with open(a[a.index("--json") + 1], "w") as f:
        json.dump({"claudeVersion": "x", "costUsd": 0.01, "cases": [{"name": "c1", "arms": {
            "with": [{"score": 1.0, "costUsd": 0.01, "error": None, "tracePath": trace}]}}]}, f)
sys.exit(3)
'''


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def read(path):
    with open(path) as f:
        return f.read()


def result(path, fired):
    """Result JSON: case c<j> has 3 runs, the first fired[j] pass `fired`."""
    runs = lambda k: [{"score": float(i < k), "costUsd": .01, "error": None,
                       "graders": [{"name": "fired", "passed": i < k}]} for i in range(3)]
    with open(path, "w") as f:
        json.dump({"claudeVersion": "x", "costUsd": .06, "cases": [
            {"name": f"c{j}", "arms": {"with": runs(k)}} for j, k in enumerate(fired)]}, f)


class AbTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.t, True)
        bin_dir = os.path.join(self.t, "bin")
        write(os.path.join(bin_dir, "claude"), STUB)
        os.chmod(os.path.join(bin_dir, "claude"), 0o755)
        self.log = os.path.join(self.t, "claude.log")
        os.makedirs(os.path.join(self.t, "tmp"))
        self.env = dict(os.environ, PATH=bin_dir + os.pathsep + os.environ.get("PATH", ""),
                        STUB_LOG=self.log, STUB_TMP=os.path.join(self.t, "tmp"))
        write(self.p("skills/alpha/SKILL.md"), "---\nname: alpha\n---\nA\n")
        write(self.p("skills/beta/SKILL.md"), "---\nname: beta\n---\nB\n")
        write(self.p("base.md"), "# Rules\n\n- Reply in French.\n- Reply in French.\n- Be brief.\n")
        write(self.p("evals/c1/case.yaml"), 'schema_version: "1.0"\nname: "c1"\n')

    def p(self, rel):
        return os.path.join(self.t, rel)

    def ab(self, *args):
        return subprocess.run([sys.executable, AB, *args], env=self.env,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def ok(self, *args):
        r = self.ab(*args)
        self.assertEqual(r.returncode, 0, f"{args}: {r.stderr}")
        return r

    def refused(self, *args):
        r = self.ab(*args)
        self.assertNotEqual(r.returncode, 0, f"should fail: {args}")
        return r

    def build(self, name, md="base.md"):
        return self.ok("build", "--out", self.p(name), "--claude-md", self.p(md),
                       "--skills", self.p("skills"), "--evals", self.p("evals"))

    def claude_calls(self):
        if not os.path.exists(self.log):
            return []
        return [json.loads(l) for l in read(self.log).splitlines()]

    # build

    def test_build_layout(self):
        self.build("a-base")
        self.assertTrue(os.path.isfile(self.p("a-base/skills/alpha/SKILL.md")))
        hook = read(self.p("a-base/hooks/claude-md.txt"))
        self.assertEqual(hook, ab.HEADER + read(self.p("base.md")))
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

    # run guards (fail before calling claude)

    def test_run_guards(self):
        self.build("a-base")
        write(self.p("taken.json"), "")
        self.refused("run", self.p("a-base"), self.p("taken.json"), "--max-cost-usd", "1")
        self.refused("run", self.p("a-base"), self.p("free.json"))
        self.refused("run", self.p("skills"), self.p("free.json"), "--max-cost-usd", "1")
        self.assertEqual(self.claude_calls(), [])

    def test_run_flags_summary_cleanup(self):
        self.build("a-base")
        out = self.p("batch/a-base.json")
        r = self.ab("run", self.p("a-base"), out, "--allow-tools", "Write", "Edit",
                    "--max-cost-usd", "2")
        self.assertEqual(r.returncode, 3, r.stderr)  # plugin eval's code
        (args,) = self.claude_calls()
        self.assertEqual(args[:3], ["plugin", "eval", self.p("a-base")])
        self.assertEqual(args[3:], ["--allow-tools", "Write", "Edit", "--max-cost-usd", "2",
                                    "--ablation", "none", "--keep-temp", "--trust-plugin",
                                    "--no-publish", "--json", out])
        (row,) = [json.loads(l) for l in read(self.p("batch/a-base.runs.jsonl")).splitlines()]
        self.assertEqual((row["case"], row["arm"], row["run"], row["skills"]),
                         ("c1", "with", 0, ["a:alpha"]))
        self.assertEqual(os.listdir(self.p("tmp")), [], "kept temp dir not removed")

    def test_run_keeps_given_ablation(self):
        self.build("a-base")
        self.ab("run", self.p("a-base"), self.p("o.json"), "--ablation", "all", "--max-cost-usd", "1")
        (args,) = self.claude_calls()
        self.assertEqual(args.count("--ablation"), 1)

    # preflight guard

    def test_preflight_refuses_set_flags(self):
        self.build("a-base")
        for bad in ("--runs", "--case", "--max-cost-usd"):
            self.refused("preflight", self.p("a-base"), "c1", bad, "1")
        self.assertEqual(self.claude_calls(), [])

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
        s = ab.summarize(f.name)
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
            self.assertTrue(ab.BASH_WRITE.search(c), c)
        for c in reads:
            self.assertFalse(ab.BASH_WRITE.search(c), c)


if __name__ == "__main__":
    unittest.main()
