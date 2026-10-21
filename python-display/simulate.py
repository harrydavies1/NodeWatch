#!/usr/bin/env python3
"""Cross-platform NodeWatch GUI simulator, using fake data and the real Tkinter UI.

Run with Python 3 + Tkinter. No agent, Raspberry Pi, server, SMART access,
.env file, psutil, python-dotenv, network connection or pip installs required.
"""

import argparse
import math
import time
from datetime import datetime, timezone


def simulated_state(
    *,
    elapsed_seconds=0.0,
    pages=4,
    auto_rotate=False,
    rotate_seconds=12,
    refresh_seconds=2,
    pi_mode=False,
):
    """Return a NodeWatch-shaped snapshot with explicitly *fake* numbers.

    This is deliberately separate from dashboard.collect_state() so previews
    cannot accidentally make remote requests or read the host's actual stats.
    """
    if pages not in (2, 3, 4):
        raise ValueError("pages must be 2, 3, or 4")
    elapsed = max(0.0, float(elapsed_seconds))
    phase = elapsed / 9.0

    def wave(center, amplitude, offset=0):
        return round(center + amplitude * math.sin(phase + offset), 1)

    gib = 1024**3
    server_stats = {
        "hostname": "demo-homeserver",
        "os": "Linux (SIMULATED)",
        "ip": "192.0.2.10",
        "cpu_percent": wave(28, 15),
        "cpu_cores": 4,
        "memory_percent": wave(41, 8, 0.8),
        "memory_used": 5 * gib,
        "memory_total": 12 * gib,
        "disk_percent": wave(37, 2, 1.2),
        "disk_used": 90 * gib,
        "disk_total": 240 * gib,
        "temperature_c": wave(39, 4, 0.5),
        "uptime_seconds": 12 * 86400 + 5 * 3600 + int(elapsed),
        "nas_storage": None,
        "nas_volumes": [],
        "hdd_temperatures": [],
        "net_sent": 20 * gib + int(elapsed * 50000),
        "net_recv": 30 * gib + int(elapsed * 75000),
    }

    # Enable the optional screens with exactly the same metrics shape as the agent.
    if pages >= 3 and not pi_mode:
        server_stats["nas_volumes"] = [
            {
                "name": "NAS Drive 1",
                "path": "/srv/nas/drive1",
                "status": "ok",
                "disk_percent": 16.4,
                "disk_used": int(75 * gib),
                "disk_total": int(458 * gib),
                "disk_free": int(383 * gib),
            },
            {
                "name": "NAS Drive 2",
                "path": "/srv/nas/drive2",
                "status": "ok",
                "disk_percent": 43.5,
                "disk_used": int(199 * gib),
                "disk_total": int(458 * gib),
                "disk_free": int(259 * gib),
            },
        ]
    if pages >= 4 and not pi_mode:
        server_stats["hdd_temperatures"] = [
            {
                "name": "NAS Drive 1",
                "device": "/dev/sdb",
                "status": "ok",
                "temperature_c": wave(34, 1.3, 0.3),
            },
            {
                "name": "NAS Drive 2",
                "device": "/dev/sdc",
                "status": "ok",
                "temperature_c": wave(51, 1.5, 0.9),
            },
        ]

    pi = {
        "hostname": "demo-raspberrypi",
        "os": "Linux (SIMULATED)",
        "ip": "192.0.2.20",
        "cpu_percent": wave(17, 10, 0.4),
        "cpu_cores": 4,
        "memory_percent": wave(35, 7, 1.1),
        "memory_used": gib,
        "memory_total": 4 * gib,
        "disk_percent": 22.5,
        "disk_used": 15 * gib,
        "disk_total": 64 * gib,
        "temperature_c": wave(45, 2, 0.2),
        "uptime_seconds": 2 * 86400 + 8 * 3600 + int(elapsed),
        "net_sent": 4 * gib + int(elapsed * 25000),
        "net_recv": 9 * gib + int(elapsed * 50000),
        "nas_storage": None,
        "nas_volumes": [],
        "hdd_temperatures": [],
    }

    is_pi = bool(pi_mode)
    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "server": {
            "name": "Demo Raspberry Pi" if is_pi else "Demo Ubuntu Server",
            "mode": "pi" if is_pi else "remote",
            "connected": None if is_pi else True,
            "stats": pi if is_pi else server_stats,
            "latency_ms": None if is_pi else 3,
            "error": None,
        },
        "pi": pi,
        "services": [
            {"name": "SSH", "port": 22, "online": True, "latency_ms": 1},
            {"name": "Music", "port": 4533, "online": True, "latency_ms": 2},
            {"name": "Example", "port": 8080, "online": False, "latency_ms": None},
        ],
        "settings": {
            "refresh_seconds": max(2, min(120, int(refresh_seconds))),
            "rotate_seconds": max(4, min(120, int(rotate_seconds))),
            "auto_rotate_pages": bool(auto_rotate),
        },
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Preview NodeWatch's real Tkinter pages with FAKE stats (no server required)."
    )
    parser.add_argument(
        "--pages", type=int, choices=(2, 3, 4), default=4,
        help="number of pages to simulate (default: 4)",
    )
    parser.add_argument(
        "--pi-mode", action="store_true",
        help="preview standalone Pi Mode (always 2 pages)",
    )
    parser.add_argument(
        "--auto-rotate", action="store_true",
        help="automatically switch pages; off by default",
    )
    parser.add_argument(
        "--rotate-seconds", type=int, default=12,
        help="seconds between automatic page changes (4-120; default: 12)",
    )
    parser.add_argument(
        "--refresh-seconds", type=int, default=2,
        help="seconds between fake telemetry updates (2-120; default: 2)",
    )
    parser.add_argument(
        "--fullscreen", action="store_true",
        help="use fullscreen instead of the default 480x320 preview window",
    )
    parser.add_argument(
        "--theme", choices=("dark", "xp"), default="dark",
        help="preview the classic dark UI or optional Windows XP Luna theme",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    start = time.monotonic()

    def get_fake_data():
        return simulated_state(
            elapsed_seconds=time.monotonic() - start,
            pages=args.pages,
            pi_mode=args.pi_mode,
            auto_rotate=args.auto_rotate,
            rotate_seconds=args.rotate_seconds,
            refresh_seconds=args.refresh_seconds,
        )

    # Import Tkinter only when opening a window. Even --help works on a
    # headless machine or minimal Python installation.
    from native_dashboard import Dashboard, tk

    try:
        Dashboard(
            windowed=not args.fullscreen,
            collector=get_fake_data,
            simulation=True,
            theme=args.theme,
        ).run()
    except tk.TclError as exc:
        raise SystemExit(
            "Unable to open the simulator window. Install or enable Tkinter "
            "and start from a graphical desktop (macOS, Windows or Linux). "
            f"Details: {exc}"
        ) from exc


if __name__ == "__main__":
    main()
