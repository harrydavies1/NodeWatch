"""Headless regression tests for the optional Windows XP Luna-style renderer."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python-display"))

from simulate import simulated_state  # noqa: E402
from ui_helpers import normalize_theme, page_count_for_state  # noqa: E402
from xp_theme import _blend, draw_xp  # noqa: E402


class DummyCanvas:
    """A tiny Tkinter Canvas stand-in; requires no X server or Tk install."""

    def __init__(self):
        self.calls = []

    def create_rectangle(self, *args, **kwargs):
        self.calls.append(("rectangle", args, kwargs))

    def create_line(self, *args, **kwargs):
        self.calls.append(("line", args, kwargs))

    def create_text(self, *args, **kwargs):
        self.calls.append(("text", args, kwargs))

    def create_oval(self, *args, **kwargs):
        self.calls.append(("oval", args, kwargs))

    def create_polygon(self, *args, **kwargs):
        self.calls.append(("polygon", args, kwargs))

    def texts(self):
        return [call[2]["text"] for call in self.calls if call[0] == "text"]


class XPThemeTests(unittest.TestCase):
    def test_theme_is_opt_in(self):
        self.assertEqual(normalize_theme(None), "dark")
        self.assertEqual(normalize_theme(""), "dark")
        self.assertEqual(normalize_theme("dark"), "dark")
        self.assertEqual(normalize_theme("unrecognized"), "dark")
        self.assertEqual(normalize_theme("  XP "), "xp")
        self.assertEqual(normalize_theme("windows-xp"), "xp")
        self.assertEqual(normalize_theme("luna"), "xp")
        self.assertEqual(normalize_theme(123), "dark")

    def test_colour_gradient_endpoints(self):
        self.assertEqual(_blend("#000000", "#FFFFFF", 0), "#000000")
        self.assertEqual(_blend("#000000", "#FFFFFF", 1), "#FFFFFF")
        self.assertEqual(_blend("#000000", "#FFFFFF", 0.5), "#808080")

    def test_four_real_dashboard_pages_render_with_fake_metrics(self):
        state = simulated_state(pages=4)
        self.assertEqual(page_count_for_state(state), 4)
        headings = (
            "System Overview", "Network & Services",
            "NAS Storage", "HDD Temperatures",
        )
        for page, heading in enumerate(headings):
            with self.subTest(page=page):
                canvas = DummyCanvas()
                draw_xp(canvas, state, page, simulation=True)
                joined = " ".join(canvas.texts())
                self.assertIn(heading, joined)
                self.assertIn("SIMULATION / FAKE DATA", joined)
                self.assertNotIn("start", canvas.texts())
                self.assertGreater(len(canvas.calls), 40)

    def test_two_page_pi_mode_and_three_page_server_mode(self):
        pi = simulated_state(pi_mode=True)
        pi_canvas = DummyCanvas()
        draw_xp(pi_canvas, pi, 1)
        self.assertIn("Network & Services", pi_canvas.texts())
        self.assertNotIn("HDD Temperatures", pi_canvas.texts())

        three = simulated_state(pages=3)
        nas_canvas = DummyCanvas()
        draw_xp(nas_canvas, three, 2)
        self.assertIn("NAS Storage", nas_canvas.texts())

    def test_no_start_button_or_hdd_footer(self):
        state = simulated_state(pages=4)
        for page in range(4):
            with self.subTest(page=page):
                canvas = DummyCanvas()
                draw_xp(canvas, state, page)
                visible = " ".join(canvas.texts()).lower()
                self.assertNotIn("start", visible)
                self.assertNotIn("read-only disk temperatures", visible)
                self.assertIn("nodewatch", visible)

    def test_overview_stat_fonts_have_room_above_progress_bars(self):
        canvas = DummyCanvas()
        state = simulated_state(pages=4)
        draw_xp(canvas, state, 0, width=480, height=320)
        percent_calls = [
            call for call in canvas.calls if call[0] == "text"
            and call[2]["text"].endswith("%")
        ]
        self.assertEqual(len(percent_calls), 3)
        # Scaled down from 20pt to 16pt plus the 0.9 global adjustment.
        self.assertTrue(all(call[2]["font"][1] <= 14 for call in percent_calls))
        self.assertEqual(sorted(int(call[1][1]) for call in percent_calls),
                         [138, 138, 212])
        page_title = [
            call for call in canvas.calls if call[0] == "text"
            and call[2]["text"] == "System Overview"
        ][0]
        self.assertLessEqual(page_title[2]["font"][1], 13)

    def test_unavailable_and_offline_metrics_are_safe(self):
        state = simulated_state(pages=4)
        state["server"]["connected"] = False
        state["server"]["stats"]["hdd_temperatures"][1] = {
            "name": "Missing Drive", "status": "unavailable",
        }
        for page in range(4):
            with self.subTest(page=page):
                canvas = DummyCanvas()
                draw_xp(canvas, state, page)
                self.assertGreater(len(canvas.calls), 40)

        canvas = DummyCanvas()
        draw_xp(canvas, {}, 0)
        self.assertIn("Gathering system metrics...", canvas.texts())

    def test_expanded_canvas_keeps_virtual_layout(self):
        canvas = DummyCanvas()
        draw_xp(canvas, simulated_state(pages=4), 0, 960, 640)
        self.assertGreater(len(canvas.calls), 40)
        self.assertTrue(any(
            call[0] == "rectangle" and call[1][2] > 480
            for call in canvas.calls
        ))


if __name__ == "__main__":
    unittest.main()
