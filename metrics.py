"""Host telemetry shared by the Raspberry Pi dashboard and optional server agent."""

import platform
import socket
import time

import psutil


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
        "temperature_c": cpu_temperature(),
        "uptime_seconds": max(0, int(time.time() - boot)),
        "net_sent": int(network.bytes_sent),
        "net_recv": int(network.bytes_recv),
    }
