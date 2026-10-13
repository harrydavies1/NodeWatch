#!/usr/bin/env bash
# Optional XDG desktop-session autostart for the native Tkinter dashboard.
# No startup configuration is installed until the user runs "enable".
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
ENTRY_DIR="$CONFIG/autostart"
ENTRY="$ENTRY_DIR/nodewatch.desktop"
BACKUP_DIR="$CONFIG/nodewatch"
BACKUP="$BACKUP_DIR/nodewatch.desktop.disabled"
LAUNCHER="$ROOT/python-display/autostart-launch.sh"

usage() {
  echo "Usage: bash python-display/autostart.sh {enable|disable|status}" >&2
  exit 2
}

case "${1:-}" in
  enable)
    if [[ -e "$ENTRY" ]]; then
      echo "NodeWatch desktop autostart already configured: $ENTRY"
      echo "Existing entry left unchanged."
      exit 0
    fi
    mkdir -p "$ENTRY_DIR"
    if [[ -e "$BACKUP" ]]; then
      mv -- "$BACKUP" "$ENTRY"
      echo "Restored saved NodeWatch desktop autostart entry: $ENTRY"
      exit 0
    fi
    # Paths in the Desktop Entry Exec key must be quoted if they contain spaces.
    if [[ "$LAUNCHER" == *'"'* || "$LAUNCHER" == *'\'* || "$LAUNCHER" == *$'\n'* ]]; then
      echo "Unsupported installation path for desktop autostart: $LAUNCHER" >&2
      exit 1
    fi
    cat > "$ENTRY" <<EOF
[Desktop Entry]
Type=Application
Name=NodeWatch
Comment=Native Tkinter Raspberry Pi monitoring dashboard
Exec=/bin/bash "$LAUNCHER"
Terminal=false
StartupNotify=false
EOF
    echo "Enabled NodeWatch for future graphical desktop logins: $ENTRY"
    echo "It will not launch immediately; log out and back in, or reboot with desktop auto-login."
    ;;
  disable)
    if [[ ! -e "$ENTRY" ]]; then
      echo "NodeWatch desktop autostart is not enabled."
      exit 0
    fi
    mkdir -p "$BACKUP_DIR"
    if [[ -e "$BACKUP" ]]; then
      echo "Refusing to overwrite an existing saved entry: $BACKUP" >&2
      exit 1
    fi
    mv -- "$ENTRY" "$BACKUP"
    echo "Disabled NodeWatch for future desktop logins."
    echo "Saved previous entry to: $BACKUP"
    echo "An already-running NodeWatch window is not stopped."
    ;;
  status)
    if [[ -e "$ENTRY" ]]; then
      echo "Desktop autostart entry exists: $ENTRY"
    elif [[ -e "$BACKUP" ]]; then
      echo "Desktop autostart entry is disabled (saved at $BACKUP)"
    else
      echo "Desktop autostart is not configured."
    fi
    ;;
  *)
    usage
    ;;
esac
