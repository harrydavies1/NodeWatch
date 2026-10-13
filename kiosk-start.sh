#!/usr/bin/env bash
# Run in a logged-in Raspberry Pi OS desktop session (labwc / Wayland).
set -euo pipefail
exec chromium --kiosk --noerrdialogs --disable-infobars --no-first-run \
  --start-maximized "http://127.0.0.1:8765/"
