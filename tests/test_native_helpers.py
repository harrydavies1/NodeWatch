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


if __name__ == "__main__":
    unittest.main()
