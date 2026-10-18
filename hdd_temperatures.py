"""Optional HDD temperatures via smartctl, read-only and cached for 60 seconds.

The Ubuntu agent runs as an unprivileged user. A narrowly-scoped sudoers entry
must permit only the explicitly configured smartctl commands; see docs/HDD_TEMPERATURES.md.
Never use shell=True or accept device paths as command-line switches.
"""

import json
import os
import re
import subprocess
import threading
import time

# Stable /dev/disk/by-id paths are preferred; /dev/sdX is allowed for simple setups.
_DEVICE = re.compile(r"^/dev/(?:sd[a-z]+|disk/by-id/(?:ata-|wwn-)[A-Za-z0-9_.:+-]+)$")
_CACHE_SECONDS = 60
_cache = {}
_cache_lock = threading.Lock()


def configured_hdd_drives():
    """At most two drives. Invalid configuration is visible on the Pi display."""
    raw = os.environ.get("HDD_TEMP_DRIVES", "").strip()
    if not raw:
        return []
    try:
        items = json.loads(raw)
    except (TypeError, ValueError):
        items = None
    if not isinstance(items, list) or not 1 <= len(items) <= 2:
        return [{"name": "HDD CONFIG", "status": "invalid"}]

    result = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            return [{"name": "HDD CONFIG", "status": "invalid"}]
        name, device = item.get("name"), item.get("device")
        if not isinstance(name, str) or not name.strip():
            name = f"NAS Drive {index}"
        name = name.strip()[:32]
        if not isinstance(device, str) or not _DEVICE.fullmatch(device):
            result.append({"name": name, "status": "invalid"})
        else:
            result.append({"name": name, "device": device})
    return result


def _valid_temp(value):
    # Includes safeguards against bogus SMART attributes and invalid JSON values.
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 < value < 100


def parse_temperature(data):
    """Handle smartctl's normalised temperature field and ATA 194/190 raw values."""
    if not isinstance(data, dict):
        return None
    value = (data.get("temperature") or {}).get("current")
    if _valid_temp(value):
        return round(float(value), 1)
    table = (data.get("ata_smart_attributes") or {}).get("table") or []
    if not isinstance(table, list):
        return None
    for attr_id in (194, 190):
        for item in table:
            if not isinstance(item, dict) or item.get("id") != attr_id:
                continue
            raw = item.get("raw") or {}
            if not isinstance(raw, dict):
                continue
            # raw.value can be packed Min/Max data; use the displayed reading.
            text = raw.get("string", "")
            match = re.match(r"^\s*(-?\d+(?:\.\d+)?)", str(text))
            if match:
                number = float(match.group(1))
                if _valid_temp(number):
                    return round(number, 1)
    return None


def _read_temperature(device):
    # -n standby avoids waking sleeping ATA disks for a dashboard refresh.
    command = ["sudo", "-n", "/usr/sbin/smartctl", "-j", "-A", "-n", "standby", device]
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=4, check=False)
        data = json.loads(process.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {"status": "unavailable"}

    if not isinstance(data, dict):
        return {"status": "unavailable"}
    mode = str(data.get("power_mode", "")).lower()
    messages = data.get("smartctl", {}).get("messages", [])
    if not isinstance(messages, list):
        messages = []
    detail = " ".join(str(m.get("string", "")) for m in messages if isinstance(m, dict)).lower()
    if "standby" in mode or "sleep" in mode or "standby" in detail or "sleep mode" in detail:
        return {"status": "standby"}

    value = parse_temperature(data)
    if value is None:
        return {"status": "unavailable"}
    return {"status": "ok", "temperature_c": value}


def hdd_temperatures_snapshot():
    """Report configured HDDs while limiting privileged SMART reads to once/minute."""
    readings = []
    for drive in configured_hdd_drives():
        device = drive.get("device")
        if not device:
            readings.append(drive)
            continue
        now = time.monotonic()
        with _cache_lock:
            cached = _cache.get(device)
            if cached is None or now - cached[0] >= _CACHE_SECONDS:
                cached = (now, _read_temperature(device))
                _cache[device] = cached
        readings.append({**drive, **cached[1]})
    return readings
