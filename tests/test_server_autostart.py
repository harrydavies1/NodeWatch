"""Test the optional Ubuntu Server systemd service generator (without sudo)."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agent_service_unit", ROOT / "deploy/server_agent_service.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AgentAutostartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "pi-server-dashboard"
        self.root.mkdir()
        (self.root / "agent.py").write_text("# test agent\n")
        python = self.root / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.write_text("#!/usr/bin/env python3\n")

    def configure(self, token="x" * 36, host="0.0.0.0", port=8766):
        (self.root / ".env").write_text(
            f"AGENT_TOKEN={token}\nAGENT_HOST={host}\nAGENT_PORT={port}\n"
        )

    def test_generates_unit_using_real_username_and_checkout_without_token(self):
        self.configure()
        unit = MODULE.render_service(self.root, "ubuntu")
        self.assertIn("User=ubuntu\n", unit)
        self.assertIn(f"WorkingDirectory={self.root}\n", unit)
        self.assertIn(f"ExecStart={self.root}/.venv/bin/python {self.root}/agent.py\n", unit)
        self.assertIn("WantedBy=multi-user.target", unit)
        self.assertIn("Restart=on-failure", unit)
        self.assertNotIn("x" * 36, unit)

    def test_rejects_missing_or_placeholder_token(self):
        for token in ("", "short", "PASTE_YOUR_LONG_RANDOM_TOKEN_HERE"):
            with self.subTest(token=token):
                self.configure(token=token)
                with self.assertRaisesRegex(ValueError, "AGENT_TOKEN"):
                    MODULE.render_service(self.root, "ubuntu")

    def test_rejects_invalid_port(self):
        self.configure(port=70000)
        with self.assertRaisesRegex(ValueError, "AGENT_PORT"):
            MODULE.render_service(self.root, "ubuntu")

    def test_rejects_invalid_username(self):
        self.configure()
        with self.assertRaisesRegex(ValueError, "username"):
            MODULE.render_service(self.root, "ubuntu;touch /tmp/bad")

    def test_requires_server_env_and_agent(self):
        with self.assertRaisesRegex(ValueError, r"\.env"):
            MODULE.render_service(self.root, "ubuntu")
        self.configure()
        (self.root / "agent.py").unlink()
        with self.assertRaisesRegex(ValueError, "agent.py"):
            MODULE.render_service(self.root, "ubuntu")


if __name__ == "__main__":
    unittest.main()
