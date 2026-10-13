"""Regression checks for local Pi and optional remote Server Mode."""
import os
import unittest
from unittest.mock import patch

from dashboard import collect_state


SAMPLE = {
    "hostname": "testpi",
    "cpu_percent": 12.5,
    "ip": "192.0.2.10",
    "memory_percent": 25.0,
}


class MonitoringModesTests(unittest.TestCase):
    @patch.dict(os.environ, {
        "REMOTE_AGENT_URL": "",
        "REMOTE_AGENT_TOKEN": "",
        "SERVICES_JSON": "[]",
    })
    @patch("dashboard.snapshot", return_value=SAMPLE)
    def test_pi_mode_uses_local_stats(self, local_snapshot):
        state = collect_state()
        self.assertEqual(state["server"]["mode"], "pi")
        self.assertIsNone(state["server"]["connected"])
        self.assertEqual(state["server"]["stats"], SAMPLE)
        self.assertEqual(state["pi"], SAMPLE)
        local_snapshot.assert_called_once()

    @patch.dict(os.environ, {
        "REMOTE_AGENT_URL": "http://server.example:8766",
        "REMOTE_AGENT_TOKEN": "test-token",
        "SERVICES_JSON": "[]",
    })
    @patch("dashboard.snapshot", return_value=SAMPLE)
    @patch("dashboard.fetch_server_metrics")
    def test_server_mode_uses_remote_stats_and_keeps_pi_stats(self, fetch, local_snapshot):
        remote = {**SAMPLE, "hostname": "ubuntu-server", "cpu_percent": 60.0}
        fetch.return_value = (remote, 25)
        state = collect_state()
        self.assertEqual(state["server"]["mode"], "remote")
        self.assertTrue(state["server"]["connected"])
        self.assertEqual(state["server"]["stats"], remote)
        self.assertEqual(state["pi"], SAMPLE)
        fetch.assert_called_once_with("http://server.example:8766", "test-token")
        local_snapshot.assert_called_once()

    @patch.dict(os.environ, {
        "REMOTE_AGENT_URL": "http://server.example:8766",
        "REMOTE_AGENT_TOKEN": "test-token",
        "SERVICES_JSON": "[]",
    })
    @patch("dashboard.snapshot", return_value=SAMPLE)
    @patch("dashboard.fetch_server_metrics", side_effect=OSError("server unavailable"))
    def test_remote_failure_does_not_mislabel_pi_stats(self, _fetch, _local_snapshot):
        state = collect_state()
        self.assertEqual(state["server"]["mode"], "remote")
        self.assertFalse(state["server"]["connected"])
        self.assertIsNone(state["server"]["stats"])
        self.assertEqual(state["pi"], SAMPLE)


if __name__ == "__main__":
    unittest.main()
