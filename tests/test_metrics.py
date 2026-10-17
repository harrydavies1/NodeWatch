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

    def test_nas_storage_not_configured(self):
        from metrics import nas_storage_snapshot
        with patch.dict(os.environ, {"NAS_STORAGE_PATH": ""}):
            self.assertIsNone(nas_storage_snapshot())

    def test_nas_folder_on_root_is_explicit(self):
        from metrics import nas_storage_snapshot
        import tempfile
        with tempfile.TemporaryDirectory() as path:
            with patch.dict(os.environ, {"NAS_STORAGE_PATH": path}):
                result = nas_storage_snapshot()
        self.assertEqual(result["status"], "system_disk")
        self.assertGreater(result["disk_total"], 0)

    def test_missing_nas_disk_is_unavailable_not_root(self):
        from metrics import nas_storage_snapshot
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "not-mounted")
            with patch.dict(os.environ, {"NAS_STORAGE_PATH": path}):
                result = nas_storage_snapshot()
        self.assertEqual(result, {"path": path, "status": "unavailable"})
        self.assertNotIn("disk_percent", result)

    def test_nas_on_separate_filesystem(self):
        from metrics import nas_storage_snapshot
        from types import SimpleNamespace
        with (
            patch.dict(os.environ, {"NAS_STORAGE_PATH": "/mnt/drive/share"}),
            patch("metrics.os.stat", side_effect=[
                SimpleNamespace(st_dev=200),
                SimpleNamespace(st_dev=100),
            ]),
            patch("metrics.os.path.isdir", return_value=True),
            patch("metrics.psutil.disk_usage", return_value=SimpleNamespace(
                percent=37.7, used=377, total=1000, free=623,
            )),
        ):
            result = nas_storage_snapshot()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["disk_percent"], 37.7)
        self.assertEqual(result["disk_total"], 1000)

    def test_nas_relative_path_not_accepted(self):
        from metrics import nas_storage_snapshot
        with patch.dict(os.environ, {"NAS_STORAGE_PATH": "share"}):
            self.assertEqual(nas_storage_snapshot(),
                             {"path": "share", "status": "unavailable"})


if __name__ == "__main__":
    unittest.main()
