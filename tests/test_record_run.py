import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tests import _paths

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

HAVE_GIT = shutil.which("git") is not None
SCRIPT = _paths.STUDY_SCRIPTS / "record_run.py"
SYSTEM_PYTHON = "/usr/bin/python3"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Project(unittest.TestCase):
    """A scratch project with a few files, and a helper that runs record_run.py in it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve() / "proj"
        self.root.mkdir()
        self.write("configs/main.yml", "grid: 0.5\n")
        self.write("inputs/weather/a.epw", "weather A\n")
        self.write("inputs/weather/b.epw", "weather B\n")
        self.write("code/run_all.py", "print('run')\n")
        self.write("results/annual.csv", "x,y\n1,2\n")
        self.runs = self.root / ".paper" / "runs.yml"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))
        return p

    def record(self, *extra, base=None, cwd=None):
        args = ["--paper", ".paper", "--id", "R3", "--kind", "production",
                "--purpose", "production run, 0.5 m grid", "--command", "python code/run_all.py",
                "--inputs", "configs/main.yml", "--code", "code", "--outputs", "results/annual.csv",
                "--tool", "Radiance=5.4a"] if base is None else list(base)
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args, *extra],
                              cwd=str(cwd or self.root), capture_output=True, text=True)

    def load(self):
        return yaml.safe_load(self.runs.read_text(encoding="utf-8"))


class TestCreateFile(Project):
    def test_creates_runs_yml_and_paper_folder(self):
        r = self.record()
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.runs.read_text(encoding="utf-8")
        self.assertIn("version: 1\n", text)
        self.assertIn(f'updated: "{date.today().isoformat()}"', text)
        self.assertIn("\nruns:\n", text)

    def test_prints_one_line_with_id_file_count_and_no_version_control(self):
        r = self.record()
        lines = r.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("R3", lines[0])
        self.assertIn("3 files hashed", lines[0])   # 1 input + 1 code + 1 output
        self.assertIn("no version control", lines[0])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_row_parses_into_the_structure_of_study_memory(self):
        self.record("--seed", "7")
        data = self.load()
        self.assertEqual(data["version"], 1)
        row = data["runs"][0]
        self.assertEqual(row["id"], "R3")
        self.assertEqual(row["kind"], "production")
        self.assertEqual(row["status"], "valid")
        self.assertEqual(row["seed"], 7)
        self.assertEqual(row["tools"], [{"name": "Radiance", "version": "5.4a"}])
        self.assertEqual(row["code"]["files"][0]["path"], "code/run_all.py")
        self.assertEqual(row["inputs"][0]["path"], "configs/main.yml")
        self.assertEqual(row["outputs"][0]["path"], "results/annual.csv")
        self.assertEqual(row["date"], date.today().isoformat())

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_hashes_are_sha256_of_the_file_bytes(self):
        self.record()
        row = self.load()["runs"][0]
        self.assertEqual(row["inputs"][0]["sha256"], sha(b"grid: 0.5\n"))
        self.assertEqual(row["outputs"][0]["sha256"], sha(b"x,y\n1,2\n"))
        self.assertEqual(row["code"]["files"][0]["sha256"], sha(b"print('run')\n"))

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_seed_defaults_to_null_and_date_can_be_given(self):
        self.record("--date", "2026-08-12")
        row = self.load()["runs"][0]
        self.assertIsNone(row["seed"])
        self.assertEqual(row["date"], "2026-08-12")

    def test_invalid_date_is_refused(self):
        r = self.record("--date", "12/08/2026")
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.runs.exists())

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_strings_with_quotes_and_colons_survive_as_double_quoted_scalars(self):
        r = self.record(base=["--paper", ".paper", "--id", "R3", "--kind", "pilot",
                              "--purpose", 'say "hi": # not a comment', "--command", "a: b",
                              "--inputs", "configs/main.yml", "--outputs", "results/annual.csv",
                              "--tool", "T=1: \"x\""])
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.load()["runs"][0]
        self.assertEqual(row["purpose"], 'say "hi": # not a comment')
        self.assertEqual(row["tools"][0]["version"], '1: "x"')


class TestPaths(Project):
    def test_directory_expands_to_sorted_files_skipping_junk(self):
        for rel in ("code/.git/config", "code/__pycache__/x.pyc", "code/node_modules/m.js",
                    "code/.venv/pyvenv.cfg", "code/venv/pyvenv.cfg", "code/.DS_Store",
                    "code/.paper/x", "code/sub/b.py", "code/sub/a.py"):
            self.write(rel, "x")
        self.record()
        text = self.runs.read_text(encoding="utf-8")
        paths = [ln.split('"')[1] for ln in text.splitlines() if ln.strip().startswith("- path:")]
        code = [p for p in paths if p.startswith("code/")]
        self.assertEqual(code, ["code/run_all.py", "code/sub/a.py", "code/sub/b.py"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_paths_are_stored_relative_to_the_project_root_from_a_subfolder(self):
        base = ["--paper", "../.paper", "--id", "R3", "--kind", "check", "--purpose", "p",
                "--command", "c", "--inputs", "../configs/main.yml",
                "--outputs", str(self.root / "results" / "annual.csv")]
        (self.root / "work").mkdir()
        r = self.record(base=base, cwd=self.root / "work")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.load()["runs"][0]
        self.assertEqual(row["inputs"][0]["path"], "configs/main.yml")
        self.assertEqual(row["outputs"][0]["path"], "results/annual.csv")

    def test_missing_path_is_refused_and_nothing_is_written(self):
        r = self.record("--inputs", "nope.txt")
        self.assertEqual(r.returncode, 2)
        self.assertIn("nope.txt", r.stderr)
        self.assertFalse(self.runs.exists())

    def test_path_outside_the_project_is_refused(self):
        outside = Path(self.tmp.name) / "outside.txt"
        outside.write_text("x")
        r = self.record("--inputs", str(outside))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.runs.exists())


class TestStatusAndKind(Project):
    def test_kind_outside_the_list_is_refused(self):
        r = self.record(base=["--paper", ".paper", "--id", "R3", "--kind", "final", "--purpose", "p",
                              "--command", "c", "--outputs", "results/annual.csv"])
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.runs.exists())

    def test_kind_is_required(self):
        r = self.record(base=["--paper", ".paper", "--id", "R3", "--purpose", "p", "--command", "c",
                              "--outputs", "results/annual.csv"])
        self.assertEqual(r.returncode, 2)

    def test_status_outside_the_list_is_refused(self):
        self.assertEqual(self.record("--status", "done").returncode, 2)

    def test_failed_excluded_superseded_each_require_a_reason(self):
        for status in ("failed", "excluded", "superseded"):
            extra = ["--status", status] + (["--superseded-by", "R9"] if status == "superseded" else [])
            r = self.record(*extra)
            self.assertEqual(r.returncode, 2, status)
            self.assertIn("--reason", r.stderr)
        self.assertFalse(self.runs.exists())

    def test_superseded_requires_superseded_by(self):
        r = self.record("--status", "superseded", "--reason", "replaced")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--superseded-by", r.stderr)

    def test_superseded_by_with_another_status_is_refused(self):
        self.assertEqual(self.record("--superseded-by", "R9").returncode, 2)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_superseded_row_carries_superseded_by_and_reason(self):
        r = self.record("--status", "superseded", "--superseded-by", "R9", "--reason", "grid changed")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.load()["runs"][0]
        self.assertEqual((row["status"], row["superseded_by"], row["reason"]),
                         ("superseded", "R9", "grid changed"))

    def test_failed_run_may_omit_outputs(self):
        base = ["--paper", ".paper", "--id", "R4", "--kind", "pilot", "--purpose", "p",
                "--command", "c", "--inputs", "configs/main.yml"]
        r = self.record("--status", "failed", "--reason", "crashed", base=base)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("outputs: []", self.runs.read_text(encoding="utf-8"))

    def test_valid_run_without_outputs_is_refused(self):
        base = ["--paper", ".paper", "--id", "R4", "--kind", "pilot", "--purpose", "p",
                "--command", "c", "--inputs", "configs/main.yml"]
        r = self.record(base=base)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--outputs", r.stderr)


class TestTools(Project):
    def test_tool_with_empty_version_is_refused(self):
        r = self.record("--tool", "Python=")
        self.assertEqual(r.returncode, 2)
        self.assertIn("version", r.stderr)
        self.assertFalse(self.runs.exists())

    def test_tool_without_equals_is_refused(self):
        self.assertEqual(self.record("--tool", "Python").returncode, 2)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_tool_may_repeat_and_version_keeps_later_equals_signs(self):
        self.record("--tool", "Python=3.12.4", "--tool", "X=a=b")
        names = [(t["name"], t["version"]) for t in self.load()["runs"][0]["tools"]]
        self.assertEqual(names, [("Radiance", "5.4a"), ("Python", "3.12.4"), ("X", "a=b")])


class TestAppend(Project):
    EXISTING = ('# my notes\nversion: 1\nupdated: "2026-01-01"   \n\nruns:\n'
                '  - id: R1\n    date: "2026-01-01"   # keep\n    kind: pilot\n    status: valid\n')

    def seed(self, text):
        self.runs.parent.mkdir(exist_ok=True)
        self.runs.write_bytes(text.encode("utf-8"))

    def test_existing_text_is_kept_byte_for_byte_except_updated(self):
        self.seed(self.EXISTING)
        r = self.record()
        self.assertEqual(r.returncode, 0, r.stderr)
        new = self.runs.read_text(encoding="utf-8")
        today = f'updated: "{date.today().isoformat()}"'
        self.assertTrue(new.startswith(self.EXISTING.replace('updated: "2026-01-01"   ', today)))
        self.assertTrue(new.endswith("\n"))
        self.assertIn("  - id: \"R3\"\n", new)

    def test_crlf_file_keeps_its_lines(self):
        self.seed(self.EXISTING.replace("\n", "\r\n"))
        self.record()
        raw = self.runs.read_bytes()
        self.assertIn(b'# my notes\r\nversion: 1\r\n', raw)

    def test_file_without_final_newline_gets_one_before_the_new_row(self):
        self.seed(self.EXISTING.rstrip("\n"))
        self.record()
        self.assertIn("status: valid\n  - id: \"R3\"", self.runs.read_text(encoding="utf-8"))

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_appended_file_still_parses_with_both_rows(self):
        self.seed(self.EXISTING)
        self.record()
        self.assertEqual([r["id"] for r in self.load()["runs"]], ["R1", "R3"])

    def test_duplicate_id_is_refused_and_file_unchanged(self):
        self.seed(self.EXISTING)
        before = self.runs.read_bytes()
        r = self.record("--id", "R1")
        self.assertEqual(r.returncode, 2)
        self.assertIn("R1", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_quoted_existing_id_is_also_a_duplicate(self):
        self.seed(self.EXISTING.replace("id: R1", 'id: "R1"'))
        before = self.runs.read_bytes()
        self.assertEqual(self.record("--id", "R1").returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_runs_not_last_key_is_refused_and_file_unchanged(self):
        self.seed(self.EXISTING + 'notes: "later"\n')
        before = self.runs.read_bytes()
        r = self.record()
        self.assertEqual(r.returncode, 2)
        self.assertIn("last", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_file_without_runs_key_is_refused(self):
        self.seed('version: 1\nupdated: "2026-01-01"\n')
        before = self.runs.read_bytes()
        self.assertEqual(self.record().returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_missing_path_leaves_existing_file_unchanged(self):
        self.seed(self.EXISTING)
        before = self.runs.read_bytes()
        self.assertEqual(self.record("--outputs", "gone.csv").returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_empty_inline_runs_list_is_accepted(self):
        self.seed('version: 1\nupdated: "2026-01-01"\nruns: []\n')
        self.assertEqual(self.record().returncode, 0)
        if HAVE_YAML:
            self.assertEqual(self.load()["runs"][0]["id"], "R3")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)


@unittest.skipUnless(HAVE_GIT, "git not installed")
class TestGit(Project):
    def setUp(self):
        super().setUp()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.com")
        git(self.root, "config", "commit.gpgsign", "false")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "init")
        self.head = git(self.root, "rev-parse", "HEAD").stdout.strip()

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_clean_tree_records_head_commit_and_dirty_false(self):
        r = self.record()
        code = self.load()["runs"][0]["code"]
        self.assertEqual(code["commit"], self.head)
        self.assertIs(code["dirty"], False)
        self.assertIn(self.head[:7], r.stdout)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_uncommitted_change_in_code_folder_is_dirty(self):
        self.write("code/run_all.py", "print('changed')\n")
        self.record()
        self.assertIs(self.load()["runs"][0]["code"]["dirty"], True)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_untracked_file_in_code_folder_is_dirty(self):
        self.write("code/new.py", "x\n")
        self.record()
        self.assertIs(self.load()["runs"][0]["code"]["dirty"], True)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_change_outside_the_code_paths_does_not_make_it_dirty(self):
        self.write("results/annual.csv", "x,y\n9,9\n")
        self.record()
        self.assertIs(self.load()["runs"][0]["code"]["dirty"], False)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_repository_with_no_commit_gives_null_commit_and_dirty(self):
        shutil.rmtree(self.root / ".git")
        git(self.root, "init", "-q")
        self.record()
        code = self.load()["runs"][0]["code"]
        self.assertIsNone(code["commit"])
        self.assertIsNone(code["dirty"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_without_git_on_path_commit_and_dirty_are_null(self):
        env = {k: v for k, v in os.environ.items() if k != "PATH"}
        env["PATH"] = str(Path(self.tmp.name))   # an empty folder: no git
        args = ["--paper", ".paper", "--id", "R3", "--kind", "check", "--purpose", "p",
                "--command", "c", "--outputs", "results/annual.csv", "--code", "code"]
        r = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=str(self.root),
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        code = self.load()["runs"][0]["code"]
        self.assertIsNone(code["commit"])
        self.assertIsNone(code["dirty"])
        self.assertIn("no version control", r.stdout)


@unittest.skipUnless(os.path.exists(SYSTEM_PYTHON), "no /usr/bin/python3")
class TestSystemPython(unittest.TestCase):
    def test_compiles_and_shows_help_on_system_python(self):
        r = subprocess.run([SYSTEM_PYTHON, "-B", "-c",
                            "import sys; compile(open(sys.argv[1]).read(), sys.argv[1], 'exec')",
                            str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = subprocess.run([SYSTEM_PYTHON, "-B", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--paper", r.stdout)


class TestScriptFile(unittest.TestCase):
    def test_is_executable_with_env_shebang_and_docstring(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("#!/usr/bin/env python3\n"))
        self.assertIn("manuscript", text.split('"""')[1])
        self.assertIn("Exit code", text.split('"""')[1])


