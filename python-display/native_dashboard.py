#!/usr/bin/env python3
"""Native two-page Raspberry Pi dashboard (no web browser required).

Requires a functioning X11/Wayland graphical session and python3-tk; an SPI
screen's display driver still needs to be configured in Raspberry Pi OS.
Reads the Pi's .env and optional read-only remote metrics agent.
"""

import argparse
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

try:
    import tkinter as tk
except ImportError:
    raise SystemExit("Tkinter is missing. On Raspberry Pi OS: sudo apt install python3-tk")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from dashboard import collect_state  # noqa: E402  (also loads the root .env file)
from ui_helpers import (  # noqa: E402
    readable_percent,
    readable_size,
    readable_uptime,
    safe_text,
    status_label,
)

BG = "#08101C"
PANEL = "#152238"
BORDER = "#263B54"
INK = "#F2F7FF"
MUTED = "#A3B2C6"
CYAN = "#59D7EB"
GREEN = "#52E0A3"
RED = "#FF7079"
AMBER = "#FFD084"


class Dashboard:
    def __init__(self, windowed=False):
        self.root = tk.Tk()
        self.root.title("NodeWatch - Native Pi Display")
        self.root.configure(bg=BG)
        self.root.attributes("-fullscreen", not windowed)
        if windowed:
            self.root.geometry("480x320")
        self.root.bind("<Escape>", lambda _: self.root.destroy())
        self.root.bind("<Left>", lambda _: self.change_page(-1))
        self.root.bind("<Right>", lambda _: self.change_page(1))
        self.root.bind("<space>", lambda _: self.change_page(1))
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _: self.draw())
        self.canvas.bind("<Button-1>", self.tap)
        self.page = 0
        self.state = None
        self.problem = "Waiting for telemetry"
        self.last_change = time.monotonic()
        self.pending = queue.Queue(maxsize=2)
        self.stop = threading.Event()
        self.root.bind("<Destroy>", self.on_destroy, add=True)
        self.worker = threading.Thread(target=self.telemetry_loop, daemon=True)
        self.worker.start()
        self.root.after(150, self.poll)

    def on_destroy(self, event):
        if event.widget == self.root:
            self.stop.set()

    def telemetry_loop(self):
        # Never touch Tk objects from the background worker.
        while not self.stop.is_set():
            try:
                result = (collect_state(), None)
            except Exception as exc:
                result = (None, safe_text(exc, 110))
            try:
                self.pending.put_nowait(result)
            except queue.Full:
                pass
            interval = 5
            if result[0]:
                interval = result[0].get("settings", {}).get("refresh_seconds", 5)
            try:
                interval = min(120, max(2, int(interval)))
            except (TypeError, ValueError):
                interval = 5
            if self.stop.wait(interval):
                return

    def poll(self):
        if self.stop.is_set():
            return
        while True:
            try:
                new_state, new_error = self.pending.get_nowait()
            except queue.Empty:
                break
            if new_state is not None:
                self.state = new_state
                self.problem = ""
            else:
                self.problem = new_error or "Unable to read metrics"
        settings = (self.state or {}).get("settings", {})
        seconds = settings.get("rotate_seconds", 12)
        try:
            seconds = max(4, min(120, int(seconds)))
        except (ValueError, TypeError):
            seconds = 12
        if time.monotonic() - self.last_change >= seconds:
            self.change_page(1)
        self.draw()
        self.root.after(500, self.poll)

    def change_page(self, direction):
        self.page = (self.page + direction) % 2
        self.last_change = time.monotonic()
        self.draw()

    def tap(self, event):
        if event.x < self.canvas.winfo_width() / 2:
            self.change_page(-1)
        else:
            self.change_page(1)

    def draw(self):
        c = self.canvas
        c.delete("all")
        width = max(c.winfo_width(), 480)
        height = max(c.winfo_height(), 320)
        sx, sy = width / 480, height / 320
        fs = max(0.75, min(sx, sy))

        def panel(x1, y1, x2, y2):
            c.create_rectangle(x1 * sx, y1 * sy, x2 * sx, y2 * sy,
                               fill=PANEL, outline=BORDER, width=1)

        def txt(x, y, msg, size=12, color=INK, bold=False, anchor="nw"):
            c.create_text(x * sx, y * sy, text=safe_text(msg, 80),
                          fill=color, anchor=anchor,
                          font=("DejaVu Sans", max(8, int(size * fs)), "bold" if bold else "normal"))

        def bar(x, y, width, pct):
            c.create_rectangle(x * sx, y * sy, (x + width) * sx, (y + 7) * sy,
                               fill=BORDER, outline="")
            if isinstance(pct, (int, float)) and not isinstance(pct, bool):
                fill = max(0, min(100, pct)) / 100
                if fill > 0:
                    c.create_rectangle(x * sx, y * sy, (x + width * fill) * sx,
                                       (y + 7) * sy, fill=CYAN if fill < 0.85 else AMBER, outline="")

        def metric(x, y, heading, pct, sub):
            panel(x, y, x + 221, y + 76)
            txt(x + 11, y + 9, heading, 11, MUTED, True)
            txt(x + 11, y + 29, readable_percent(pct), 20, INK, True)
            txt(x + 98, y + 36, safe_text(sub, 18), 10, MUTED)
            bar(x + 11, y + 62, 198, pct)

        txt(13, 9, "NODEWATCH", 13, CYAN, True)
        txt(465, 10, datetime.now().strftime("%H:%M"), 12, MUTED, anchor="ne")
        c.create_line(12 * sx, 35 * sy, 468 * sx, 35 * sy, fill=BORDER)

        if not self.state:
            txt(240, 120, "Gathering system metrics...", 16, INK, anchor="center")
            txt(240, 158, self.problem, 11, MUTED, anchor="center")
        elif self.page == 0:
            server = self.state.get("server") or {}
            stats = server.get("stats") or {}
            txt(13, 44, "SYSTEM OVERVIEW", 17, INK, True)
            txt(13, 72, safe_text(stats.get("hostname") or server.get("name"), 34), 11, MUTED)
            status = status_label(server)
            txt(466, 71, status, 10, GREEN if status != "OFFLINE" else RED, True, anchor="ne")
            metric(12, 94, "CPU", stats.get("cpu_percent"),
                   str(stats.get("cpu_cores", "--")) + " cores")
            metric(247, 94, "RAM", stats.get("memory_percent"),
                   readable_size(stats.get("memory_total")))
            metric(12, 182, "DISK", stats.get("disk_percent"),
                   readable_size(stats.get("disk_total")))
            panel(247, 182, 468, 258)
            txt(259, 191, "TEMPERATURE", 11, MUTED, True)
            temp = stats.get("temperature_c")
            if isinstance(temp, (int, float)) and not isinstance(temp, bool):
                txt(259, 212, f"{temp:.1f}°C", 22, INK, True)
            else:
                txt(259, 212, "--", 22, MUTED, True)
            txt(355, 220, "UP " + readable_uptime(stats.get("uptime_seconds")), 10, MUTED)
            nas = stats.get("nas_storage")
            if status != "OFFLINE" and isinstance(nas, dict):
                nas_status = nas.get("status")
                panel(12, 264, 468, 300)
                if nas_status in ("ok", "system_disk"):
                    heading = "NAS STORAGE" if nas_status == "ok" else "NAS ON SYSTEM DISK"
                    txt(23, 270, heading, 10, AMBER if nas_status != "ok" else MUTED, True)
                    txt(226, 269, readable_percent(nas.get("disk_percent")), 13, INK, True)
                    used = readable_size(nas.get("disk_used"))
                    total = readable_size(nas.get("disk_total"))
                    txt(292, 271, used + " / " + total, 10, MUTED)
                    bar(23, 290, 432, nas.get("disk_percent"))
                else:
                    txt(23, 270, "NAS STORAGE UNAVAILABLE", 11, RED, True)
                    txt(23, 285, "Check NAS_STORAGE_PATH and mount", 10, MUTED)
            if status == "OFFLINE":
                txt(14, 262, "Server offline: check agent and network", 10, RED)
        else:
            server = self.state.get("server") or {}
            pi = self.state.get("pi") or {}
            services = self.state.get("services") or []
            status = status_label(server)
            txt(13, 44, "NETWORK & SERVICES", 17, INK, True)
            panel(12, 79, 468, 130)
            txt(23, 87, "SERVER LINK", 10, MUTED, True)
            txt(23, 105, status, 14, GREEN if status != "OFFLINE" else RED, True)
            txt(455, 87, safe_text(server.get("name"), 31), 11, INK, anchor="ne")
            txt(455, 106, str(server.get("latency_ms") or "--") + " ms", 10, MUTED, anchor="ne")
            panel(12, 140, 468, 207)
            txt(23, 147, "THIS RASPBERRY PI", 10, MUTED, True)
            txt(23, 168, safe_text(pi.get("hostname"), 19), 11, INK, True)
            txt(23, 188, safe_text(pi.get("ip"), 22), 10, MUTED)
            txt(240, 165, "CPU " + readable_percent(pi.get("cpu_percent")), 12, CYAN, True)
            txt(355, 165, "RAM " + readable_percent(pi.get("memory_percent")), 12, CYAN, True)
            txt(240, 188, "UP " + readable_uptime(pi.get("uptime_seconds")), 10, MUTED)
            txt(13, 219, "NETWORK (TOTAL SINCE BOOT)", 10, MUTED, True)
            txt(13, 238, "↑  " + readable_size(pi.get("net_sent")), 13, CYAN, True)
            txt(247, 238, "↓  " + readable_size(pi.get("net_recv")), 13, CYAN, True)
            if services:
                txt(13, 264, "PORT CHECKS", 10, MUTED, True)
                for idx, service in enumerate(services[:3]):
                    x = 13 + idx * 153
                    txt(x, 282, safe_text(service.get("name"), 12), 11, INK, True)
                    txt(x + 92, 283, "UP" if service.get("online") else "DOWN", 9,
                        GREEN if service.get("online") else RED, True)
            elif status == "OFFLINE":
                txt(13, 275, "Server agent unreachable", 11, RED)
            else:
                txt(13, 277, "No TCP service checks configured", 10, MUTED)
        c.create_line(12 * sx, 304 * sy, 468 * sx, 304 * sy, fill=BORDER)
        txt(13, 309, "◀", 10, MUTED)
        txt(240, 309, "●  ○" if self.page == 0 else "○  ●", 10, CYAN, anchor="n")
        txt(466, 309, "▶", 10, MUTED, anchor="ne")

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="NodeWatch native dashboard: no browser required")
    parser.add_argument("--windowed", action="store_true", help="480x320 preview instead of fullscreen")
    args = parser.parse_args()
    try:
        Dashboard(windowed=args.windowed).run()
    except tk.TclError as exc:
        raise SystemExit(f"Unable to open a graphical display: {exc}. Check your desktop session and SPI driver.") from exc


if __name__ == "__main__":
    main()
