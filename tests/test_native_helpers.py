import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python-display"))
from ui_helpers import readable_percent, readable_size, readable_uptime, safe_text, status_label


class NativeHelpersTests(unittest.TestCase):
    def test_percent_handles_missing_and_invalid(self):
        self.assertEqual(readable_percent(None), "--")
        self.assertEqual(readable_percent(52.7), "53%")
        self.assertEqual(readable_percent(999), "100%")
        self.assertEqual(readable_percent(True), "--")

    def test_size_and_uptime(self):
        self.assertEqual(readable_size(1024), "1.0 KiB")
        self.assertEqual(readable_size(-1), "--")
        self.assertEqual(readable_uptime(3601), "1h 0m")
        self.assertEqual(readable_uptime(None), "--")

    def test_status_values(self):
        self.assertEqual(status_label({"mode": "pi"}), "PI ONLY")
        self.assertEqual(status_label({"mode": "remote", "connected": True}), "CONNECTED")
        self.assertEqual(status_label({"mode": "remote", "connected": False}), "OFFLINE")

    def test_strip_control_chars(self):
        self.assertEqual(safe_text("Pi\nDisplay"), "PiDisplay")

    def test_auto_rotation_enabled_and_disabled(self):
        from ui_helpers import auto_rotate_due
        self.assertTrue(auto_rotate_due({"auto_rotate_pages": True, "rotate_seconds": 8}, 8))
        self.assertFalse(auto_rotate_due({"auto_rotate_pages": True, "rotate_seconds": 8}, 7))
        self.assertFalse(auto_rotate_due({"auto_rotate_pages": False, "rotate_seconds": 8}, 10000))
        self.assertTrue(auto_rotate_due({"rotate_seconds": 8}, 9))
        self.assertFalse(auto_rotate_due({"auto_rotate_pages": False}, 10000))

    def test_storage_page_only_for_remote_multi_nas(self):
        from ui_helpers import page_count_for_state, nas_volumes_for_state
        self.assertEqual(page_count_for_state(None), 2)
        stats = {"nas_volumes": [
            {"name": "NAS Drive 1", "status": "ok"},
            {"name": "NAS Drive 2", "status": "system_disk"},
        ]}
        state = {"server": {"mode": "remote", "connected": True,
                            "stats": stats}}
        self.assertEqual(page_count_for_state(state), 3)
        self.assertEqual(len(nas_volumes_for_state(state)), 2)
        state["server"]["mode"] = "pi"
        self.assertEqual(page_count_for_state(state), 2)
        state["server"]["mode"] = "remote"
        state["server"]["stats"] = {"nas_storage": {"status": "ok"}}
        self.assertEqual(page_count_for_state(state), 2)


if __name__ == "__main__":
    unittest.main()
