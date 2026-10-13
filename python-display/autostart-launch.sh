#!/usr/bin/env bash
# Runs in the logged-in graphical desktop session, inheriting DISPLAY/XAUTHORITY.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$HOME/nodewatch-autostart.log"
sleep 8
echo "[$(date -Is)] Starting NodeWatch Tkinter display" >> "$LOG"
exec /bin/bash "$ROOT/python-display/start-native.sh" >> "$LOG" 2>&1
