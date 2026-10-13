# NodeWatch — Raspberry Pi and Ubuntu Server monitoring

**NodeWatch is a lightweight, two-page system stats dashboard for Raspberry Pi.** Run it in **Pi Mode** to monitor the Raspberry Pi itself, or use **Server Mode** to monitor an Ubuntu Server while still displaying the Pi's health.

Choose either a native Python/Tkinter display (**no Chromium needed**) or a browser-based HTML/CSS/JavaScript display. Both interfaces use the same Python telemetry collector and configuration.

## Choose your monitoring method

| Method | Main system being monitored | Additional machine needed? | Full setup |
| --- | --- | --- | --- |
| **1. Pi Mode** | This Raspberry Pi: CPU, RAM, disk, temperature, uptime and network | **No** | [Pi Mode instructions](docs/PI_MODE.md) |
| **2. Server Mode** | Remote Ubuntu Server: CPU, RAM, disk, temperature and uptime; also shows the local Pi's stats | **Yes — an Ubuntu/Linux server running the agent** | [Server Mode instructions](docs/SERVER_MODE.md) |

**Mode is selected through the Pi's `.env` file**, using `REMOTE_AGENT_URL`. There is no remote agent requirement in Pi Mode, and you don't need to run both methods.

### Method 1 — Pi Mode: just the Raspberry Pi

Install NodeWatch on the Pi (or use your existing checkout):

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv python3-tk
# Clone only if not already installed; a private repo needs authorized SSH access:
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

Edit the Pi's `.env`:

```ini
SERVER_NAME="Raspberry Pi"
REMOTE_AGENT_URL=
REMOTE_AGENT_TOKEN=
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

**Leave `REMOTE_AGENT_URL` empty.** This selects Pi Mode, reads real Pi telemetry via `psutil` and shows **PI ONLY** / **LOCAL PI MODE** in the interface. No Ubuntu Server or token needed.

Start the native Python display on the Pi's graphical desktop:

```bash
bash python-display/start-native.sh
```

Or start the browser version instead:

```bash
bash browser/start-web.sh
```

The browser version is available at `http://127.0.0.1:8765/` on the Pi. See [Pi Mode — complete guide](docs/PI_MODE.md) for verification and display options.

### Method 2 — Server Mode: Ubuntu Server + Raspberry Pi

Install the read-only metrics agent on your **Ubuntu Server** and configure a strong `AGENT_TOKEN` plus an agent listener reachable **only from your trusted Pi/LAN/VPN**. Detailed installation, token generation, firewall guidance and agent startup are in [Server Mode — complete guide](docs/SERVER_MODE.md).

Then edit `.env` **on the Raspberry Pi**:

```ini
SERVER_NAME="Ubuntu Home Server"
REMOTE_AGENT_URL=http://YOUR_UBUNTU_SERVER_LAN_IP:8766
REMOTE_AGENT_TOKEN=PASTE_THE_SAME_AGENT_TOKEN_HERE
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

**A non-empty `REMOTE_AGENT_URL` selects Server Mode.** Start either display using the same native/browser commands as Pi Mode. Page 1 now shows the Ubuntu Server's metrics; page 2 continues to show the Raspberry Pi's own health, network totals and optional port checks.

The Ubuntu Server does **not** need a graphical desktop. If the remote agent is unreachable, the dashboard shows **OFFLINE**, not fabricated server readings.

To return to Pi Mode, clear `REMOTE_AGENT_URL` on the Pi and restart NodeWatch.

## Choose your display version

Monitoring **mode** (Pi or Server) and display **version** (native or browser) are independent choices.

| Display | Best for | Launch on Pi |
| --- | --- | --- |
| [Native Python](python-display/README.md) | Raspberry Pi 3B, 3.5-inch SPI display, no Chromium | `bash python-display/start-native.sh` |
| [Browser](browser/README.md) | Browser-capable Pi, monitor or another supported screen | `bash browser/start-web.sh` |

The native version uses Tkinter with a 480×320-style layout and needs a working graphical desktop/display driver; it is not a direct framebuffer or console app. More detail: [Display version comparison](DISPLAY_VERSIONS.md).

## What the two pages show

| Page | Pi Mode | Server Mode |
| --- | --- | --- |
| **1 — System Overview** | Raspberry Pi CPU, RAM, root disk, temperature, hostname, uptime | Ubuntu Server CPU, RAM, root disk, temperature, hostname, uptime |
| **2 — Network & Services** | Pi IP/hostname/CPU/RAM/uptime, cumulative network totals, optional TCP checks | Ubuntu agent connection and optional TCP checks **plus the same local Pi health/network information** |

Data refreshes every **5 seconds** and pages auto-rotate every **12 seconds** by default. Adjust `REFRESH_SECONDS` and `ROTATE_SECONDS` in `.env`. On the native touchscreen, tap left or right to change pages; keyboard left/right arrows also work.

Telemetry comes from `psutil` on the monitored host. The local Pi network counters are **cumulative since boot**, not live transfer speeds. A missing temperature sensor displays `--` / a dash; TCP port checks only test reachability.

## Verify the active monitoring mode

From the Pi's project directory:

```bash
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("Remote connected:", s["server"]["connected"]); print("Pi CPU:", s["pi"]["cpu_percent"])'
```

- Pi Mode: `Mode: pi`; remote connection is not required.
- Server Mode: `Mode: remote`; `Remote connected: True` means the agent responded.

## Project files

- `dashboard.py` — web API server and shared `collect_state()` for both interfaces.
- `metrics.py` — local CPU, memory, disk, temperature, uptime and network telemetry.
- `agent.py` — optional authenticated read-only agent for a separate Ubuntu Server.
- `python-display/` — native Python/Tkinter two-page interface.
- `browser/`, `static/` — browser launcher and HTML/CSS/JavaScript interface.
- `.env.example` — configuration template; copy it to `.env`.
- `deploy/` — optional example systemd service files.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The project also runs tests using GitHub Actions.

## Security and privacy

Do not commit your actual `.env`, agent tokens, passwords or internal credentials. The GitHub repository may be private; cloning requires authorized access. The web dashboard binds to `127.0.0.1` by default. Restrict the optional Server Mode agent to your trusted LAN/VPN and use firewall rules allowing only the Pi; do not expose the unencrypted agent HTTP endpoint to the public internet. For networks you don't fully trust, use HTTPS or an encrypted VPN/tunnel.

License: MIT (see `LICENSE`).
