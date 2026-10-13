"""Optional read-only agent: run on a separate server to report its host metrics."""

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import load_dotenv
from metrics import snapshot

load_dotenv(Path(__file__).resolve().parent / ".env")


class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        expected = os.environ.get("AGENT_TOKEN", "")
        provided = self.headers.get("Authorization", "")
        if self.path != "/api/metrics":
            self.send_error(404)
            return
        if not expected or not hmac.compare_digest(provided, "Bearer " + expected):
            self.send_error(401, "Unauthorized")
            return
        payload = json.dumps(snapshot()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    if not os.environ.get("AGENT_TOKEN", "").strip():
        raise SystemExit("Set a strong AGENT_TOKEN in .env before starting the agent.")
    host = os.environ.get("AGENT_HOST", "127.0.0.1")
    port = int(os.environ.get("AGENT_PORT", "8766"))
    server = ThreadingHTTPServer((host, port), AgentHandler)
    print(f"Telemetry agent listening on {host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
