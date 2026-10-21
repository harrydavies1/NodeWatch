# NodeWatch — Native Tkinter dashboard

NodeWatch uses **one display implementation: native Python/Tkinter**. It is designed for Raspberry Pi, including a Pi 3B with a small SPI display (commonly 480×320). Two pages are shown by default; Server Mode can add a third NAS storage page and an optional fourth HDD-temperature page. It **does not require Chromium**.

## Tested Raspberry Pi display

The native fullscreen Tkinter interface has been tested on a **Raspberry Pi 3 Model B (Pi 3B)** with a **3.5-inch OSOYOO SPI RPi Display V1.0**. Pi Mode telemetry, two-page rotation and automatic launch at desktop login were confirmed on this hardware. Other SPI screens may have different display requirements.

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
# Public repository: HTTPS clone does not require a GitHub SSH key.
git clone https://github.com/harrydavies1/NodeWatch.git pi-server-dashboard
cd pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

If NodeWatch is already installed, keep the existing checkout, `.venv` and `.env`; do not clone again. The public GitHub repo is named `NodeWatch`, but the clone command above deliberately preserves the original local `pi-server-dashboard` folder name.

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

## Choose the visual theme (dark or XP)

The familiar **dark** style remains the default. The optional **Windows XP-inspired** style recreates Luna-era blue window chrome, a green Start button, a blue taskbar and system tray, raised panels and retro blue progress bars. The **Start** button opens a working page launcher; the other controls and navigation continue to work.

To enable it, edit `.env` on the **machine displaying NodeWatch** (Raspberry Pi or desktop Mac/Linux):

```ini
DASHBOARD_THEME=xp
```

Restart the Tkinter dashboard. Set `DASHBOARD_THEME=dark` to go back. This does not require any changes to the Ubuntu Server's agent or NAS configuration.

For one-off previews, override `.env` with:

```bash
bash python-display/start-native.sh --windowed --theme xp
```

The fake-data preview can use `python3 python-display/simulate.py --theme xp` without installing the monitoring dependencies. Details: [Theme selection and XP interactions](../docs/THEMES.md).

## Cross-platform fake-data simulator (v1.1.1)

To preview the **same native Tkinter interface** on macOS, Windows or Linux without a Pi, server, credentials or `.env`, run the new simulator from a complete NodeWatch checkout:

```bash
python3 python-display/simulate.py
```

It opens a **480×320 window with four pages** by default, showing animated **SIMULATION / FAKE DATA** metrics. The simulator needs Python 3, Tkinter and a graphical desktop, but no pip dependencies or connection to your server. Use `--auto-rotate --rotate-seconds 8`, `--fullscreen`, `--pages 3` or `--pi-mode` to preview other layouts. See [the full simulator guide](../docs/SIMULATOR.md).

## Optional autostart at desktop login

If you want NodeWatch to open when the Pi graphical desktop logs in, run `bash python-display/autostart.sh enable` from the repository. To inspect or disable it, run `bash python-display/autostart.sh status` or `bash python-display/autostart.sh disable`. This is **off by default**, doesn't replace an existing startup entry, and doesn't change the Pi's graphical configuration. See [the optional autostart guide](../docs/AUTOSTART.md).

## Controls and settings

- Stats refresh every 5 seconds by default. Automatic rotation is controlled by `AUTO_ROTATE_PAGES` in the **Pi's** `.env`. The default `true` keeps rotating every `ROTATE_SECONDS` (12 seconds unless changed); `false` stops automatic page changes, without stopping live metric refresh. A third page for up to two NAS filesystems appears in Server Mode when `NAS_STORAGE_PATHS` is configured on the Ubuntu Server; see [NAS Storage](../docs/NAS_STORAGE.md). An optional HDD SMART temperature page appears when `HDD_TEMP_DRIVES` is set on Ubuntu Server (page 4 when the NAS page is also enabled); see [HDD Temperatures](../docs/HDD_TEMPERATURES.md).
- Tap left/right side of screen or press Left/Right arrow keys to navigate.
- Press Escape to leave fullscreen.
- Adjust `REFRESH_SECONDS`, `AUTO_ROTATE_PAGES` and `ROTATE_SECONDS` in the Pi's `.env` and restart. Setting `AUTO_ROTATE_PAGES=false` disables timed switching; touch/keyboard navigation still works. `ROTATE_SECONDS` only takes effect when rotation is enabled.
- Optional `SERVICES_JSON` checks TCP port reachability (up to three displayed), not application/process/Docker health. Network totals are cumulative since boot.

## Troubleshooting

- **No Tkinter window:** verify `python3-tk` is installed and launch from a working graphical desktop. Try `--windowed`.
- **Page 1 still shows Pi stats:** `REMOTE_AGENT_URL` is empty; configure Server Mode using the guide.
- **Remote server OFFLINE:** check the agent, server IP/port and matching tokens; the Pi's local stats still work.
- **Missing temperature:** the platform may not expose sensors; unavailable readings appear as a dash.
- **Only three pages after a Pi update:** the HDD page requires a non-empty `hdd_temperatures` list from the **Ubuntu Server** agent. Set `HDD_TEMP_DRIVES` on **Ubuntu**, update both checkouts, restart `server-agent` on Ubuntu and the Tkinter display on the Pi. Use the [live data diagnostic and outcome table](../docs/HDD_TEMPERATURES.md#troubleshooting-case-updated-the-pi-but-still-only-see-three-pages) to distinguish `None`, `[]`, and configured drives.

See also the main [Troubleshooting section](../README.md#troubleshooting).
