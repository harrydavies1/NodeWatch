# NodeWatch — Raspberry Pi monitoring dashboard

**Latest stable release: [v1.1.0](https://github.com/harrydavies1/NodeWatch/releases/tag/v1.1.0)** · [Changelog](CHANGELOG.md) · [What's new since v1.0.0](releases/v1.1.0.md)

**NodeWatch is a native Python/Tkinter dashboard for a Raspberry Pi**, designed for a small display such as a 480×320 SPI screen. It shows two live telemetry pages, an optional third NAS storage page, and an optional **fourth HDD temperature page**. It **does not need a web browser**. Automatic page rotation is optional.

## Hardware used

- **Raspberry Pi display:** Raspberry Pi 3 Model B (Pi 3B) with a **3.5-inch OSOYOO SPI RPi Display V1.0**.
- **Server hardware:** A basic **Dell OptiPlex** desktop running **Ubuntu Server**.

**Testing status:** Pi Mode, the native 3.5-inch Tkinter display and end-to-end Server Mode with Ubuntu Server on a Dell OptiPlex have been tested on real hardware. The Ubuntu agent and NAS drive paths have also been tested on the OptiPlex. The HDD-temperature fourth page was confirmed working on the Raspberry Pi after deployment troubleshooting. NAS storage and HDD temperature functionality have automated tests; compatibility with every SPI display, drive and operating-system configuration is not guaranteed.

There are **two monitoring modes**. The same Tkinter dashboard works in either one; both have now been tested with the Pi and OptiPlex. Dual-NAS monitoring is opt-in and covered by automated tests.

| Mode | What NodeWatch monitors | Requires another machine? |
| --- | --- | --- |
| **[Pi Mode](docs/PI_MODE.md)** | This Raspberry Pi's CPU, RAM, disk, temperature, uptime and network | No |
| **[Server Mode](docs/SERVER_MODE.md)** | A separate Ubuntu/Linux server, **plus** the Pi's local health | Yes, a server running `agent.py` |

## Install on the Raspberry Pi

Run these commands on the Pi (skip the clone if you already have the project installed):

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv python3-tk

# Public repository: HTTPS clone does not require a GitHub SSH key.
git clone https://github.com/harrydavies1/NodeWatch.git pi-server-dashboard
cd pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

**Already running NodeWatch?** Keep your existing `~/pi-server-dashboard` directory, `.venv` and `.env` — don't clone again or overwrite your configuration. The GitHub repository was renamed to `NodeWatch`, but your Pi's local folder can keep its old name. To point an existing checkout at the new address, run `git remote set-url origin https://github.com/harrydavies1/NodeWatch.git` from inside that checkout, then `git pull` whenever you choose to update. This is **not required** for the dashboard to keep running.

## Method 1 — Pi Mode (no Ubuntu Server)

Set these lines in the Pi's `.env`:

```ini
SERVER_NAME="Raspberry Pi"
REMOTE_AGENT_URL=
REMOTE_AGENT_TOKEN=
REFRESH_SECONDS=5
AUTO_ROTATE_PAGES=true
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
AUTO_ROTATE_PAGES=true
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

Replace `YOUR_SERVER_LAN_IP` with the server's actual LAN/VPN address and `YOUR_MATCHING_AGENT_TOKEN` with the **same `AGENT_TOKEN` configured on the Ubuntu Server**.

Save the file and **restart NodeWatch** (if your Pi launches it automatically at desktop login, a reboot is a simple way to restart it). NodeWatch now uses Server Mode:

- **Page 1:** Ubuntu Server CPU, RAM, disk, temperature and uptime.
- **Page 2:** Remote connection status, optional TCP checks and **the Raspberry Pi's own** CPU, RAM, IP, uptime and cumulative network traffic.

To return to Pi Mode, clear `REMOTE_AGENT_URL` and `REMOTE_AGENT_TOKEN` in the Pi's `.env`, then restart NodeWatch. **Edit the existing settings rather than adding duplicate lines.** No code changes are required.

## Optional: monitor both Samba NAS drives

Server Mode can display independent storage usage for **two NAS disks** without replacing the Ubuntu root **DISK** tile. It adds a dedicated **third page** to the 480×320 Tkinter display, with a separate usage bar, used/free capacity and mount warnings for each drive. The feature is disabled until you configure `NAS_STORAGE_PATHS`.

On **Ubuntu Server**, edit `~/pi-server-dashboard/.env` and add:

```ini
NAS_STORAGE_PATHS='[{"name":"NAS Drive 1","path":"/srv/nas/drive1"},{"name":"NAS Drive 2","path":"/srv/nas/drive2"}]'
```

These are the confirmed Samba mount paths for the Dell OptiPlex build. Keep the existing agent token/settings; remove or comment out any old `NAS_STORAGE_PATH` single-drive line for clarity.

Pull the latest code and restart the agent on **Ubuntu Server**, then pull on the **Pi**, verify `nas_volumes` is arriving and restart its Tkinter dashboard. The monitoring code will show **MOUNT MISSING / SYSTEM DISK** or **UNAVAILABLE** instead of reporting a missing NAS disk as healthy. Existing Pi Mode and older single-drive monitoring remain supported.

[Step-by-step two-drive setup and troubleshooting →](docs/NAS_STORAGE.md)

## Optional: HDD temperatures on page 4

In Server Mode, NodeWatch can also show the SMART temperatures of up to two HDDs on a **dedicated fourth page** (when the NAS storage page is enabled; otherwise it is page 3). The readings come from the **Ubuntu Server** via `smartctl`, are cached for 60 seconds and show a warning if a disk is sleeping, missing or unreadable. The feature is opt-in and never changes disks or fan settings.

Add `HDD_TEMP_DRIVES` to **Ubuntu Server's** `.env` (not the Pi's):

```ini
HDD_TEMP_DRIVES='[{"name":"NAS Drive 1","device":"/dev/sdb"},{"name":"NAS Drive 2","device":"/dev/sdc"}]'
```

Device names can change after a reboot or replacement. Stable `/dev/disk/by-id/` names are preferred. **A restricted read-only sudoers rule is required** for the agent to read SMART data; don't run the agent as root or grant broad disk permissions. See the guide before enabling this setting.

[Set up the HDD temperature page safely →](docs/HDD_TEMPERATURES.md)

**Only three pages after updating the Pi?** The fourth page appears only after **Ubuntu Server's** agent sends the `hdd_temperatures` list. Pull the updated code on **both machines**, set `HDD_TEMP_DRIVES` in **Ubuntu Server's** `.env`, restart `server-agent`, and restart the Pi dashboard. Use the [step-by-step live-data troubleshooting guide](docs/HDD_TEMPERATURES.md#troubleshooting-case-updated-the-pi-but-still-only-see-three-pages) to distinguish an old agent (`None`), missing configuration (`[]`) and data arriving correctly (a list).

## Optional: start the Ubuntu Server metrics agent on boot

For **Server Mode**, the Ubuntu Server can start its read-only agent automatically whenever Ubuntu boots — no login or desktop is needed. After completing [Server Mode setup](docs/SERVER_MODE.md), stop any manually running agent, then on the **Ubuntu Server** run:

```bash
cd ~/pi-server-dashboard
bash deploy/server-agent-autostart.sh enable
```

Check or disable the agent using:

```bash
bash deploy/server-agent-autostart.sh status
bash deploy/server-agent-autostart.sh disable
```

The optional systemd service starts the agent immediately, keeps it available after reboots and restarts it after unexpected failures. This is **off by default** and separate from the Pi's optional graphical autostart. The server **listens**, while the Pi requests fresh stats periodically.

[Complete optional Ubuntu Server autostart guide →](docs/SERVER_AUTOSTART.md)

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

## Optional: launch NodeWatch when the Raspberry Pi desktop starts

**Autostart is opt-in and disabled by default.** NodeWatch also works perfectly well when launched manually. This method is for Raspberry Pi OS graphical desktop sessions that support XDG autostart (including LXDE); it starts **after you log in to the desktop**, not as a headless system service.

On the Pi, from the NodeWatch project folder:

```bash
cd ~/pi-server-dashboard
bash python-display/autostart.sh enable
```

The command creates a `~/.config/autostart/nodewatch.desktop` entry, unless one already exists; **it does not overwrite an existing NodeWatch startup entry**. The launcher waits a few seconds for the desktop to settle before opening Tkinter fullscreen. No `sudo` is needed.

To inspect or disable it later:

```bash
bash python-display/autostart.sh status
bash python-display/autostart.sh disable
```

Disabling preserves the previous entry outside the desktop's autostart folder, so you can run `enable` again to restore it. It affects **future desktop logins only**; it will not close the currently running dashboard.

For NodeWatch to appear **without any manual login after power-on**, configure desktop auto-login separately on your Pi. Otherwise, NodeWatch starts when you log into the desktop. **A graphical desktop and its display driver must already be working.** This is not a fix for missing graphical sessions.

To troubleshoot an enabled startup entry, check `bash python-display/autostart.sh status` and the log at `~/nodewatch-autostart.log`. If you already have a working autostart configuration, you can leave it unchanged.

[Full optional autostart guide →](docs/AUTOSTART.md)

## What the dashboard shows

| Screen | Pi Mode | Server Mode |
| --- | --- | --- |
| **1 — System Overview** | Local Pi CPU, RAM, root disk, temperature, hostname, uptime | Ubuntu Server CPU, RAM, root disk, temperature, hostname, uptime; optional legacy single-NAS strip |
| **2 — Network & Services** | Pi IP, CPU/RAM, uptime, cumulative traffic and optional TCP checks | Server connection and optional port checks **alongside** Pi IP, CPU/RAM, uptime and traffic |
| **3 — NAS Storage (optional)** | Not shown | Two independently monitored Ubuntu NAS volumes, with usage and mount warnings when configured |
| **4 — HDD Temperatures (optional)** | Not shown | SMART temperatures for up to two server HDDs, with standby/unavailable warnings; shown as **page 3** if NAS Storage is not configured |

Stats update every **5 seconds** by default. Automatic switching is configurable on the **Pi only**: `AUTO_ROTATE_PAGES=true` (default; continue switching every `ROTATE_SECONDS`, normally 12) or `AUTO_ROTATE_PAGES=false` (stay on the selected page until you navigate manually). Edit the existing key in the Pi's `.env`, then restart the Tkinter dashboard; do not change Ubuntu Server's agent. Pi Mode remains two pages; the NAS page appears in Server Mode only when multi-drive data is available. Temperature appears only when an OS sensor is available; the display does not guarantee a CPU-specific sensor. The native page shows **up to three** configured TCP port checks, and those checks do not indicate whether a service or Docker container is healthy. Network upload/download values are **cumulative since boot**, not bandwidth speeds. Tap either side of the touchscreen, or use Left/Right arrows to change pages. Press Escape to exit fullscreen.

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
| No temperature reading | The operating system may not expose a supported CPU sensor; NodeWatch displays a dash rather than inventing a reading. HDD SMART temperatures have separate setup steps. |
| Updated Pi but still only three pages | **Ubuntu Server** must run the updated agent and have `HDD_TEMP_DRIVES` set in its own `.env`. Restart `server-agent`; on the Pi, inspect `hdd_temperatures` with the [diagnostic command](docs/HDD_TEMPERATURES.md#troubleshooting-case-updated-the-pi-but-still-only-see-three-pages), update the Pi code, and restart Tkinter. |
| No service checks | Add entries to `SERVICES_JSON` or leave it as `'[]'` to disable checks. Only the first three checks are shown on the native page; checks are TCP reachability probes, not full service or Docker health. |
| Changes to `.env` don't show | Restart the Tkinter dashboard; configuration is read when the application starts. Don't append duplicate `REMOTE_AGENT_URL` or token lines — edit the existing entries. |
| Fresh clone fails | Use `https://github.com/harrydavies1/NodeWatch.git` (the public repo's current name). A plain HTTPS clone does not require an SSH key. |

For detailed setup help, see [Pi Mode](docs/PI_MODE.md), [Server Mode](docs/SERVER_MODE.md), and the [Tkinter display guide](python-display/README.md).

## Project structure

- `python-display/native_dashboard.py` — native Tkinter dashboard with two base pages, optional NAS storage and HDD temperature pages
- `python-display/start-native.sh` — native display launcher
- `python-display/autostart.sh` — optional desktop startup enable/disable helper
- `dashboard.py` — **telemetry collection only** for Pi Mode and Server Mode (no browser server)
- `metrics.py` — psutil CPU/RAM/disk/temperature/uptime/network snapshot, optional NAS usage and HDD temperature readings
- `hdd_temperatures.py` — read-only SMART HDD temperature collector with 60-second caching and clear failure states
- `agent.py` and `start-agent.sh` — optional Ubuntu Server telemetry agent
- `.env.example` — configuration template; keep your real `.env` local
- `deploy/server-agent-autostart.sh` — optional agent startup enable/disable/status on Ubuntu Server
- `deploy/server_agent_service.py` — validates and renders the Ubuntu systemd unit
- `deploy/server-agent.service.example` — optional manual service template
- `tests/` — Python tests

## Run tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

License: MIT (see `LICENSE`).
