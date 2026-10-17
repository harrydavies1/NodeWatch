"""Presentation helpers for the browser-free Tkinter dashboard."""


def readable_percent(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        return "--"
    return f"{min(100, max(0, value)):.0f}%"


def readable_size(value):
    """Render byte quantities in binary units, without assuming valid telemetry."""
    if isinstance(value, bool) or not isinstance(value, (float, int)) or value < 0:
        return "--"
    amount = float(value)
    for suffix in ("B", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or suffix == "TiB":
            return f"{amount:.0f} {suffix}" if suffix == "B" else f"{amount:.1f} {suffix}"
        amount /= 1024
    return "--"


def readable_uptime(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        return "--"
    minutes = int(value) // 60
    days, remainder = divmod(minutes, 1440)
    hours, mins = divmod(remainder, 60)
    return f"{days}d {hours}h" if days else (f"{hours}h {mins}m" if hours else f"{mins}m")


def safe_text(value, limit=32, default="--"):
    if value is None:
        return default
    # Strip control characters from untrusted hostname/service display values.
    cleaned = "".join(ch for ch in str(value) if ch.isprintable()).strip()
    return cleaned[:limit] if cleaned else default


def status_label(server):
    if not isinstance(server, dict):
        return "WAITING"
    if server.get("mode") == "pi":
        return "PI ONLY"
    return "CONNECTED" if server.get("connected") else "OFFLINE"


def nas_volumes_for_state(state):
    """Return two-drive metrics only in configured remote Server Mode."""
    server = (state or {}).get("server") or {}
    if server.get("mode") != "remote":
        return []
    stats = server.get("stats") or {}
    volumes = stats.get("nas_volumes")
    if not isinstance(volumes, list):
        return []
    return [item for item in volumes[:2] if isinstance(item, dict)]


def page_count_for_state(state):
    """Existing two-page experience stays unchanged until multi-NAS is set."""
    return 3 if nas_volumes_for_state(state) else 2


def auto_rotate_due(settings, elapsed_seconds):
    """Whether the dashboard should advance without user input.

    Older installations without AUTO_ROTATE_PAGES retain automatic rotation.
    """
    if not isinstance(settings, dict) or settings.get("auto_rotate_pages", True) is not True:
        return False
    try:
        seconds = max(4, min(120, int(settings.get("rotate_seconds", 12))))
    except (ValueError, TypeError):
        seconds = 12
    return elapsed_seconds >= seconds
