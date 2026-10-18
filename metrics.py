"""Host telemetry shared by the Raspberry Pi dashboard and optional server agent."""

import json
import os
import platform
import socket
import time

import psutil
from hdd_temperatures import hdd_temperatures_snapshot


def cpu_temperature():
    try:
        for group in (psutil.sensors_temperatures() or {}).values():
            for sensor in group:
                if sensor.current is not None:
                    return round(float(sensor.current), 1)
    except (AttributeError, OSError, RuntimeError):
        pass
    return None


def local_ipv4():
    try:
        for interfaces in psutil.net_if_addrs().values():
            for addr in interfaces:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    return addr.address
    except (OSError, RuntimeError):
        pass
    return "Unavailable"


def nas_storage_snapshot(path=None):
    """Inspect the filesystem backing the configured local Samba storage directory.

    When a separate disk is unmounted, don't silently report the root disk
    as if it were the NAS volume.
    """
    path = os.environ.get("NAS_STORAGE_PATH", "") if path is None else path
    path = path.strip() if isinstance(path, str) else ""
    if not path:
        return None
    result = {"path": path, "status": "unavailable"}
    try:
        if not os.path.isabs(path):
            return result
        target = os.stat(path)
        if not os.path.isdir(path):
            return result
        root = os.stat("/")
        disk = psutil.disk_usage(path)
    except (OSError, ValueError):
        return result

    return {
        "path": path,
        "status": "system_disk" if target.st_dev == root.st_dev else "ok",
        "disk_percent": round(disk.percent, 1),
        "disk_used": int(disk.used),
        "disk_total": int(disk.total),
        "disk_free": int(disk.free),
    }



def nas_volumes_snapshot():
    """Return at most two independent NAS filesystems for the small Pi screen.

    Bad configuration is visible as a warning, not as a fake healthy drive.
    The historical single NAS_STORAGE_PATH setting remains supported.
    """
    raw = os.environ.get("NAS_STORAGE_PATHS", "").strip()
    if not raw:
        return []
    try:
        entries = json.loads(raw)
    except (TypeError, ValueError):
        entries = None
    if not isinstance(entries, list) or not 1 <= len(entries) <= 2:
        return [{"name": "NAS CONFIG", "path": "", "status": "invalid"}]

    result = []
    for index, item in enumerate(entries, 1):
        if not isinstance(item, dict):
            return [{"name": "NAS CONFIG", "path": "", "status": "invalid"}]
        name, path = item.get("name"), item.get("path")
        if not isinstance(name, str) or not name.strip() or len(name) > 32:
            name = f"NAS Drive {index}"
        if not isinstance(path, str) or not path.startswith("/") or len(path) > 255:
            result.append({"name": name, "path": str(path)[:120],
                           "status": "invalid"})
            continue
        stats = nas_storage_snapshot(path)
        if stats is None:
            stats = {"path": path, "status": "invalid"}
        result.append({"name": name, **stats})
    return result


def snapshot():
    """Return safe, numeric current-host stats. Does not expose secrets."""
    disk = psutil.disk_usage("/")
    memory = psutil.virtual_memory()
    boot = psutil.boot_time()
    network = psutil.net_io_counters()
    cpu = psutil.cpu_percent(interval=0.12)
    return {
        "hostname": socket.gethostname(),
        "os": platform.system() + " " + platform.release(),
        "ip": local_ipv4(),
        "cpu_percent": round(cpu, 1),
        "cpu_cores": psutil.cpu_count() or 1,
        "memory_percent": round(memory.percent, 1),
        "memory_used": int(memory.used),
        "memory_total": int(memory.total),
        "disk_percent": round(disk.percent, 1),
        "disk_used": int(disk.used),
        "disk_total": int(disk.total),
        "nas_storage": nas_storage_snapshot(),
        "nas_volumes": nas_volumes_snapshot(),
        "hdd_temperatures": hdd_temperatures_snapshot(),
        "temperature_c": cpu_temperature(),
        "uptime_seconds": max(0, int(time.time() - boot)),
        "net_sent": int(network.bytes_sent),
        "net_recv": int(network.bytes_recv),
    }
