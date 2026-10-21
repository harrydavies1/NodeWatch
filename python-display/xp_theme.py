"""Windows XP Luna-inspired canvas theme for NodeWatch.

All artwork uses vector shapes drawn by Tkinter: no external fonts, Windows
assets, image files, Pillow, network access or third-party dependencies.
The normal dark dashboard remains a separate, unchanged renderer.
"""

from datetime import datetime

from ui_helpers import (
    hdd_temperatures_for_state,
    nas_volumes_for_state,
    page_count_for_state,
    readable_percent,
    readable_size,
    readable_uptime,
    safe_text,
    status_label,
)

BLUE = "#0B59D9"
BLUE_DARK = "#00378B"
BLUE_LIGHT = "#80BEFF"
BLUE_TEXT = "#153E80"
PANEL = "#FFFDF5"
PANEL_BORDER = "#709BD4"
TEXT = "#183059"
MUTED = "#64758B"
WHITE = "#FFFFFF"
GREEN = "#2E8E30"
RED = "#B82E34"
AMBER = "#AA6200"


def _blend(start, end, fraction):
    """Blend two #RRGGBB colours; keep the renderer independent of Tk."""
    fraction = max(0.0, min(1.0, fraction))
    a = tuple(int(start[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(end[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(x + (y - x) * fraction):02X}" for x, y in zip(a, b))


def draw_xp(canvas, state, page, width=480, height=320, simulation=False,
            menu_open=False):
    """Draw a 480x320-friendly Luna-style window, taskbar and NodeWatch pages.

    The menu is decorative until Dashboard.tap() handles its hitboxes.
    Rendering accepts a minimal Tkinter-canvas-compatible object for testing.
    """
    state = state or {}
    width = max(1, width)
    height = max(1, height)
    sx, sy = width / 480, height / 320
    scale = max(0.75, min(sx, sy))
    page_count = page_count_for_state(state)
    server = state.get("server") or {}
    stats = server.get("stats") or {}
    status = status_label(server)
    is_online = status != "OFFLINE"
    page = max(0, min(page_count - 1, page))
    page_names = ["System Overview", "Network & Services"]
    if nas_volumes_for_state(state):
        page_names.append("NAS Storage")
    if hdd_temperatures_for_state(state):
        page_names.append("HDD Temperatures")

    def rect(x1, y1, x2, y2, fill, outline="", width=1):
        canvas.create_rectangle(x1 * sx, y1 * sy, x2 * sx, y2 * sy,
                                fill=fill, outline=outline, width=width)

    def line(x1, y1, x2, y2, fill, width=1):
        canvas.create_line(x1 * sx, y1 * sy, x2 * sx, y2 * sy,
                           fill=fill, width=width)

    def polygon(points, fill, outline=""):
        canvas.create_polygon(
            *[coord * (sx if i % 2 == 0 else sy)
              for i, coord in enumerate(points)],
            fill=fill, outline=outline,
        )

    def oval(x1, y1, x2, y2, fill, outline=""):
        canvas.create_oval(x1 * sx, y1 * sy, x2 * sx, y2 * sy,
                           fill=fill, outline=outline)

    def text(x, y, value, size=11, color=TEXT, bold=False, anchor="nw",
             italic=False):
        canvas.create_text(
            x * sx, y * sy, text=safe_text(value, 80),
            fill=color, anchor=anchor,
            font=("Tahoma", max(8, int(size * scale)),
                  "bold italic" if italic and bold else
                  "bold" if bold else "italic" if italic else "normal"),
        )

    def gradient(x1, y1, x2, y2, top, bottom, steps=24):
        for i in range(steps):
            a = y1 + (y2 - y1) * i / steps
            b = y1 + (y2 - y1) * (i + 1) / steps + 0.2
            rect(x1, a, x2, b, _blend(top, bottom, i / max(1, steps - 1)))

    def box(x1, y1, x2, y2, caption=None):
        # Beige translucent-looking panels and raised XP border.
        rect(x1, y1, x2, y2, "#BBD5F1", "#4D84C4")
        rect(x1 + 2, y1 + 2, x2 - 2, y2 - 2, PANEL, "#D5E2F0")
        line(x1 + 2, y1 + 2, x2 - 3, y1 + 2, WHITE)
        if caption:
            gradient(x1 + 4, y1 + 4, x2 - 4, y1 + 24,
                     "#E9F5FF", "#D3E7FD", steps=7)
            line(x1 + 4, y1 + 24, x2 - 4, y1 + 24, "#AAC8E6")
            text(x1 + 11, y1 + 7, caption, 10, BLUE_TEXT, True)

    def bar(x, y, bar_width, percent, warning=False):
        rect(x, y, x + bar_width, y + 12, WHITE, "#7197BE")
        if isinstance(percent, (int, float)) and not isinstance(percent, bool):
            p = max(0, min(100, percent))
            fill_width = (bar_width - 4) * p / 100
            # Chunky segmented progress bar evokes the XP Luna controls.
            for step in range(int(fill_width // 10) + 1):
                dx = step * 10
                remainder = min(8, fill_width - dx)
                if remainder <= 0:
                    break
                rect(x + 2 + dx, y + 2, x + 2 + dx + remainder, y + 10,
                     "#EE9B2B" if warning else "#42A8F0")
                line(x + 2 + dx, y + 2,
                     x + 2 + dx + remainder, y + 2,
                     "#FFE3A9" if warning else "#A4DFFD")

    def state_color(label):
        return RED if label == "OFFLINE" else GREEN if label in ("CONNECTED", "PI ONLY") else AMBER

    def drive_name(item, default="NAS DRIVE"):
        return safe_text(item.get("name"), 29, default)

    # Desktop/wallpaper. A bright blue sky and green rolling hills evoke Bliss
    # without requiring or distributing Microsoft image assets.
    gradient(0, 0, 480, 289, "#58A8F2", "#CDEFFF", steps=42)
    polygon([0, 228, 80, 211, 154, 222, 251, 201,
             345, 215, 480, 184, 480, 289, 0, 289], "#82C84A")
    polygon([0, 263, 101, 234, 186, 251, 314, 229,
             406, 246, 480, 229, 480, 289, 0, 289], "#4C9F29")

    # Main faux XP application window.
    rect(5, 6, 475, 288, "#165EC6", BLUE_DARK, 2)
    gradient(8, 8, 472, 37, "#1264DC", "#0B48B8", steps=14)
    line(9, 9, 471, 9, BLUE_LIGHT, 2)
    oval(14, 13, 34, 33, "#FEFDFC", "#A5CEEE")
    polygon([17, 22, 23, 17, 30, 21, 23, 28], "#2D8A4F")
    text(40, 15, "NodeWatch - System Monitor", 12, WHITE, True)
    # Minimize / maximize / close boxes match the iconic blue XP chrome.
    for index, symbol in enumerate(("–", "□", "×")):
        left = 400 + index * 23
        rect(left, 12, left + 20, 32,
             "#DF4945" if index == 2 else "#478CE8",
             "#FFF5EF")
        line(left + 2, 14, left + 17, 14, "#A8D3FF" if index != 2 else "#FFB3A4")
        text(left + 10, 14, symbol, 12, WHITE, True, anchor="n")

    gradient(9, 37, 471, 61, "#FCFCF7", "#E6E9DE", steps=10)
    line(9, 60, 471, 60, "#9DA6A6")
    text(18, 43, "File", 10, TEXT)
    text(56, 43, "View", 10, TEXT)
    text(99, 43, "Help", 10, TEXT)
    if simulation:
        rect(288, 41, 465, 57, "#FFF0BF", "#CAA65F")
        text(293, 43, "SIMULATION / FAKE DATA", 9, "#764400", True)
    else:
        text(460, 43, "LIVE MONITOR", 10, BLUE_TEXT, True, anchor="ne")

    # Content area, a light XP Explorer-style workspace.
    rect(9, 61, 471, 282, "#D8E9FB")
    gradient(10, 61, 470, 101, "#FFFFFF", "#C9DFF7", steps=12)
    text(19, 68, page_names[page], 17, BLUE_TEXT, True)
    text(20, 89, safe_text(server.get("name") or "NodeWatch", 44),
         9, MUTED)
    text(459, 89, status, 10, state_color(status), True, anchor="ne")
    line(14, 101, 466, 101, "#83ABDB")

    if not state:
        box(16, 112, 464, 265, "Welcome to NodeWatch")
        text(240, 173, "Gathering system metrics...", 15, BLUE_TEXT, True,
             anchor="center")
    elif page == 0:
        box(16, 110, 235, 177, "CPU USAGE")
        text(27, 138, readable_percent(stats.get("cpu_percent")), 20, BLUE_TEXT, True)
        text(125, 145, f'{stats.get("cpu_cores", "--")} cores', 10, MUTED)
        bar(27, 160, 196, stats.get("cpu_percent"))

        box(245, 110, 464, 177, "MEMORY")
        text(256, 138, readable_percent(stats.get("memory_percent")), 20, BLUE_TEXT, True)
        text(353, 145, readable_size(stats.get("memory_total")), 10, MUTED)
        bar(256, 160, 196, stats.get("memory_percent"))

        box(16, 184, 235, 251, "SYSTEM DISK")
        text(27, 211, readable_percent(stats.get("disk_percent")), 20, BLUE_TEXT, True)
        text(125, 219, readable_size(stats.get("disk_total")), 10, MUTED)
        bar(27, 234, 196, stats.get("disk_percent"))

        box(245, 184, 464, 251, "TEMPERATURE")
        temp = stats.get("temperature_c")
        if isinstance(temp, (int, float)) and not isinstance(temp, bool):
            text(257, 212, f"{temp:.1f}°C", 19, BLUE_TEXT, True)
        else:
            text(257, 212, "Unavailable", 14, MUTED, True)
        text(259, 235, "Up " + readable_uptime(stats.get("uptime_seconds")), 9, MUTED)
        text(20, 261, "Computer status:", 9, MUTED)
        text(110, 261, "Connected" if is_online else "Server offline",
             9, GREEN if is_online else RED, True)

    elif page == 1:
        pi = state.get("pi") or {}
        services = state.get("services") or []
        box(16, 110, 464, 155, "SERVER CONNECTION")
        text(28, 137, status, 13, state_color(status), True)
        text(451, 140, f'{server.get("latency_ms") if server.get("latency_ms") is not None else "--"} ms',
             10, MUTED, anchor="ne")
        box(16, 162, 464, 220, "LOCAL DEVICE")
        text(28, 190, safe_text(pi.get("hostname"), 23), 12, BLUE_TEXT, True)
        text(28, 205, safe_text(pi.get("ip"), 25), 9, MUTED)
        text(261, 189, "CPU " + readable_percent(pi.get("cpu_percent")), 11, BLUE_TEXT, True)
        text(359, 189, "RAM " + readable_percent(pi.get("memory_percent")), 11, BLUE_TEXT, True)
        box(16, 227, 464, 273, "NETWORK TOTALS")
        text(28, 253, "Sent " + readable_size(pi.get("net_sent")), 11, BLUE_TEXT, True)
        text(242, 253, "Received " + readable_size(pi.get("net_recv")), 11, BLUE_TEXT, True)
        if services:
            name = safe_text(services[0].get("name"), 14)
            text(352, 232, name + "  " + ("UP" if services[0].get("online") else "DOWN"),
                 9, GREEN if services[0].get("online") else RED, True)

    elif page_names[page] == "NAS Storage":
        volumes = nas_volumes_for_state(state)
        for index, volume in enumerate(volumes[:2]):
            y = 110 + index * 83
            box(16, y, 464, y + 77, drive_name(volume))
            text(27, y + 28, safe_text(volume.get("path"), 35), 9, MUTED)
            if volume.get("status") == "ok" and is_online:
                text(447, y + 7, readable_percent(volume.get("disk_percent")),
                     17, BLUE_TEXT, True, anchor="ne")
                text(27, y + 43,
                     readable_size(volume.get("disk_used")) + " used / "
                     + readable_size(volume.get("disk_total")), 10, TEXT)
                text(449, y + 43,
                     readable_size(volume.get("disk_free")) + " free",
                     9, MUTED, anchor="ne")
                bar(27, y + 60, 419, volume.get("disk_percent"))
            else:
                text(27, y + 43, "MOUNT MISSING / DISK UNAVAILABLE",
                     11, RED, True)
        if not volumes or not is_online:
            text(240, 264, "Server storage data unavailable", 10, RED, anchor="center")

    else:
        drives = hdd_temperatures_for_state(state)
        for index, drive in enumerate(drives[:2]):
            y = 110 + index * 83
            box(16, y, 464, y + 77, drive_name(drive, "HDD"))
            text(28, y + 30, safe_text(drive.get("device"), 38), 10, MUTED)
            temp = drive.get("temperature_c")
            good = (drive.get("status") == "ok" and is_online
                    and isinstance(temp, (int, float)) and not isinstance(temp, bool))
            if good:
                label = "HOT" if temp >= 50 else "WARM" if temp >= 45 else "NORMAL"
                colour = RED if temp >= 50 else AMBER if temp >= 45 else GREEN
                text(449, y + 9, f"{temp:.1f}°C", 20, colour, True, anchor="ne")
                text(28, y + 53, label + "  -  SMART temperature",
                     10, colour, True)
                bar(281, y + 56, 168,
                    max(0, min(100, (temp - 20) / 40 * 100)),
                    warning=temp >= 45)
            else:
                label = "DRIVE SLEEPING" if drive.get("status") == "standby" else \
                        "INVALID CONFIG" if drive.get("status") == "invalid" else \
                        "TEMPERATURE UNAVAILABLE"
                text(28, y + 51, label, 10, AMBER if label == "DRIVE SLEEPING" else RED, True)
        text(23, 263, "Read-only disk temperatures - refresh every 60 seconds",
             9, MUTED)

    # Windows XP signature bottom taskbar, Start button and system tray.
    gradient(0, 286, 480, 320, "#438FED", "#1452CA", steps=15)
    line(0, 287, 480, 287, "#A6D8FF", 2)
    oval(-26, 287, 113, 327, "#1C7227", "#74C777")
    oval(-26, 288, 107, 323, "#319C39", "#74C777")
    polygon([17, 298, 24, 294, 31, 299, 23, 306], "#FFFFFF")
    text(40, 294, "start", 17, WHITE, True, italic=True)
    rect(117, 293, 368, 316, "#1D58B7", "#74B5FA")
    text(128, 297, "NodeWatch  -  " + page_names[page], 10, WHITE, True)
    gradient(379, 288, 480, 319, "#61BDF5", "#2681DA", steps=9)
    line(379, 290, 379, 319, "#AFDFFF")
    text(386, 298, f"{page + 1}/{page_count}", 9, WHITE, True)
    text(468, 298, datetime.now().strftime("%H:%M"), 10, WHITE, True, anchor="ne")

    if menu_open:
        # Clickable Start-style page launcher (Dashboard.tap handles hit testing).
        entries = page_names[:4]
        rect(7, 130, 229, 287, "#EDF4FF", BLUE_DARK, 2)
        gradient(9, 133, 227, 157, "#4F9BFF", "#0E4BB4", steps=8)
        text(21, 138, "NodeWatch", 13, WHITE, True)
        text(216, 142, "PAGES", 9, WHITE, anchor="ne")
        for i, name in enumerate(entries):
            y = 159 + i * 29
            if y + 26 > 285:
                break
            rect(11, y, 225, y + 26,
                 "#DCEBFF" if i == page else "#F7FAFF",
                 "#AFC7E9")
            oval(18, y + 6, 31, y + 19, BLUE if i != page else GREEN)
            text(39, y + 5, name, 10, BLUE_TEXT, i == page)
