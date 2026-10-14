#!/usr/bin/env python3
"""Validate Ubuntu Server settings and render an optional NodeWatch systemd unit.

The token stays in the local .env file; it is never printed in the unit.
"""
import re
import sys
from pathlib import Path

from dotenv import dotenv_values

MARKER = "# Managed by NodeWatch server-agent-autostart.sh"


def render_service(project_directory, username):
    root = Path(project_directory).resolve()
    if not re.fullmatch(r"/[A-Za-z0-9._/+~-]+", str(root)):
        raise ValueError(
            "Use an absolute project path without spaces, backslashes or % "
            "(for example /home/ubuntu/pi-server-dashboard)."
        )
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*[$]?", username):
        raise ValueError("Invalid Linux username for systemd service.")

    python = root / ".venv/bin/python"
    agent = root / "agent.py"
    env_file = root / ".env"
    if not python.is_file():
        raise ValueError(f"Missing {python}. Create the server's .venv first.")
    if not agent.is_file():
        raise ValueError(f"Missing {agent}. Run this from the NodeWatch repository.")
    if not env_file.is_file():
        raise ValueError(f"Missing {env_file}. Copy .env.example and configure the agent.")

    config = dotenv_values(env_file)
    token = config.get("AGENT_TOKEN") or ""
    if not isinstance(token, str) or len(token) < 24 or token.startswith("replace-") or "PASTE_" in token:
        raise ValueError("Set a unique AGENT_TOKEN of at least 24 characters in the Ubuntu Server's .env.")
    host = config.get("AGENT_HOST") or "127.0.0.1"
    port = config.get("AGENT_PORT") or "8766"
    try:
        port_number = int(port)
        if not 1 <= port_number <= 65535:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("AGENT_PORT must be an integer from 1 to 65535.") from None

    if host in ("127.0.0.1", "localhost", "::1"):
        print(
            "Note: AGENT_HOST is loopback-only; the Pi cannot connect over LAN. "
            "Use AGENT_HOST=0.0.0.0 with a firewall restricted to your Pi.",
            file=sys.stderr,
        )

    return (
        f"{MARKER}\n"
        "[Unit]\n"
        "Description=NodeWatch read-only Ubuntu Server metrics agent\n"
        "Wants=network-online.target\n"
        "After=network-online.target\n"
        "\n"
        "[Service]\n"
        "Type=simple\n"
        f"User={username}\n"
        f"WorkingDirectory={root}\n"
        f"ExecStart={python} {agent}\n"
        "Environment=PYTHONUNBUFFERED=1\n"
        "Restart=on-failure\n"
        "RestartSec=5\n"
        "\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    )


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: server_agent_service.py PROJECT_DIR LINUX_USERNAME")
    try:
        print(render_service(sys.argv[1], sys.argv[2]), end="")
    except ValueError as exc:
        raise SystemExit(f"Cannot enable agent startup: {exc}") from None


if __name__ == "__main__":
    main()
