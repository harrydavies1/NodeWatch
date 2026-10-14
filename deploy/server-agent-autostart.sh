#!/usr/bin/env bash
# Optional Ubuntu Server systemd startup helper. Cloning never enables it.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
UNIT="server-agent.service"
SERVICE_FILE="/etc/systemd/system/$UNIT"
MARKER="# Managed by NodeWatch server-agent-autostart.sh"

usage() {
  echo "Usage: bash deploy/server-agent-autostart.sh {enable|disable|status|logs}" >&2
  exit 2
}

if [[ "$#" -ne 1 ]]; then
  usage
fi

case "$1" in
  enable)
    if [[ "$EUID" -eq 0 ]]; then
      echo "Run as your normal Ubuntu Server user, without sudo; the helper uses sudo where needed." >&2
      exit 1
    fi
    if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
      echo "Missing executable $ROOT/.venv/bin/python. Install dependencies on Ubuntu Server first." >&2
      exit 1
    fi
    tmp="$(mktemp)"
    trap 'rm -f -- "$tmp"' EXIT
    "$ROOT/.venv/bin/python" "$ROOT/deploy/server_agent_service.py" "$ROOT" "$(id -un)" > "$tmp"
    if sudo test -e "$SERVICE_FILE" && ! sudo grep -Fqx "$MARKER" "$SERVICE_FILE"; then
      echo "Existing $SERVICE_FILE was not created by this helper; leaving it untouched." >&2
      echo "For an existing manually installed unit, use: sudo systemctl enable --now $UNIT" >&2
      exit 1
    fi
    sudo install -m 0644 "$tmp" "$SERVICE_FILE"
    sudo systemctl daemon-reload
    sudo systemctl enable --now "$UNIT"
    echo "Enabled $UNIT now and on each Ubuntu boot."
    ;;
  disable)
    if ! sudo test -e "$SERVICE_FILE"; then
      echo "No $SERVICE_FILE exists; nothing to disable."
      exit 0
    fi
    if ! sudo grep -Fqx "$MARKER" "$SERVICE_FILE"; then
      echo "Refusing to manage an existing systemd unit not created by this helper." >&2
      echo "For a manually installed unit, use: sudo systemctl disable --now $UNIT" >&2
      exit 1
    fi
    sudo systemctl disable --now "$UNIT"
    echo "Stopped and disabled $UNIT. The unit file remains for re-enabling."
    ;;
  status)
    enabled="$(systemctl is-enabled "$UNIT" 2>/dev/null || true)"
    active="$(systemctl is-active "$UNIT" 2>/dev/null || true)"
    echo "Boot setting: ${enabled:-not-installed}"
    echo "Running now:  ${active:-not-installed}"
    systemctl --no-pager --full status "$UNIT" || true
    ;;
  logs)
    sudo journalctl -u "$UNIT" -n 50 --no-pager
    ;;
  *)
    usage
    ;;
esac
