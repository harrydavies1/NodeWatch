"""Regression tests for opt-in cached SMART HDD temperatures and Pi pages."""

import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import hdd_temperatures as hdd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python-display"))
from ui_helpers import hdd_temperatures_for_state, page_count_for_state


class HDDTemperatureTests(unittest.TestCase):
    def setUp(self):
        hdd._cache.clear()

    def test_no_config_no_smart_reads(self):
        with patch.dict(os.environ, {"HDD_TEMP_DRIVES": ""}), patch("hdd_temperatures.subprocess.run") as run:
            self.assertEqual(hdd.hdd_temperatures_snapshot(), [])
            run.assert_not_called()

    def test_parse_194_prefers_raw_string_not_packed_value(self):
        payload = {"ata_smart_attributes": {"table": [
            {"id": 194, "raw": {"value": 999999, "string": "52 (Min/Max 10/58)"}},
            {"id": 190, "raw": {"string": "33 (Min/Max 21/33)"}},
        ]}}
        self.assertEqual(hdd.parse_temperature(payload), 52.0)

    def test_parse_top_level_temperature(self):
        self.assertEqual(hdd.parse_temperature({"temperature": {"current": 33}}), 33.0)
        self.assertIsNone(hdd.parse_temperature({"temperature": {"current": 999}}))

    def test_190_fallback(self):
        payload = {"ata_smart_attributes": {"table": [
            {"id": 190, "raw": {"string": "33 (Min/Max 21/33)"}}]}}
        self.assertEqual(hdd.parse_temperature(payload), 33.0)

    def test_two_drives_cached_for_sixty_seconds(self):
        config = json.dumps([
            {"name": "Drive 1", "device": "/dev/sdb"},
            {"name": "Drive 2", "device": "/dev/sdc"},
        ])
        first = {"temperature": {"current": 33}}
        second = {"ata_smart_attributes": {"table": [{"id": 194, "raw": {"string": "52 (Min/Max 10/58)"}}]}}
        with (
            patch.dict(os.environ, {"HDD_TEMP_DRIVES": config}),
            patch("hdd_temperatures.subprocess.run", side_effect=[
                SimpleNamespace(stdout=json.dumps(first), returncode=0),
                SimpleNamespace(stdout=json.dumps(second), returncode=0),
                SimpleNamespace(stdout=json.dumps(first), returncode=0),
                SimpleNamespace(stdout=json.dumps(second), returncode=0),
            ]) as runner,
            patch("hdd_temperatures.time.monotonic", side_effect=[0, 0, 30, 30, 61, 61]),
        ):
            result = hdd.hdd_temperatures_snapshot()
            self.assertEqual([x["temperature_c"] for x in result], [33.0, 52.0])
            hdd.hdd_temperatures_snapshot()
            self.assertEqual(runner.call_count, 2)
            hdd.hdd_temperatures_snapshot()
            self.assertEqual(runner.call_count, 4)
        args = runner.call_args_list[0].args[0]
        self.assertEqual(args, ["sudo", "-n", "/usr/sbin/smartctl",
                                "-j", "-A", "-n", "standby", "/dev/sdb"])

    def test_sleeping_drive_does_not_fabricate_temperature(self):
        with patch("hdd_temperatures.subprocess.run",
                   return_value=SimpleNamespace(stdout=json.dumps({
                       "smartctl": {"messages": [{"string": "Device is in STANDBY mode"}]}
                   }), returncode=2)):
            self.assertEqual(hdd._read_temperature("/dev/sdb"), {"status": "standby"})

    def test_smart_permissions_failure_is_unavailable(self):
        with patch("hdd_temperatures.subprocess.run",
                   return_value=SimpleNamespace(stdout="", returncode=1)):
            self.assertEqual(hdd._read_temperature("/dev/sdc"), {"status": "unavailable"})

    def test_invalid_config_is_visible_and_not_executed(self):
        for cfg in ('bad JSON', '[]',
                    '[{"name":"bad","device":"--help"}]',
                    '[{"name":"bad","device":"/dev/sdb;echo test"}]'):
            with self.subTest(cfg=cfg), patch.dict(os.environ, {"HDD_TEMP_DRIVES": cfg}), \
                 patch("hdd_temperatures.subprocess.run") as run:
                readings = hdd.hdd_temperatures_snapshot()
                self.assertEqual(readings[0]["status"], "invalid")
                run.assert_not_called()

    def test_page_counts_and_page_order_compatibility(self):
        self.assertEqual(page_count_for_state(None), 2)
        state = {"server": {"mode": "remote", "connected": True, "stats": {
            "nas_volumes": [{"name": "Drive 1", "status": "ok"}],
            "hdd_temperatures": [
                {"name": "Drive 1", "status": "ok", "temperature_c": 33},
                {"name": "Drive 2", "status": "unavailable"},
            ],
        }}}
        self.assertEqual(page_count_for_state(state), 4)
        self.assertEqual(len(hdd_temperatures_for_state(state)), 2)
        state["server"]["stats"]["nas_volumes"] = []
        self.assertEqual(page_count_for_state(state), 3)
        state["server"]["stats"]["hdd_temperatures"] = []
        self.assertEqual(page_count_for_state(state), 2)
        state["server"]["mode"] = "pi"
        state["server"]["stats"]["hdd_temperatures"] = [{"status": "ok"}]
        self.assertEqual(page_count_for_state(state), 2)


if __name__ == "__main__":
    unittest.main()
