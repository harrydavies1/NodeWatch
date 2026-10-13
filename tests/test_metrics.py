import os
import unittest
from unittest.mock import patch

from dashboard import env_int, service_configs
from metrics import snapshot


class DashboardTests(unittest.TestCase):
    def test_snapshot_has_expected_numbers(self):
        stats = snapshot()
        self.assertIsInstance(stats["cpu_percent"], (int, float))
        self.assertGreaterEqual(stats["memory_total"], 0)
        self.assertGreaterEqual(stats["uptime_seconds"], 0)
        self.assertIn("hostname", stats)

    def test_config_clamping(self):
        with patch.dict(os.environ, {"ROTATE_SECONDS": "999"}):
            self.assertEqual(env_int("ROTATE_SECONDS", 12, 4, 120), 120)
        with patch.dict(os.environ, {"ROTATE_SECONDS": "banana"}):
            self.assertEqual(env_int("ROTATE_SECONDS", 12, 4, 120), 12)

    def test_service_config_validation(self):
        with patch.dict(os.environ, {"SERVICES_JSON": '[{"name":"SSH","host":"localhost","port":22},{"bad":"value"}]'}):
            self.assertEqual(len(service_configs()), 1)
        with patch.dict(os.environ, {"SERVICES_JSON": 'not-json'}):
            self.assertEqual(service_configs(), [])


if __name__ == "__main__":
    unittest.main()
