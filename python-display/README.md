# NodeWatch — Native Python display (no Chromium)

A two-page Tkinter interface for Raspberry Pi, including a Pi 3B with a small 3.5-inch SPI display (typically 480×320). No browser is required.

This display supports **two distinct monitoring methods**. They share the same application and only differ in configuration:

| Mode | Page 1 displays | Page 2 includes | Full guide |
| --- | --- | --- | --- |
| **Pi Mode** | The Raspberry Pi's own CPU, RAM, disk, temperature and uptime | Local Pi networking and optional TCP service checks | [Set up Pi Mode](../docs/PI_MODE.md) |
| **Server Mode** | Remote Ubuntu Server stats from `agent.py` | Remote connection status **and** local Raspberry Pi health | [Set up Server Mode](../docs/SERVER_MODE.md) |

## Requirements

- Raspberry Pi OS with a **working graphical desktop session** (X11 or a Tk-compatible graphical session).
- For SPI screens, a driver that presents the graphical desktop on the attached display.
- Python 3, `python3-tk`, `python3-venv`, and dependencies from `requirements.txt`.

Tkinter does not run directly on a bare text console, but **does not require Chromium**.

## Install

```bash
sudo apt update
sudo apt install -y git python3 python3-tk python3-venv python3-pip

# If you don't already have a checkout, clone with authorized GitHub access:
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard

python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

Skip the clone if NodeWatch is already installed. Keep your existing `.env` when updating.

## Method 1 — Pi Mode (no remote server)

On the **Pi's** `.env`:

```ini
SERVER_NAME="Raspberry Pi"
REMOTE_AGENT_URL=
REMOTE_AGENT_TOKEN=
SERVICES_JSON='[]'
```

This displays **real local Pi statistics**. On the native screen, the status reads **PI ONLY**. No Ubuntu Server is required. See [Pi Mode setup](../docs/PI_MODE.md).

## Method 2 — Server Mode (Ubuntu Server + Pi)

First install and start the optional agent **on Ubuntu Server** using [Server Mode setup](../docs/SERVER_MODE.md). Then set these values **in the Pi's** `.env`:

```ini
SERVER_NAME="Ubuntu Home Server"
REMOTE_AGENT_URL=http://YOUR_UBUNTU_SERVER_LAN_IP:8766
REMOTE_AGENT_TOKEN=YOUR_MATCHING_AGENT_TOKEN
```

The primary metrics switch to the Ubuntu Server. The native second page continues showing the Raspberry Pi's local stats. A remote connection failure is shown as **OFFLINE**, not as local server data.

## Launch the native display

From the Pi's graphical desktop environment:

```bash
bash python-display/start-native.sh
```

For a 480×320 windowed preview:

```bash
bash python-display/start-native.sh --windowed
```

To switch between Pi Mode and Server Mode, change `REMOTE_AGENT_URL` in the Pi's `.env` and restart NodeWatch. No code changes are necessary.

## Controls

- Two pages auto-rotate every 12 seconds; data refreshes every 5 seconds by default.
- Tap the left/right half of the screen or press Left/Right arrow to switch pages.
- Escape exits fullscreen.
- Customize `ROTATE_SECONDS` and `REFRESH_SECONDS` in `.env`.
- CPU temperature is shown only if a supported sensor is available.

SPI panels vary by driver and resolution; a working desktop and display driver are prerequisites for this Tkinter renderer. For Pi 3B performance, avoid running Chromium alongside the native app if memory is tight. Keep remote agent traffic on a trusted LAN or VPN.
