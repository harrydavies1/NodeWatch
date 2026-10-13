# NodeWatch — Native Tkinter dashboard

NodeWatch uses **one display implementation: native Python/Tkinter**. It is designed for Raspberry Pi, including a Pi 3B with a small SPI display (commonly 480×320). It **does not require Chromium**.

## Choose a monitoring mode

| Mode | Main metrics | Second page | Setup |
| --- | --- | --- | --- |
| **Pi Mode** | Raspberry Pi CPU, RAM, disk, temperature and uptime | Pi networking and optional TCP checks | [Pi Mode guide](../docs/PI_MODE.md) |
| **Server Mode** | Remote Ubuntu/Linux Server CPU, RAM, disk, temperature and uptime | Agent connection plus local Raspberry Pi health | [Server Mode guide](../docs/SERVER_MODE.md) |

Mode is configured on the Pi using `REMOTE_AGENT_URL` in `.env`:
- `REMOTE_AGENT_URL=` (empty): **Pi Mode**, no Ubuntu Server required.
- `REMOTE_AGENT_URL=http://SERVER_IP:8766` with a matching `REMOTE_AGENT_TOKEN`: **Server Mode**, requires `agent.py` on the server.

Edit the Pi's `.env` and restart the application to change modes.

## Installation

```bash
sudo apt update
sudo apt install -y git python3 python3-tk python3-venv python3-pip
# For private repositories, configure authorized GitHub SSH credentials first:
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

If NodeWatch is already installed, keep the existing checkout, `.venv` and `.env`.

## Launch

From the Pi's working graphical desktop:

```bash
cd ~/pi-server-dashboard
bash python-display/start-native.sh
```

For a windowed 480×320 preview:

```bash
bash python-display/start-native.sh --windowed
```

Tkinter requires a functioning X11 or other Tk-compatible graphical session and display driver; it cannot open on a bare text-only console.

## Optional autostart at desktop login

If you want NodeWatch to open when the Pi graphical desktop logs in, run `bash python-display/autostart.sh enable` from the repository. To inspect or disable it, run `bash python-display/autostart.sh status` or `bash python-display/autostart.sh disable`. This is **off by default**, doesn't replace an existing startup entry, and doesn't change the Pi's graphical configuration. See [the optional autostart guide](../docs/AUTOSTART.md).

## Controls and settings

- Stats refresh every 5 seconds; pages alternate every 12 seconds by default.
- Tap left/right side of screen or press Left/Right arrow keys to navigate.
- Press Escape to leave fullscreen.
- Adjust `REFRESH_SECONDS` and `ROTATE_SECONDS` in the Pi's `.env` and restart.
- Optional `SERVICES_JSON` checks whether TCP ports are reachable.

## Troubleshooting

- **No Tkinter window:** verify `python3-tk` is installed and launch from a working graphical desktop. Try `--windowed`.
- **Page 1 still shows Pi stats:** `REMOTE_AGENT_URL` is empty; configure Server Mode using the guide.
- **Remote server OFFLINE:** check the agent, server IP/port and matching tokens; the Pi's local stats still work.
- **Missing temperature:** the platform may not expose sensors; unavailable readings appear as a dash.

See also the main [Troubleshooting section](../README.md#troubleshooting).
