"""Headless tests for the optional cross-platform NodeWatch screen simulator."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPLAY = ROOT / "python-display"
sys.path.insert(0, str(DISPLAY))

from simulate import build_parser, simulated_state  # noqa: E402
from ui_helpers import page_count_for_state  # noqa: E402


class SimulatorTests(unittest.TestCase):
    def test_four_demo_pages_and_real_dashboard_schema(self):
        state = simulated_state(elapsed_seconds=0, pages=4)
        self.assertEqual(page_count_for_state(state), 4)
        self.assertEqual(state["server"]["mode"], "remote")
        self.assertTrue(state["server"]["connected"])
        self.assertEqual(len(state["server"]["stats"]["nas_volumes"]), 2)
        self.assertEqual(len(state["server"]["stats"]["hdd_temperatures"]), 2)
        self.assertEqual(len(state["services"]), 3)
        self.assertFalse(state["settings"]["auto_rotate_pages"])

    def test_two_and_three_page_previews(self):
        self.assertEqual(page_count_for_state(simulated_state(pages=2)), 2)
        three = simulated_state(pages=3)
        self.assertEqual(page_count_for_state(three), 3)
        self.assertEqual(three["server"]["stats"]["hdd_temperatures"], [])

    def test_pi_mode_is_standalone_and_two_pages(self):
        state = simulated_state(pages=4, pi_mode=True)
        self.assertEqual(page_count_for_state(state), 2)
        self.assertEqual(state["server"]["mode"], "pi")
        self.assertIsNone(state["server"]["connected"])
        self.assertIs(state["server"]["stats"], state["pi"])

    def test_fake_numbers_refresh_and_settings_propagate(self):
        first = simulated_state(elapsed_seconds=0)
        later = simulated_state(
            elapsed_seconds=28, auto_rotate=True, rotate_seconds=8,
            refresh_seconds=3,
        )
        self.assertNotEqual(first["server"]["stats"]["cpu_percent"],
                            later["server"]["stats"]["cpu_percent"])
        self.assertGreater(later["server"]["stats"]["uptime_seconds"],
                           first["server"]["stats"]["uptime_seconds"])
        self.assertEqual(later["settings"], {
            "refresh_seconds": 3,
            "rotate_seconds": 8,
            "auto_rotate_pages": True,
        })
        self.assertEqual(later["server"]["stats"]["hdd_temperatures"][0]["status"], "ok")

    def test_invalid_page_count_is_rejected(self):
        for invalid in (0, 1, 5):
            with self.subTest(pages=invalid), self.assertRaises(ValueError):
                simulated_state(pages=invalid)

    def test_cli_options(self):
        args = build_parser().parse_args([
            "--pages", "3", "--fullscreen", "--auto-rotate",
            "--rotate-seconds", "8", "--refresh-seconds", "5",
        ])
        self.assertEqual(args.pages, 3)
        self.assertTrue(args.fullscreen)
        self.assertTrue(args.auto_rotate)
        self.assertEqual(args.rotate_seconds, 8)
        self.assertEqual(args.refresh_seconds, 5)
        with self.assertRaises(SystemExit):
            build_parser().parse_args(["--pages", "7"])

    def test_help_needs_no_third_party_packages_or_display(self):
        # -S skips site-packages; --help exits before importing Tkinter.
        result = subprocess.run(
            [sys.executable, "-S", str(DISPLAY / "simulate.py"), "--help"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--pages", result.stdout)
        self.assertIn("--auto-rotate", result.stdout)


if __name__ == "__main__":
    unittest.main()
