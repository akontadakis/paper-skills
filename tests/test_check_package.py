"""check_package.py checks the files the package ships, and no others.

A virtual environment, a results folder or a cache sits inside the package folder on a
developer's machine. Markdown files inside them belong to other projects, so a fault in one
of them is not a fault in this package.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import _paths

SCRIPT = _paths.SCRIPTS / "check_package.py"
NOT_SHIPPED = shutil.ignore_patterns(".venv", ".git", "__pycache__", "results", ".pytest_cache")

# Three faults the checker reports when they sit in a shipped file: a bare filename that
# matches nothing, a reference path that matches nothing, and a YAML block that does not parse.
STRAY = (
    "See `nowhere-in-this-package.py` and references/nowhere-in-this-package.md.\n\n"
    "```yaml\nbroken: [1\n```\n"
)


def run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), "--root", str(root)],
                          capture_output=True, text=True)


class TestFoldersNotShipped(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "pkg"
        shutil.copytree(_paths.ROOT, self.root, ignore=NOT_SHIPPED)

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, relative: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(STRAY, encoding="utf-8")

    def test_clean_copy_passes(self):
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_clean_copy_gives_no_warning(self):
        """A warning on every run teaches the reader to ignore warnings."""
        result = run(self.root)
        self.assertNotIn("WARN", result.stdout)
        self.assertIn("0 warning(s)", result.stdout)

    def test_stray_file_in_a_skill_folder_is_reported(self):
        self.put("research-paper-writing/references/stray.md")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("nowhere-in-this-package.py", result.stdout)

    def test_virtual_environment_is_not_checked(self):
        self.put(".venv/lib/python3.12/site-packages/other_project/README.md")
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn(".venv", result.stdout)

    def test_cache_folders_are_not_checked(self):
        self.put("node_modules/some_tool/README.md")
        self.put("tests/__pycache__/notes.md")
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)


def run_without_yaml(root: Path) -> subprocess.CompletedProcess:
    code = ("import sys, runpy; sys.modules['yaml'] = None; "
            f"sys.argv = ['check_package.py', '--root', {str(root)!r}]; "
            f"runpy.run_path({str(SCRIPT)!r}, run_name='__main__')")
    return subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True)


class TestSkippedCheckIsNotClean(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "pkg"
        shutil.copytree(_paths.ROOT, self.root, ignore=NOT_SHIPPED)

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_pyyaml_gives_exit_3_when_nothing_failed(self):
        if run(self.root).returncode != 0:
            self.skipTest("the package itself fails its own check, so there is no passing "
                          "copy to test; fix the package first")
        result = run_without_yaml(self.root)
        self.assertIn("NOT CHECKED", result.stdout)
        self.assertEqual(result.returncode, 3, result.stdout)

    def test_missing_pyyaml_with_a_failure_still_exits_1(self):
        (self.root / "research-paper-writing" / "references" / "stray.md").write_text(
            STRAY, encoding="utf-8")
        result = run_without_yaml(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_wrong_root_still_exits_2(self):
        result = run(Path(self._tmp.name))
        self.assertEqual(result.returncode, 2)


class TestAgentLayout(unittest.TestCase):
    """Claude Code loads plugin agents from a top-level agents/ folder. An agent file that
    sits inside a skill folder, or is listed as a file in plugin.json, is not loaded."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "pkg"
        shutil.copytree(_paths.ROOT, self.root, ignore=NOT_SHIPPED)

    def tearDown(self):
        self._tmp.cleanup()

    def test_agents_sit_in_the_top_level_folder(self):
        names = sorted(p.stem for p in (self.root / "agents").glob("*.md"))
        self.assertEqual(names, ["bibliography-auditor", "claim-auditor", "consistency-checker",
                                 "design-reviewer", "latex-layout-auditor", "literature-crawler"])

    def test_agent_file_inside_a_skill_folder_is_reported(self):
        target = self.root / "research-paper-writing" / "agents" / "claim-auditor.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(self.root / "agents" / "claim-auditor.md", target)
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("research-paper-writing/agents/claim-auditor.md", result.stdout)

    def test_manifest_that_lists_agent_files_is_reported(self):
        import json
        manifest = self.root / ".claude-plugin" / "plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["agents"] = ["./agents/claim-auditor.md"]
        manifest.write_text(json.dumps(data), encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("plugin.json", result.stdout)


class TestNoBehaviourSuite(unittest.TestCase):
    """The owner removed the behaviour-test suite on 2026-11-17. Nothing in the package
    ships it, points to it, or checks it."""

    def test_the_folder_is_gone(self):
        self.assertFalse((_paths.ROOT / "plugin-evals").exists())

    def test_the_manifest_does_not_point_to_it(self):
        import json
        manifest = json.loads((_paths.ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("experimental", manifest)

    def test_no_tracked_text_file_names_it(self):
        for path in sorted(_paths.ROOT.rglob("*")):
            parts = path.relative_to(_paths.ROOT).parts
            if not path.is_file() or {".venv", ".git", "__pycache__"} & set(parts):
                continue
            if path.suffix not in (".md", ".json", ".py", ".yaml", ".yml") and path.name != ".gitignore":
                continue
            if path.name in ("test_check_package.py", "test_guide_facts.py"):
                continue                      # these two name it in order to forbid it
            with self.subTest(file="/".join(parts)):
                self.assertNotIn("plugin-evals", path.read_text(encoding="utf-8", errors="replace"))


class TestThreeSkills(unittest.TestCase):
    """The package ships three skills. Each one is in the manifest, in the install guide, and
    under the same quality checks."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "pkg"
        shutil.copytree(_paths.ROOT, self.root, ignore=NOT_SHIPPED)

    def tearDown(self):
        self._tmp.cleanup()

    def test_every_skill_folder_is_in_the_manifest(self):
        import json
        manifest = json.loads((self.root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        folders = sorted("./" + p.parent.name for p in self.root.glob("*/SKILL.md"))
        self.assertEqual(sorted(manifest["skills"]), folders)
        self.assertIn("./research-study-design", folders)

    def test_manifest_that_omits_the_study_design_skill_is_reported(self):
        import json
        path = self.root / ".claude-plugin" / "plugin.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["skills"] = [s for s in manifest["skills"] if "research-study-design" not in s]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("research-study-design", result.stdout)

    def test_study_design_skill_is_held_to_its_word_budget(self):
        skill = self.root / "research-study-design" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\n" + "word " * 1200, encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("research-study-design/SKILL.md", result.stdout)

    def test_memory_file_missing_from_the_directory_listing_is_reported(self):
        guide = self.root / "research-paper-writing" / "references" / "paper-memory.md"
        text = guide.read_text(encoding="utf-8")
        self.assertIn("design.yml", text)
        guide.write_text("\n".join(line for line in text.splitlines() if "design.yml" not in line),
                         encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("design.yml", result.stdout)


class TestSkillQuality(unittest.TestCase):
    """A SKILL.md is read in full every time its skill loads, and its description decides
    whether the skill loads at all. The checker holds both to the skill-writing standard."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "pkg"
        shutil.copytree(_paths.ROOT, self.root, ignore=NOT_SHIPPED)
        self.skill = self.root / "research-paper-writing" / "SKILL.md"

    def tearDown(self):
        self._tmp.cleanup()

    def edit(self, old: str, new: str) -> None:
        text = self.skill.read_text(encoding="utf-8")
        self.assertIn(old, text)
        self.skill.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_description_that_does_not_start_with_use_when_is_reported(self):
        self.edit("description: Use when", "description: Improves papers when")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Use when", result.stdout)

    def test_skill_file_over_its_word_budget_is_reported(self):
        self.skill.write_text(self.skill.read_text(encoding="utf-8") + "\n" + "word " * 2500,
                              encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("word budget", result.stdout)

    def test_skill_file_without_a_when_to_use_section_is_reported(self):
        self.edit("## When to Use", "## Scope")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("When to Use", result.stdout)

    def test_long_guide_without_a_load_when_line_is_reported(self):
        guide = self.root / "research-paper-writing" / "references" / "statistics-reporting.md"
        text = guide.read_text(encoding="utf-8")
        self.assertIn("**Load when:**", text)
        guide.write_text(text.replace("**Load when:**", "**Note:**", 1), encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Load when", result.stdout)

    def test_long_guide_without_a_contents_line_is_reported(self):
        guide = self.root / "responding-to-reviewers" / "references" / "triage.md"
        text = guide.read_text(encoding="utf-8")
        self.assertIn("**Contents:**", text)
        guide.write_text(text.replace("**Contents:**", "**Parts:**", 1), encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Contents", result.stdout)

    def test_agent_description_that_does_not_say_when_to_use_it_is_reported(self):
        agent = self.root / "agents" / "claim-auditor.md"
        text = agent.read_text(encoding="utf-8")
        self.assertRegex(text, r"Use (when|before|after)")
        import re as _re
        agent.write_text(_re.sub(r"Use (when|before|after)", "Good for", text), encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("claim-auditor", result.stdout)

    def test_script_run_without_an_interpreter_is_reported(self):
        self.skill.write_text(self.skill.read_text(encoding="utf-8")
                              + "\nRun `scripts/check_ledger.py .paper --manuscript main.tex`.\n",
                              encoding="utf-8")
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("python3", result.stdout)


if __name__ == "__main__":
    unittest.main()
