"""Two-page Pi dashboard web server. Standard-library HTTP; psutil for telemetry."""

import json
import os
import socket
import time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, parse, request

from dotenv import load_dotenv
from metrics import snapshot

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


def env_int(key, fallback, low, high):
    try:
        return max(low, min(high, int(os.environ.get(key, fallback))))
    except (TypeError, ValueError):
        return fallback


def service_configs():
    try:
        raw = json.loads(os.environ.get("SERVICES_JSON", "[]"))
        if not isinstance(raw, list):
            return []
        valid = []
        for item in raw[:10]:
            if not isinstance(item, dict):
                continue
            name, host, port = item.get("name"), item.get("host"), item.get("port")
            if isinstance(name, str) and isinstance(host, str) and host and name and isinstance(port, int) and 1 <= port <= 65535:
                valid.append({"name": name[:60], "host": host[:255], "port": port})
        return valid
    except (json.JSONDecodeError, TypeError):
        return []


def probe_service(config):
    begin = time.monotonic()
    try:
        with socket.create_connection((config["host"], config["port"]), timeout=0.5):
            reachable = True
    except (OSError, TimeoutError):
        reachable = False
    return {
        "name": config["name"],
        "port": config["port"],
        "online": reachable,
        "latency_ms": round((time.monotonic() - begin) * 1000) if reachable else None,
    }


def fetch_server_metrics(url, token):
    """Fetch optional telemetry from an agent on a trusted private network."""
    url = url.rstrip("/") + "/api/metrics"
    parsed = parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("REMOTE_AGENT_URL must begin with http:// or https://")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = request.Request(url, headers=headers, method="GET")
    start = time.monotonic()
    with request.urlopen(req, timeout=2.0) as response:
        if response.status != 200:
            raise ValueError("Unexpected remote response")
        # Limit the data read; only small JSON snapshots are expected.
        content = response.read(8193)
        if len(content) > 8192:
            raise ValueError("Remote payload too large")
        data = json.loads(content)
        if not isinstance(data, dict) or not isinstance(data.get("cpu_percent"), (int, float)):
            raise ValueError("Remote agent returned invalid metrics")
    return data, round((time.monotonic() - start) * 1000)


def collect_state():
    pi = snapshot()
    url = os.environ.get("REMOTE_AGENT_URL", "").strip()
    remote_token = os.environ.get("REMOTE_AGENT_TOKEN", "").strip()
    server_name = os.environ.get("SERVER_NAME", "My Server")[:80]
    error_message = None
    latency_ms = None
    if not url:
        # Initial setup shows *real Pi metrics*, never pretend they're remote server metrics.
        stats = pi
        mode = "pi"
        connected = None
    else:
        mode = "remote"
        try:
            stats, latency_ms = fetch_server_metrics(url, remote_token)
            connected = True
        except (OSError, ValueError, TimeoutError, error.URLError, json.JSONDecodeError) as exc:
            stats = None
            connected = False
            error_message = str(exc)[:160]
    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "server": {
            "name": server_name,
            "mode": mode,
            "connected": connected,
            "stats": stats,
            "latency_ms": latency_ms,
            "error": error_message,
        },
        "pi": pi,
        "services": [probe_service(service) for service in service_configs()],
        "settings": {
            "refresh_seconds": env_int("REFRESH_SECONDS", 5, 2, 120),
            "rotate_seconds": env_int("ROTATE_SECONDS", 12, 4, 120),
        },
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "static"), **kwargs)

    def do_GET(self):
        if parse.urlsplit(self.path).path == "/api/state":
            try:
                payload = json.dumps(collect_state()).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            except Exception:
                payload = b'{"error":"Unable to collect telemetry"}'
                self.send_response(503)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()


def main():
    host = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
    port = env_int("DASHBOARD_PORT", 8765, 1, 65535)
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Dashboard at http://{host}:{port} (Ctrl+C to stop)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
