import os
import unittest
from unittest.mock import patch

from dashboard import env_bool, env_int, service_configs
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

    def test_auto_rotate_config_on_and_off(self):
        for value in ("false", "OFF", "no", "0"):
            with self.subTest(value=value), patch.dict(os.environ, {"AUTO_ROTATE_PAGES": value}):
                self.assertFalse(env_bool("AUTO_ROTATE_PAGES"))
        for value in ("true", "ON", "yes", "1"):
            with self.subTest(value=value), patch.dict(os.environ, {"AUTO_ROTATE_PAGES": value}):
                self.assertTrue(env_bool("AUTO_ROTATE_PAGES"))
        with patch.dict(os.environ, {"AUTO_ROTATE_PAGES": ""}):
            self.assertTrue(env_bool("AUTO_ROTATE_PAGES"))
        with patch.dict(os.environ, {"AUTO_ROTATE_PAGES": "invalid"}):
            self.assertTrue(env_bool("AUTO_ROTATE_PAGES"))

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

    def test_two_nas_paths_have_independent_readings(self):
        from metrics import nas_volumes_snapshot
        paths = '[{"name":"Drive 1","path":"/srv/nas/drive1"},{"name":"Drive 2","path":"/srv/nas/drive2"}]'
        with (
            patch.dict(os.environ, {"NAS_STORAGE_PATHS": paths}),
            patch("metrics.nas_storage_snapshot", side_effect=[
                {"path": "/srv/nas/drive1", "status": "ok", "disk_percent": 25.0},
                {"path": "/srv/nas/drive2", "status": "ok", "disk_percent": 60.0},
            ]),
        ):
            volumes = nas_volumes_snapshot()
        self.assertEqual([v["name"] for v in volumes], ["Drive 1", "Drive 2"])
        self.assertEqual([v["disk_percent"] for v in volumes], [25.0, 60.0])

    def test_unmounted_second_nas_is_not_reported_as_healthy(self):
        from metrics import nas_volumes_snapshot
        config = '[{"name":"Drive 1","path":"/srv/nas/drive1"},{"name":"Drive 2","path":"/srv/nas/drive2"}]'
        with (
            patch.dict(os.environ, {"NAS_STORAGE_PATHS": config}),
            patch("metrics.nas_storage_snapshot", side_effect=[
                {"path": "/srv/nas/drive1", "status": "ok", "disk_percent": 10.0},
                {"path": "/srv/nas/drive2", "status": "system_disk"},
            ]),
        ):
            first, second = nas_volumes_snapshot()
        self.assertEqual(first["status"], "ok")
        self.assertEqual(second["status"], "system_disk")
        self.assertNotIn("disk_percent", second)

    def test_bad_nas_paths_configuration_displays_warning(self):
        from metrics import nas_volumes_snapshot
        for raw in ("not JSON", "[]", '[{"name":"a","path":"/a"},{"name":"b","path":"/b"},{"name":"c","path":"/c"}]'):
            with self.subTest(raw=raw):
                with patch.dict(os.environ, {"NAS_STORAGE_PATHS": raw}):
                    self.assertEqual(nas_volumes_snapshot()[0]["status"], "invalid")

    def test_disabled_multi_nas_keeps_legacy_single_path(self):
        from metrics import nas_volumes_snapshot
        with patch.dict(os.environ, {"NAS_STORAGE_PATHS": ""}):
            self.assertEqual(nas_volumes_snapshot(), [])


if __name__ == "__main__":
    unittest.main()
