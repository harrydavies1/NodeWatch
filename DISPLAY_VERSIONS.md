# Choose your NodeWatch display and monitoring mode

NodeWatch provides **two monitoring modes** and **two display implementations**. You can combine either monitoring mode with either display.

## Step 1 — Choose what to monitor

| Monitoring mode | What appears on the dashboard | How it is selected |
| --- | --- | --- |
| **[Pi Mode](docs/PI_MODE.md)** | Stats from the Raspberry Pi running NodeWatch; no Ubuntu Server needed | Leave `REMOTE_AGENT_URL=` empty in the Pi's `.env` |
| **[Server Mode](docs/SERVER_MODE.md)** | Remote Ubuntu Server stats **plus** local Raspberry Pi health | Set `REMOTE_AGENT_URL=http://SERVER_LAN_IP:8766` and matching `REMOTE_AGENT_TOKEN`; run `agent.py` on the server |

The selection applies to both pages and both display implementations. Switching modes only requires an update to the Pi's `.env` followed by restarting the display.

## Step 2 — Choose how to display it

| Version | Interface | Launch on Pi |
| --- | --- | --- |
| [Browser](browser/README.md) | HTML, CSS and JavaScript in Chromium or another browser | `bash browser/start-web.sh` |
| [Native Python](python-display/README.md) | Tkinter canvas with no Chromium | `bash python-display/start-native.sh` |

Both have two automatically rotating pages. The native Python version is designed for small displays, including a common 480×320 SPI panel on a Raspberry Pi 3B.

## Quick native installation

On the Pi:

```bash
sudo apt update
sudo apt install -y python3-tk python3-venv python3-pip
cd ~/pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

Configure either [Pi Mode](docs/PI_MODE.md) or [Server Mode](docs/SERVER_MODE.md) and then launch:

```bash
bash python-display/start-native.sh
```

**Chromium isn't needed for the native version**, but Tkinter requires an available graphical desktop and appropriate SPI/monitor display driver. Your real `.env` must never be committed.
