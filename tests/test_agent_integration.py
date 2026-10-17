"""Loopback HTTP test: the real optional server agent and Pi collector interoperate."""
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from agent import AgentHandler
from dashboard import collect_state

PI = {"hostname": "test-pi", "cpu_percent": 10, "memory_percent": 20}
SERVER = {"hostname": "test-optiplex", "cpu_percent": 48, "memory_percent": 35}


class QuietAgentHandler(AgentHandler):
    def log_message(self, format, *args):
        pass


class AgentIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietAgentHandler)
        self.worker = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.worker.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.worker.join, 2)
        self.addCleanup(self.server.shutdown)
        self.agent_url = "http://127.0.0.1:%d" % self.server.server_port

    def test_real_agent_http_path_with_matching_token(self):
        env = {
            "AGENT_TOKEN": "long-test-token",
            "REMOTE_AGENT_URL": self.agent_url,
            "REMOTE_AGENT_TOKEN": "long-test-token",
            "SERVICES_JSON": "[]",
        }
        with (
            patch.dict(os.environ, env),
            patch("dashboard.snapshot", return_value=PI),
            patch("agent.snapshot", return_value=SERVER),
        ):
            state = collect_state()
        self.assertEqual(state["server"]["mode"], "remote")
        self.assertTrue(state["server"]["connected"])
        self.assertEqual(state["server"]["stats"], SERVER)
        self.assertEqual(state["pi"], PI)
        self.assertIsInstance(state["server"]["latency_ms"], int)

    def test_wrong_token_is_offline_without_faking_server_stats(self):
        env = {
            "AGENT_TOKEN": "actual-test-token",
            "REMOTE_AGENT_URL": self.agent_url,
            "REMOTE_AGENT_TOKEN": "incorrect-token",
            "SERVICES_JSON": "[]",
        }
        with (
            patch.dict(os.environ, env),
            patch("dashboard.snapshot", return_value=PI),
            patch("agent.snapshot", return_value=SERVER),
        ):
            state = collect_state()
        self.assertEqual(state["server"]["mode"], "remote")
        self.assertFalse(state["server"]["connected"])
        self.assertIsNone(state["server"]["stats"])
        self.assertEqual(state["pi"], PI)
        self.assertIn("401", state["server"]["error"])

    def test_remote_agent_transmits_configured_nas_storage(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from metrics import snapshot
        with TemporaryDirectory() as folder:
            env = {
                "AGENT_TOKEN": "test-token",
                "REMOTE_AGENT_URL": self.agent_url,
                "REMOTE_AGENT_TOKEN": "test-token",
                "NAS_STORAGE_PATH": str(Path(folder)),
                "SERVICES_JSON": "[]",
            }
            with (
                patch.dict(os.environ, env),
                patch("dashboard.snapshot", return_value=PI),
                patch("agent.snapshot", side_effect=snapshot),
            ):
                state = collect_state()
        self.assertTrue(state["server"]["connected"])
        nas = state["server"]["stats"]["nas_storage"]
        self.assertEqual(nas["status"], "system_disk")
        self.assertEqual(nas["path"], folder)
        self.assertGreater(nas["disk_total"], 0)

    def test_two_nas_volumes_travel_from_server_agent_to_pi(self):
        remote = {**SERVER, "nas_volumes": [
            {"name": "NAS Drive 1", "path": "/srv/nas/drive1",
             "status": "ok", "disk_percent": 0.1, "disk_total": 500000000000},
            {"name": "NAS Drive 2", "path": "/srv/nas/drive2",
             "status": "ok", "disk_percent": 26.1, "disk_total": 500000000000},
        ]}
        env = {
            "AGENT_TOKEN": "matching-test-token",
            "REMOTE_AGENT_URL": self.agent_url,
            "REMOTE_AGENT_TOKEN": "matching-test-token",
            "SERVICES_JSON": "[]",
        }
        with (
            patch.dict(os.environ, env),
            patch("dashboard.snapshot", return_value=PI),
            patch("agent.snapshot", return_value=remote),
        ):
            state = collect_state()
        self.assertTrue(state["server"]["connected"])
        volumes = state["server"]["stats"]["nas_volumes"]
        self.assertEqual(len(volumes), 2)
        self.assertEqual([v["disk_percent"] for v in volumes], [0.1, 26.1])


if __name__ == "__main__":
    unittest.main()
