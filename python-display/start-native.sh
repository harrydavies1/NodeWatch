#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv. Set up with: python3 -m venv --system-site-packages .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi
exec .venv/bin/python python-display/native_dashboard.py "$@"
