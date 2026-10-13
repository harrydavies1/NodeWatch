"""Check the optional autostart helper without starting a GUI or modifying user settings."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "python-display" / "autostart.sh"


class AutostartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.config = self.home / ".config"
        self.entry = self.config / "autostart" / "nodewatch.desktop"
        self.saved = self.config / "nodewatch" / "nodewatch.desktop.disabled"
        self.env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.config))

    def run_helper(self, action):
        return subprocess.run(
            ["bash", str(HELPER), action],
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    def test_opt_in_enable_disable_and_restore(self):
        self.assertIn("not configured", self.run_helper("status"))
        self.run_helper("enable")
        entry_content = self.entry.read_text()
        self.assertIn("[Desktop Entry]", entry_content)
        self.assertIn('Exec=/bin/bash "', entry_content)
        self.assertIn("autostart-launch.sh", entry_content)
        self.assertIn("exists", self.run_helper("status"))
        self.run_helper("disable")
        self.assertFalse(self.entry.exists())
        self.assertTrue(self.saved.exists())
        self.run_helper("enable")
        self.assertEqual(self.entry.read_text(), entry_content)

    def test_enable_keeps_existing_custom_entry(self):
        self.entry.parent.mkdir(parents=True)
        original = "[Desktop Entry]\nName=Custom NodeWatch\nExec=/bin/bash /custom/run.sh\n"
        self.entry.write_text(original)
        self.run_helper("enable")
        self.assertEqual(self.entry.read_text(), original)


if __name__ == "__main__":
    unittest.main()
