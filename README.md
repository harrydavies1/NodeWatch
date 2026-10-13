# NodeWatch — Raspberry Pi / Ubuntu Server dashboard

**A lightweight, two-page server monitoring dashboard for Ubuntu Server, tested on a Raspberry Pi 3B with a 3.5-inch SPI display. Shows live system stats, network activity, temperatures, and service status in a compact interface. Could possibly work on other distros (debian, arch, raspian, etc.).**

NodeWatch is a web-based, dark-mode 800×480-style dashboard built with Python, HTML, CSS and vanilla JavaScript. It uses `psutil` on Linux (including Raspberry Pi OS and Ubuntu Server). There is no cloud account or paid service requirement.

> **Project status:** functional starter implementation. Its two-page layout is a default design, **not a claim to reproduce any previously discussed/custom screen exactly**. Share your prior files or screenshots to match an existing design. Hardware-specific GPIO/SPI displays may require their own drivers.

## Two pages

| Screen | Displays |
| --- | --- |
| **1 — System Overview** | Ubuntu Server (or Pi-only) CPU usage, memory, root-disk space, available temperature sensor, hostname, IP, CPU cores, and uptime |
| **2 — Network & Services** | Ubuntu Server agent connection, configurable TCP port checks, Raspberry Pi hostname, IP, CPU, RAM, temperature and uptime, cumulative Pi network traffic |

Pages change automatically every **12 seconds** and data refreshes every **5 seconds** (both configurable). You can switch pages with the visible arrows/dots or your keyboard's left/right arrows.

## How it works

```text
 Ubuntu Server (runs agent.py)                 Raspberry Pi (runs dashboard.py)
  - CPU, RAM, disk, uptime                       - Kiosk web interface
  - Optional CPU temperature       private       - Pi health/network info
  - GET /api/metrics  ----------------------->    - Pulls Ubuntu stats every 5 sec
                       authenticated read-only    - Monitors selected TCP services
                                      HDMI / touchscreen / desktop browser
```

The **Ubuntu Server machine does not require a desktop environment**. Only the device used to display the web page needs a graphical browser. If your Pi is also running Ubuntu Server headlessly, it can run the Python dashboard service but needs a GUI/browser on the Pi for an attached display (or open the page remotely by changing `DASHBOARD_HOST` and using an appropriate firewall). HDMI screens with Raspberry Pi OS Desktop are the simplest kiosk setup.

## Prerequisites

- Ubuntu Server 22.04 LTS, 24.04 LTS or other recent supported Linux distributions for the **monitored server** (a normal Python 3 environment; tested code here, not tested on every hardware/OS combination).
- Raspberry Pi running Raspberry Pi OS with a desktop for a locally attached HDMI monitor, or Ubuntu with a graphical desktop.
- Python 3 with `venv` and `pip` on both computers.
- Network connectivity between the two machines; **never expose the agent directly to the public internet**.

## Step 1 — Install the read-only agent on Ubuntu Server

On **Ubuntu Server**:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
# After publishing your repository, use its URL:
git clone https://github.com/YOUR_USERNAME/pi-server-dashboard.git
cd pi-server-dashboard
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
python3 -c 'import secrets; print(secrets.token_urlsafe(36))'
```

Edit **the Ubuntu machine's** `.env` (`nano .env`) and set:

```ini
AGENT_TOKEN=PASTE_A_LONG_RANDOM_TOKEN_HERE
AGENT_HOST=0.0.0.0
AGENT_PORT=8766
```

Then start with `./start-agent.sh`. Test locally:

```bash
curl -H 'Authorization: Bearer PASTE_A_LONG_RANDOM_TOKEN_HERE' http://127.0.0.1:8766/api/metrics
```

Expect JSON metrics. The agent returns `401` unless the token matches. To make it survive a reboot, copy `deploy/server-agent.service.example` to `/etc/systemd/system/server-agent.service`, change `YOUR_USERNAME` and paths, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now server-agent
sudo systemctl status server-agent
```