# ---- review findings R1 to R9 and regression cases -------------------------------------------

import record_run  # noqa: E402  (path set by tests._paths)

EXISTING_RUNS = ('version: 1\nupdated: "2026-01-01"\n\nruns:\n'
                 '  - id: R1\n    date: "2026-01-01"\n    kind: pilot\n    status: valid\n')


class Seeded(Project):
    def seed(self, text=EXISTING_RUNS, raw=None):
        self.runs.parent.mkdir(exist_ok=True)
        self.runs.write_bytes(raw if raw is not None else text.encode("utf-8"))
        return self.runs.read_bytes()

    def ids(self):
        return [r["id"] for r in self.load()["runs"]]


class TestR1AtomicWrite(Seeded):
    def test_unencodable_text_is_refused_and_the_file_is_unchanged(self):
        before = self.seed()
        r = self.record("--purpose", "bad \udcff byte")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_unencodable_text_creates_no_file_and_leaves_no_temporary_file(self):
        r = self.record("--purpose", "bad \udcff byte")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertFalse(self.runs.exists())
        self.assertEqual(list((self.root / ".paper").glob("*")) if (self.root / ".paper").exists() else [], [])

    def test_failure_while_writing_leaves_the_file_unchanged(self):
        before = self.seed()
        real = os.fsync
        os.fsync = lambda fd: (_ for _ in ()).throw(OSError(28, "No space left on device"))
        try:
            rc = record_run.main(["--paper", str(self.root / ".paper"), "--id", "R3", "--kind", "check",
                                  "--purpose", "p", "--command", "c", "--outputs",
                                  str(self.root / "results/annual.csv")])
        finally:
            os.fsync = real
        self.assertEqual(rc, 2)
        self.assertEqual(self.runs.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.runs.parent.iterdir()), ["runs.yml"])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestR2Escaping(unittest.TestCase):
    def test_every_class_of_special_character_reads_back_as_itself(self):
        chars = [chr(c) for c in range(0, 0x20)] + [chr(c) for c in range(0x7f, 0xa0)]
        chars += [" ", " ", "￾", "￿", "﻿", '"', "\\", "é", "\U0001F600"]
        for ch in chars:
            with self.subTest(char=hex(ord(ch))):
                text = "a" + ch + "b"
                self.assertEqual(yaml.safe_load("k: " + record_run.q(text))["k"], text)

    def test_a_lone_surrogate_is_refused(self):
        with self.assertRaises(record_run.Refused):
            record_run.q("a\ud800b")

    def test_del_and_nel_in_purpose_survive_a_real_run(self):
        p = Project()
        p.setUp()
        try:
            r = p.record("--purpose", "a\x7fb\x85c d")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(p.load()["runs"][0]["purpose"], "a\x7fb\x85c d")
        finally:
            p.tearDown()


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestR3Indent(Seeded):
    def check(self, text):
        self.seed(text)
        r = self.record()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.ids(), ["R0", "R3"])

    def test_list_items_at_indent_0(self):
        self.check('version: 1\nruns:\n- id: R0\n  status: valid\n')

    def test_list_items_at_indent_4(self):
        self.check('version: 1\nruns:\n    - id: R0\n      status: valid\n')

    def test_mixed_indents_are_refused_and_unchanged(self):
        before = self.seed('version: 1\nruns:\n  - id: R0\n    status: valid\n- id: R1\n  status: valid\n')
        r = self.record()
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestR4SafetyNet(Seeded):
    def test_an_append_that_would_break_the_file_is_refused(self):
        before = self.seed(EXISTING_RUNS + "...\n")
        r = self.record()
        self.assertEqual(r.returncode, 2)
        self.assertIn("refused", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_an_existing_file_that_does_not_parse_is_refused(self):
        before = self.seed('version: 1\nruns:\n  - id: "R0\n')
        self.assertEqual(self.record().returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    @unittest.skipUnless(os.path.exists(SYSTEM_PYTHON), "no /usr/bin/python3")
    def test_without_pyyaml_the_check_is_skipped_silently(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        Path(d.name, "yaml.py").write_text("raise ImportError('blocked')\n")
        self.seed()
        r = subprocess.run([sys.executable, "-B", str(SCRIPT), "--paper", ".paper", "--id", "R3",
                            "--kind", "check", "--purpose", "p", "--command", "c",
                            "--outputs", "results/annual.csv"], cwd=str(self.root),
                           capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=d.name))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr, "")
        self.assertEqual(self.ids(), ["R1", "R3"])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestR5Lock(Seeded):
    def test_parallel_invocations_all_land(self):
        self.seed()
        base = ["--paper", ".paper", "--kind", "check", "--purpose", "p", "--command", "c",
                "--inputs", "inputs", "--outputs", "results/annual.csv"]
        procs = [subprocess.Popen([sys.executable, "-B", str(SCRIPT), "--id", f"P{i}", *base],
                                  cwd=str(self.root), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                 for i in range(8)]
        codes = [p.wait() for p in procs]
        for p in procs:
            p.stdout.close()
            p.stderr.close()
        self.assertEqual(codes, [0] * 8)
        self.assertEqual(sorted(self.ids()), sorted(["R1"] + [f"P{i}" for i in range(8)]))
        self.assertFalse((self.runs.parent / "runs.yml.lock").exists())

    def test_fallback_lock_file_is_refused_when_it_cannot_be_taken(self):
        self.seed()
        before = self.runs.read_bytes()
        (self.runs.parent / "runs.yml.lock").write_text("held")
        saved = (record_run.fcntl, record_run.LOCK_WAIT)
        record_run.fcntl, record_run.LOCK_WAIT = None, 0.3
        try:
            rc = record_run.main(["--paper", str(self.root / ".paper"), "--id", "R3", "--kind", "check",
                                  "--purpose", "p", "--command", "c", "--outputs",
                                  str(self.root / "results/annual.csv")])
        finally:
            record_run.fcntl, record_run.LOCK_WAIT = saved
        self.assertEqual(rc, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_fallback_lock_is_removed_after_a_successful_write(self):
        self.seed()
        saved = record_run.fcntl
        record_run.fcntl = None
        try:
            rc = record_run.main(["--paper", str(self.root / ".paper"), "--id", "R3", "--kind", "check",
                                  "--purpose", "p", "--command", "c", "--outputs",
                                  str(self.root / "results/annual.csv")])
        finally:
            record_run.fcntl = saved
        self.assertEqual(rc, 0)
        self.assertFalse((self.runs.parent / "runs.yml.lock").exists())


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestR6Seed(Project):
    def test_leading_zero_seed_stays_a_string_and_plain_integers_stay_integers(self):
        for given, want in (("007", "007"), ("010", "010"), ("-0", "-0"), ("7", 7), ("-12", -12), ("0", 0),
                            ("1e3", "1e3"), ("abc", "abc")):
            with self.subTest(seed=given):
                self.runs.unlink() if self.runs.exists() else None
                self.assertEqual(self.record("--seed", given).returncode, 0)
                self.assertEqual(self.load()["runs"][0]["seed"], want)


class TestR7Symlinks(Seeded):
    def test_symlinked_directory_is_warned_about_and_not_followed(self):
        (self.root / "elsewhere").mkdir()
        (self.root / "elsewhere" / "x.txt").write_text("x")
        os.symlink(self.root / "elsewhere", self.root / "inputs" / "link_dir")
        r = self.record("--inputs", "inputs")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("warning", r.stderr)
        self.assertIn("link_dir", r.stderr)
        self.assertNotIn("x.txt", self.runs.read_text(encoding="utf-8"))

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_symlinked_file_is_hashed_through_the_target_with_a_warning(self):
        (self.root / "elsewhere").mkdir()
        (self.root / "elsewhere" / "t.txt").write_bytes(b"target\n")
        os.symlink(self.root / "elsewhere" / "t.txt", self.root / "inputs" / "link.txt")
        r = self.record("--inputs", "inputs")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("warning", r.stderr)
        self.assertIn("link.txt", r.stderr)
        got = {i["path"]: i["sha256"] for i in self.load()["runs"][0]["inputs"]}
        self.assertEqual(got["inputs/link.txt"], sha(b"target\n"))

    def test_unreadable_file_is_a_refusal_not_a_traceback(self):
        if os.geteuid() == 0:
            self.skipTest("root can read everything")
        before = self.seed()
        p = self.root / "inputs" / "weather" / "a.epw"
        p.chmod(0)
        try:
            r = self.record("--inputs", "inputs")
        finally:
            p.chmod(0o644)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_broken_symlink_is_a_refusal(self):
        os.symlink(self.root / "nowhere", self.root / "inputs" / "dead")
        r = self.record("--inputs", "inputs")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)


class TestR8PaperFolder(Seeded):
    def test_paper_folder_must_be_named_dot_paper(self):
        r = self.record(base=["--paper", "notes", "--id", "R3", "--kind", "check", "--purpose", "p",
                              "--command", "c", "--outputs", "results/annual.csv"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("notes", r.stderr)
        self.assertFalse((self.root / "notes").exists())

    def test_missing_parent_folder_is_a_refusal(self):
        r = self.record(base=["--paper", str(self.root / "nope" / ".paper"), "--id", "R3", "--kind", "failed"
                              if False else "check", "--purpose", "p", "--command", "c",
                              "--status", "failed", "--reason", "x"])
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)

    def test_runs_yml_that_is_a_directory_is_a_refusal(self):
        (self.root / ".paper" / "runs.yml").mkdir(parents=True)
        r = self.record()
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)

    def test_empty_folder_in_inputs_gives_a_warning(self):
        (self.root / "empty").mkdir()
        r = self.record("--inputs", "empty")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("warning", r.stderr)
        self.assertIn("empty", r.stderr)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestR9DuplicateIds(Seeded):
    FLOW = 'version: 1\nruns:\n  - {id: R1, status: valid}\n'

    def test_flow_style_existing_row_is_seen_as_a_duplicate(self):
        before = self.seed(self.FLOW)
        r = self.record("--id", "R1")
        self.assertEqual(r.returncode, 2)
        self.assertIn("R1", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_without_pyyaml_an_unrecognised_row_shape_is_refused(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        Path(d.name, "yaml.py").write_text("raise ImportError('blocked')\n")
        before = self.seed(self.FLOW)
        r = subprocess.run([sys.executable, "-B", str(SCRIPT), "--paper", ".paper", "--id", "R9",
                            "--kind", "check", "--purpose", "p", "--command", "c",
                            "--outputs", "results/annual.csv"], cwd=str(self.root),
                           capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=d.name))
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRegressions(Seeded):
    def test_windows_line_endings_parse_after_append(self):
        self.seed(EXISTING_RUNS.replace("\n", "\r\n"))
        self.assertEqual(self.record().returncode, 0)
        self.assertEqual(self.ids(), ["R1", "R3"])

    def test_no_trailing_newline_parses_after_append(self):
        self.seed(EXISTING_RUNS.rstrip("\n"))
        self.assertEqual(self.record().returncode, 0)
        self.assertEqual(self.ids(), ["R1", "R3"])

    def test_comment_after_the_last_row(self):
        self.seed(EXISTING_RUNS + "# end of runs\n")
        self.assertEqual(self.record().returncode, 0)
        self.assertEqual(self.ids(), ["R1", "R3"])

    def test_purpose_containing_updated_does_not_touch_the_updated_line(self):
        self.seed()
        r = self.record("--purpose", "updated: 2020-01-01\nupdated: x")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = self.load()
        self.assertEqual(data["updated"], date.today().isoformat())
        self.assertEqual(data["runs"][1]["purpose"], "updated: 2020-01-01\nupdated: x")

    def test_path_with_spaces_and_non_ascii_characters(self):
        self.write("out dir/résumé ä.csv", "a\n")
        r = self.record("--outputs", "out dir/résumé ä.csv")
        self.assertEqual(r.returncode, 0, r.stderr)
        paths = [o["path"] for o in self.load()["runs"][-1]["outputs"]]
        self.assertIn("out dir/résumé ä.csv", paths)

    def test_awkward_tool_versions_read_back_as_the_same_string(self):
        for version in ("1e3", "yes", "5.4", "2026-01-01", "a: b #c", "null", "0x1F", "1_000"):
            with self.subTest(version=version):
                self.runs.unlink() if self.runs.exists() else None
                r = self.record("--tool", f"T={version}")
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn({"name": "T", "version": version}, self.load()["runs"][0]["tools"])


# ---- supersede mode, hardware and wall time, honest dirty flag, unreadable folders ------------

TWO_RUNS = ('# my notes\nversion: 1\nupdated: "2026-01-01"\nrelease:\n  repository: "[insert the repository]"\n'
            '\nruns:\n'
            '  - id: R1\n    date: "2026-01-01"   # keep\n    kind: production\n'
            '    status: valid   # valid | superseded\n    seed: 1\n'
            '  - id: R3\n    date: "2026-02-01"\n    kind: production\n    status: valid\n')


class TestSupersede(Seeded):
    def supersede(self, *extra, args=None):
        a = ["--paper", ".paper", "--supersede", "R1", "--by", "R3", "--reason", "grid changed"] \
            if args is None else list(args)
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *a, *extra], cwd=str(self.root),
                              capture_output=True, text=True)

    def test_only_status_superseded_by_reason_and_updated_change(self):
        before = self.seed(TWO_RUNS).decode("utf-8")
        r = self.supersede()
        self.assertEqual(r.returncode, 0, r.stderr)
        after = self.runs.read_text(encoding="utf-8")
        today = f'updated: "{date.today().isoformat()}"'
        want = (before.replace('updated: "2026-01-01"', today)
                .replace('    status: valid   # valid | superseded\n    seed: 1\n',
                         '    status: superseded\n    superseded_by: "R3"\n'
                         '    reason: "grid changed"\n    seed: 1\n'))
        self.assertEqual(after, want)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_row_reads_back_and_the_other_row_is_unchanged(self):
        self.seed(TWO_RUNS)
        old = self.load()["runs"]
        self.assertEqual(self.supersede().returncode, 0)
        new = self.load()["runs"]
        self.assertEqual(new[1], old[1])
        self.assertEqual(new[0], dict(old[0], status="superseded", superseded_by="R3",
                                      reason="grid changed"))

    def test_unknown_run_to_supersede_is_refused_and_the_file_is_unchanged(self):
        before = self.seed(TWO_RUNS)
        r = self.supersede(args=["--paper", ".paper", "--supersede", "R9", "--by", "R3",
                                 "--reason", "x"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("R9", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_unknown_replacing_run_is_refused(self):
        before = self.seed(TWO_RUNS)
        r = self.supersede(args=["--paper", ".paper", "--supersede", "R1", "--by", "R8",
                                 "--reason", "x"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("R8", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_a_run_cannot_replace_itself(self):
        before = self.seed(TWO_RUNS)
        r = self.supersede(args=["--paper", ".paper", "--supersede", "R1", "--by", "R1",
                                 "--reason", "x"])
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_an_already_superseded_run_is_refused(self):
        self.seed(TWO_RUNS)
        self.assertEqual(self.supersede().returncode, 0)
        before = self.runs.read_bytes()
        r = self.supersede()
        self.assertEqual(r.returncode, 2)
        self.assertIn("already", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_a_reason_and_a_replacing_run_are_required(self):
        before = self.seed(TWO_RUNS)
        for args in (["--paper", ".paper", "--supersede", "R1", "--reason", "x"],
                     ["--paper", ".paper", "--supersede", "R1", "--by", "R3"]):
            r = self.supersede(args=args)
            self.assertEqual(r.returncode, 2, args)
            self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_a_missing_record_is_refused(self):
        r = self.supersede()
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.runs.exists())

    def test_a_reason_with_quotes_reads_back_as_written(self):
        if not HAVE_YAML:
            self.skipTest("PyYAML not installed")
        self.seed(TWO_RUNS)
        r = self.supersede(args=["--paper", ".paper", "--supersede", "R1", "--by", "R3",
                                 "--reason", 'grid "1.0 m": not converged'])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.load()["runs"][0]["reason"], 'grid "1.0 m": not converged')

    def test_help_names_the_mode(self):
        r = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertIn("--supersede", r.stdout)
        self.assertIn("--by", r.stdout)


class TestHardwareAndWallTime(Project):
    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_both_fields_are_written_when_given(self):
        r = self.record("--hardware", "1 GPU, 64 GB", "--wall-time", "3 h 10 min")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.load()["runs"][0]
        self.assertEqual(row["hardware"], "1 GPU, 64 GB")
        self.assertEqual(row["wall_time"], "3 h 10 min")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_fields_are_absent_when_not_given(self):
        self.record()
        row = self.load()["runs"][0]
        self.assertNotIn("hardware", row)
        self.assertNotIn("wall_time", row)


class TestReleaseBlock(Seeded):
    RELEASE = ('version: 1\nupdated: "2026-01-01"\nrelease:\n  repository: "[insert the repository]"\n'
               '  withheld: "[insert what is not released, and why]"\n\nruns:\n'
               '  - id: R1\n    date: "2026-01-01"\n    kind: pilot\n    status: valid\n')

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_a_top_level_release_block_is_kept_byte_for_byte(self):
        self.seed(self.RELEASE)
        r = self.record()
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.runs.read_text(encoding="utf-8")
        block = self.RELEASE.split("\nruns:")[0].split('updated: "2026-01-01"\n')[1]
        self.assertIn(block, text)
        self.assertEqual(self.load()["release"]["repository"], "[insert the repository]")


@unittest.skipUnless(HAVE_GIT, "git not installed")
class TestDirtyHonesty(Project):
    def setUp(self):
        super().setUp()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.com")
        git(self.root, "config", "commit.gpgsign", "false")
        self.write(".gitignore", "*.log\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "init")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_no_code_argument_records_dirty_null(self):
        self.write("code/run_all.py", "print('changed')\n")
        r = self.record(base=["--paper", ".paper", "--id", "R3", "--kind", "check", "--purpose", "p",
                              "--command", "c", "--outputs", "results/annual.csv"])
        self.assertEqual(r.returncode, 0, r.stderr)
        code = self.load()["runs"][0]["code"]
        self.assertIsNotNone(code["commit"])
        self.assertIsNone(code["dirty"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_an_ignored_file_under_a_code_path_counts_as_dirty(self):
        self.write("code/local.log", "not in the commit\n")
        r = self.record()
        self.assertEqual(r.returncode, 0, r.stderr)
        run = self.load()["runs"][0]
        self.assertIn("code/local.log", [f["path"] for f in run["code"]["files"]])
        self.assertIs(run["code"]["dirty"], True)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_an_ignored_cache_folder_that_is_not_hashed_does_not_make_it_dirty(self):
        self.write("code/__pycache__/x.pyc", "bytecode\n")
        self.write(".gitignore", "*.log\n__pycache__/\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "ignore caches")
        self.record()
        self.assertIs(self.load()["runs"][0]["code"]["dirty"], False)


class TestUnreadableFolders(Seeded):
    def setUp(self):
        super().setUp()
        self.locked_dirs = []
        if os.geteuid() == 0:
            self.skipTest("root can read everything")

    def locked(self, rel):
        d = self.root / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / "secret.txt").write_text("x")
        d.chmod(0)
        self.locked_dirs.append(d)
        return d

    def tearDown(self):
        for d in self.locked_dirs:
            d.chmod(0o755)
        super().tearDown()

    def test_an_unreadable_subfolder_is_a_refusal_with_exit_2(self):
        before = self.seed()
        self.locked("inputs/weather/private")
        r = self.record("--inputs", "inputs")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("refused", r.stderr)
        self.assertIn("private", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_a_file_named_inside_an_unreadable_folder_is_a_refusal_not_a_traceback(self):
        before = self.seed()
        self.locked("inputs/locked")
        r = self.record("--inputs", "inputs/locked/secret.txt")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)


class TestNamedSymlinkFolder(Seeded):
    def test_a_symlinked_folder_named_directly_is_not_followed_and_is_warned_about(self):
        (self.root / "elsewhere").mkdir()
        (self.root / "elsewhere" / "x.txt").write_text("x")
        os.symlink(self.root / "elsewhere", self.root / "linked")
        r = self.record("--inputs", "linked", "configs/main.yml")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("warning", r.stderr)
        self.assertIn("linked", r.stderr)
        self.assertNotIn("x.txt", self.runs.read_text(encoding="utf-8"))


class TestToolWarning(Project):
    def test_a_production_run_with_no_tool_prints_a_warning_and_is_written(self):
        base = ["--paper", ".paper", "--id", "R3", "--kind", "production", "--purpose", "p",
                "--command", "c", "--outputs", "results/annual.csv"]
        r = self.record(base=base)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("warning", r.stderr)
        self.assertIn("--tool", r.stderr)

    def test_a_pilot_with_no_tool_and_a_production_run_with_one_print_no_warning(self):
        base = ["--paper", ".paper", "--id", "R3", "--kind", "pilot", "--purpose", "p",
                "--command", "c", "--outputs", "results/annual.csv"]
        self.assertNotIn("--tool", self.record(base=base).stderr)
        self.runs.unlink()
        self.assertEqual(self.record().stderr, "")


class TestHelpExample(unittest.TestCase):
    def test_the_example_does_not_invent_a_tool_version(self):
        doc = SCRIPT.read_text(encoding="utf-8").split('"""')[1]
        self.assertNotIn("5.4a", doc)
        self.assertNotIn("3.12.4", doc)


class TestSupersedeRound2(Seeded):
    def supersede(self, old="R1", by="R3", reason="grid changed"):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--paper", ".paper",
                               "--supersede", old, "--by", by, "--reason", reason],
                              cwd=str(self.root), capture_output=True, text=True)

    def test_a_replacing_run_that_is_not_valid_is_refused(self):
        for status, extra in (("superseded", '    superseded_by: "R1"\n    reason: "x"\n'),
                              ("failed", '    reason: "crashed"\n'),
                              ("excluded", '    reason: "out of scope"\n')):
            with self.subTest(status):
                before = self.seed(TWO_RUNS.replace(
                    '    kind: production\n    status: valid\n',
                    f'    kind: production\n    status: {status}\n{extra}'))
                r = self.supersede()
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("valid", r.stderr)
                self.assertEqual(self.runs.read_bytes(), before)

    def test_no_cycle_can_be_made(self):
        self.seed(TWO_RUNS)
        self.assertEqual(self.supersede().returncode, 0)
        before = self.runs.read_bytes()
        r = self.supersede("R3", "R1")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_an_existing_reason_is_not_overwritten(self):
        before = self.seed(TWO_RUNS.replace('    seed: 1\n', '    seed: 1\n    reason: "my note"\n'))
        r = self.supersede()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("reason", r.stderr)
        self.assertIn("by hand", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)


class TestRound2Fixes(Project):
    BASE = ["--paper", ".paper", "--purpose", "p", "--command", "c", "--outputs", "results/annual.csv"]

    def rec(self, *args):
        return self.record(base=self.BASE + list(args))

    # B-21
    def test_ids_are_letters_digits_dot_underscore_hyphen(self):
        for ok in ("K1", "K2", "R1", "R4", "run_2.b-3"):
            with self.subTest(id=ok):
                r = self.rec("--id", ok, "--kind", "check", "--inputs", "configs/main.yml")
                self.assertEqual(r.returncode, 0, r.stderr)
        for bad in ("R\\1", 'R"3', "R 1", "R:1", "R#1", "R!1", "Ré4"):
            with self.subTest(id=bad):
                r = self.rec("--id", bad, "--kind", "check", "--inputs", "configs/main.yml")
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("--id", r.stderr)

    # B-22
    def test_production_run_without_inputs_or_code_warns(self):
        r = self.rec("--id", "R1", "--kind", "production", "--tool", "Radiance=5.4a")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--inputs", r.stderr)
        self.assertIn("--code", r.stderr)

    def test_production_run_with_inputs_and_code_does_not_warn_about_them(self):
        r = self.rec("--id", "R1", "--kind", "production", "--tool", "Radiance=5.4a",
                     "--inputs", "configs/main.yml", "--code", "code")
        self.assertEqual(r.stderr, "")

    # B-25
    def test_a_crlf_file_stays_crlf(self):
        self.runs.parent.mkdir()
        self.runs.write_bytes(b'version: 1\r\nupdated: "2020-01-01"\r\n\r\nruns:\r\n'
                              b'  - id: "R1"\r\n    status: valid\r\n')
        r = self.rec("--id", "R2", "--kind", "check", "--inputs", "configs/main.yml")
        self.assertEqual(r.returncode, 0, r.stderr)
        raw = self.runs.read_bytes()
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        self.assertEqual([x["id"] for x in self.load()["runs"]], ["R1", "R2"])

    def test_an_inline_runs_list_is_refused_and_left_alone(self):
        self.runs.parent.mkdir()
        before = b"version: 1\nruns: [{id: R1, status: valid}]\n"
        self.runs.write_bytes(before)
        r = self.rec("--id", "R2", "--kind", "check", "--inputs", "configs/main.yml")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.runs.read_bytes(), before)

    def test_mixed_indents_are_refused_and_left_alone(self):
        self.runs.parent.mkdir()
        before = b"version: 1\nruns:\n  - id: R1\n    status: valid\n - id: R2\n    status: valid\n"
        self.runs.write_bytes(before)
        r = self.rec("--id", "R3", "--kind", "check", "--inputs", "configs/main.yml")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_read_back_refuses_a_change_to_an_earlier_row_or_key(self):
        import record_run
        old = 'version: 1\nrelease:\n  x: 1\nruns:\n  - id: R1\n    status: valid\n'
        good = old + "  - id: R2\n    status: valid\n"
        record_run._verify(old, good, "R2", self.runs)               # no error
        changed_row = good.replace("id: R1\n    status: valid", "id: R1\n    status: failed")
        with self.assertRaises(record_run.Refused):
            record_run._verify(old, changed_row, "R2", self.runs)
        changed_key = good.replace("  x: 1", "  x: 2")
        with self.assertRaises(record_run.Refused):
            record_run._verify(old, changed_key, "R2", self.runs)
        with self.assertRaises(record_run.Refused):                  # two rows added
            record_run._verify(old, good + "  - id: R3\n    status: valid\n", "R3", self.runs)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_supersede_read_back_refuses_a_change_to_another_row(self):
        import record_run
        old = "runs:\n  - id: R1\n    status: valid\n  - id: R2\n    status: valid\n"
        good = ("runs:\n  - id: R1\n    status: superseded\n    superseded_by: \"R2\"\n"
                "    reason: \"x\"\n  - id: R2\n    status: valid\n")
        record_run._verify_supersede(old, good, "R1", "R2", "x", self.runs)
        with self.assertRaises(record_run.Refused):
            record_run._verify_supersede(old, good.replace("id: R2\n    status: valid",
                                                           "id: R2\n    status: failed"),
                                         "R1", "R2", "x", self.runs)

    def test_a_failed_write_leaves_the_old_file_and_no_temporary_file(self):
        import record_run
        from unittest import mock
        self.runs.parent.mkdir()
        self.runs.write_text("old", encoding="utf-8")
        with mock.patch.object(record_run.os, "replace", side_effect=OSError(5, "disk")):
            with self.assertRaises(record_run.Refused):
                record_run.write_atomic(self.runs, "new")
        self.assertEqual(self.runs.read_text(encoding="utf-8"), "old")
        self.assertEqual([p.name for p in self.runs.parent.iterdir()], ["runs.yml"])

    def test_a_failed_run_with_no_reason_field_cannot_be_superseded(self):
        self.runs.parent.mkdir()
        self.runs.write_text("version: 1\nruns:\n  - id: R1\n    status: failed\n"
                             "  - id: R2\n    status: valid\n", encoding="utf-8")
        before = self.runs.read_bytes()
        r = self.record(base=["--paper", ".paper", "--supersede", "R1", "--by", "R2",
                              "--reason", "x"])
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("not valid", r.stderr)
        self.assertEqual(self.runs.read_bytes(), before)
