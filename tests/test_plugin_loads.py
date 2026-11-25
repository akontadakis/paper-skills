"""The plugin, loaded by Claude Code itself, offers every agent and skill the package ships.

`claude plugin validate` checks the manifest's form. It does not show what the loader finds.
This test asks the loader. It runs no model and costs nothing.
"""
import re
import shutil
import subprocess
import unittest

from tests import _paths

CLAUDE = shutil.which("claude")


@unittest.skipIf(CLAUDE is None, "the claude command is not installed")
class TestPluginInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            [CLAUDE, "--plugin-dir", str(_paths.ROOT), "plugin", "details", "paper-skills"],
            capture_output=True, text=True, timeout=120)
        cls.output = result.stdout + result.stderr

    def count(self, kind: str) -> int:
        found = re.search(rf"{kind} \((\d+)\)", self.output)
        self.assertIsNotNone(found, f"no '{kind} (n)' line in:\n{self.output}")
        return int(found.group(1))

    def test_every_agent_file_is_loaded(self):
        shipped = sorted(p.stem for p in (_paths.ROOT / "agents").glob("*.md"))
        self.assertGreaterEqual(len(shipped), 5, "expected agent files in the top-level agents/ folder")
        self.assertEqual(self.count("Agents"), len(shipped))
        for name in shipped:
            with self.subTest(agent=name):
                self.assertIn(name, self.output)

    def test_every_skill_and_command_is_loaded(self):
        skills = [p.parent.name for p in _paths.ROOT.glob("*/SKILL.md")]
        commands = [p.stem for p in (_paths.ROOT / "commands").glob("*.md")]
        self.assertEqual(self.count("Skills"), len(skills) + len(commands))


if __name__ == "__main__":
    unittest.main()