**Firewall:** restrict TCP `8766` to the Pi IP or to an authenticated VPN interface. For example, with UFW and a known Pi address:

```bash
sudo ufw allow from PI_LAN_IP to any port 8766 proto tcp
```

Do not blindly enable a firewall over SSH without allowing SSH first. For traffic outside your trusted LAN, use WireGuard/Tailscale and preferably TLS; the bearer token is not encrypted by HTTP alone.

## Step 2 — Install the dashboard on the Raspberry Pi

On the **Raspberry Pi**:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
# After publishing your repository, use its URL:
git clone https://github.com/YOUR_USERNAME/pi-server-dashboard.git
cd pi-server-dashboard
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
nano .env
```

Set **the Pi's** `.env` to point at Ubuntu Server:

```ini
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8765
SERVER_NAME="Ubuntu Home Server"
REMOTE_AGENT_URL=http://YOUR_UBUNTU_SERVER_LAN_IP:8766
REMOTE_AGENT_TOKEN=PASTE_THE_SAME_LONG_RANDOM_TOKEN_HERE
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[{"name":"SSH","host":"YOUR_UBUNTU_SERVER_LAN_IP","port":22}]'
```

Replace all placeholders with real local or VPN IP addresses and **the same agent token**. Set `SERVICES_JSON='[]'` if you don't want TCP checks. Note: service checks show whether a TCP port accepts connections, not whether the service is fully healthy.

Run:

```bash
./start.sh
```

Open `http://127.0.0.1:8765/` on the Pi. You should now see the live two-page screen. For a Pi with a desktop, install Chromium if needed and run:

```bash
./kiosk-start.sh
```

On some distributions the Chromium command/package is `chromium-browser` instead of `chromium`; adjust the script if needed. To keep the dashboard service running after reboot, use `deploy/pi-dashboard.service.example` as above; launch the browser in the **logged-in graphical desktop session** (not in the headless `systemd` service).

## Pi-only quick test (no remote Ubuntu Server required)

If `REMOTE_AGENT_URL` is empty, the dashboard deliberately shows **real Raspberry Pi telemetry** and labels it **Local Pi Mode** instead of pretending it came from the server. Set a remote URL later to switch to Ubuntu Server metrics.

## Customize

- **Layout:** `static/index.html`
- **Styling/responsiveness:** `static/style.css`
- **Auto-rotation/page logic:** `static/app.js`
- **Collection and networking:** `dashboard.py`, `agent.py`, `metrics.py`
- **Settings and optional service checks:** `.env` (never commit this file)

The app doesn't need root permissions for basic telemetry; CPU temperature availability depends on exposed sensors, and inaccessible sensors display a dash, not fake readings. Pi network totals are **cumulative since boot** rather than live per-second throughput. Service checks are TCP reachability probes, not Docker/container state inspection.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

GitHub Actions runs the same checks on pushes and pull requests.

## Repository privacy and security

Create the GitHub repository as **private** initially. The `.gitignore` excludes `.env`, virtual environments and caches. `.env.example` only contains placeholders. Do not commit real API keys, passwords, VPN keys, bearer tokens or internal addresses you want kept secret. Prefer secure transport (VPN / HTTPS); restrict both the agent listener and firewall to trusted devices. The dashboard binds to Pi localhost by default.

## Troubleshooting

- **SERVER OFFLINE:** verify `REMOTE_AGENT_URL`/`REMOTE_AGENT_TOKEN`, `systemctl status server-agent`, and firewall/network connectivity.
- **No temperature:** your server/VM may not expose supported sensors.
- **No services listed:** edit `SERVICES_JSON` in the Pi `.env` and restart the dashboard.
- **Black screen / browser missing:** check the graphical desktop, HDMI display output, and Chromium installation; Ubuntu Server by itself is normally headless.
- **Port already in use:** change `AGENT_PORT` or `DASHBOARD_PORT` in the relevant machine's `.env`.

License: MIT (see `LICENSE`).
