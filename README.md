# NodeWatch — Raspberry Pi monitoring dashboard

**NodeWatch is a native Python/Tkinter dashboard for a Raspberry Pi**, designed for a small display such as a 480×320 SPI screen. It shows two automatically rotating pages of live stats and **does not need a web browser**.

There are **two monitoring modes**. The same Tkinter dashboard works in either one.

| Mode | What NodeWatch monitors | Requires another machine? |
| --- | --- | --- |
| **[Pi Mode](docs/PI_MODE.md)** | This Raspberry Pi's CPU, RAM, disk, temperature, uptime and network | No |
| **[Server Mode](docs/SERVER_MODE.md)** | A separate Ubuntu/Linux server, **plus** the Pi's local health | Yes, a server running `agent.py` |

## Install on the Raspberry Pi

Run these commands on the Pi (skip the clone if you already have the project installed):

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv python3-tk

# For a private repository, configure authorized GitHub SSH access first.
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

**Already running NodeWatch?** Keep your existing `~/pi-server-dashboard` directory, `.venv` and `.env`. You can update the code with `git pull` when you want to, without repeating installation.

## Method 1 — Pi Mode (no Ubuntu Server)

Set these lines in the Pi's `.env`:

```ini
SERVER_NAME="Raspberry Pi"
REMOTE_AGENT_URL=
REMOTE_AGENT_TOKEN=
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

An **empty `REMOTE_AGENT_URL`** selects Pi Mode. NodeWatch reads real Raspberry Pi telemetry directly using `psutil`. No second computer or server agent is needed.

[Complete Pi Mode guide →](docs/PI_MODE.md)

## Method 2 — Server Mode (Ubuntu Server + Pi)

First, install and start the read-only `agent.py` on the Ubuntu/Linux server. [Complete Server Mode guide →](docs/SERVER_MODE.md)

**When your server is ready, you only need to change the Pi's `.env`:**

```ini
SERVER_NAME="Ubuntu Home Server"
REMOTE_AGENT_URL=http://YOUR_SERVER_LAN_IP:8766
REMOTE_AGENT_TOKEN=YOUR_MATCHING_AGENT_TOKEN
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

Replace `YOUR_SERVER_LAN_IP` with the server's actual LAN/VPN address and `YOUR_MATCHING_AGENT_TOKEN` with the **same `AGENT_TOKEN` configured on the Ubuntu Server**.

Save the file and **restart NodeWatch** (if your Pi launches it automatically at desktop login, a reboot is a simple way to restart it). NodeWatch now uses Server Mode:

- **Page 1:** Ubuntu Server CPU, RAM, disk, temperature and uptime.
- **Page 2:** Remote connection status, optional TCP checks and **the Raspberry Pi's own** CPU, RAM, IP, uptime and cumulative network traffic.

To return to Pi Mode, clear `REMOTE_AGENT_URL` and `REMOTE_AGENT_TOKEN` in the Pi's `.env`, then restart NodeWatch. No code changes are required.

## Launch NodeWatch

From the Raspberry Pi's working graphical desktop:

```bash
cd ~/pi-server-dashboard
bash python-display/start-native.sh
```

To preview in a 480×320 window rather than fullscreen:

```bash
bash python-display/start-native.sh --windowed
```

The native dashboard uses Tkinter and needs a graphical session and an appropriate screen driver. It **does not** require Chromium and does not render directly from a Linux text-only console.

## What the dashboard shows

| Screen | Pi Mode | Server Mode |
| --- | --- | --- |
| **1 — System Overview** | Local Pi CPU, RAM, disk, temperature, hostname, uptime | Remote server CPU, RAM, disk, temperature, hostname, uptime |
| **2 — Network & Services** | Pi IP, CPU/RAM, uptime, cumulative traffic and optional TCP checks | Server connection and optional port checks **alongside** Pi IP, CPU/RAM, uptime and traffic |

Pages switch every **12 seconds** and data updates every **5 seconds** by default. Tap either side of the touchscreen, or use Left/Right arrows to change pages. Press Escape to exit fullscreen.

## Check which monitoring mode is running

On the Pi:

```bash
cd ~/pi-server-dashboard
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("Remote connected:", s["server"]["connected"]); print("Pi IP:", s["pi"]["ip"])'
```

- **Pi Mode:** `Mode: pi` — the remote connection value is not needed.
- **Server Mode:** `Mode: remote` and `Remote connected: True` when the server agent responds.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Dashboard won't start | Check that `python3-tk` is installed, the Pi has an active graphical display, and `.venv/bin/python` exists. Try `bash python-display/start-native.sh --windowed` from the desktop. |
| Stats do not appear | Run the mode-check command above. Check `.venv/bin/pip install -r requirements.txt` and look for Python errors in the launching terminal or NodeWatch log. |
| Still seeing Pi stats instead of Ubuntu Server | Ensure `REMOTE_AGENT_URL` is **not empty**, and that you edited the **Pi's** `.env` (not only the server's). Restart NodeWatch. |
| Server shows OFFLINE | Check that `agent.py` is running on Ubuntu Server, the Pi can reach the server's IP and port 8766, and both machines use matching tokens. |
| Agent replies `401 Unauthorized` | The Pi's `REMOTE_AGENT_TOKEN` must match Ubuntu Server's `AGENT_TOKEN` exactly. |
| No CPU temperature | The operating system may not expose a supported sensor; NodeWatch displays a dash rather than inventing a reading. |
| No service checks | Add valid entries to `SERVICES_JSON` or leave it as `'[]'` to disable checks. Checks test TCP connectivity, not full service health. |
| Changes to `.env` don't show | Restart the Tkinter dashboard; configuration is read when the application starts. |

For detailed setup help, see [Pi Mode](docs/PI_MODE.md), [Server Mode](docs/SERVER_MODE.md), and the [Tkinter display guide](python-display/README.md).

## Project structure

- `python-display/native_dashboard.py` — two-page Tkinter dashboard
- `python-display/start-native.sh` — native display launcher
- `dashboard.py` — **telemetry collection only** for Pi Mode and Server Mode (no browser server)
- `metrics.py` — psutil CPU/RAM/disk/temperature/uptime/network snapshot
- `agent.py` and `start-agent.sh` — optional Ubuntu Server telemetry agent
- `.env.example` — configuration template; keep your real `.env` local
- `deploy/server-agent.service.example` — optional Ubuntu Server agent service
- `tests/` — Python tests

## Run tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

License: MIT (see `LICENSE`).
