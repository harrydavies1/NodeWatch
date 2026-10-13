# NodeWatch — Native Python display (no Chromium)

This is a second display implementation for a Raspberry Pi 3B with a 3.5-inch SPI screen, often 480×320.

It uses **Tkinter** to show the same two auto-switching information pages without a browser. It shares `dashboard.collect_state()` and the same root `.env` configuration and Ubuntu Server monitoring agent.

## Requirements

- Raspberry Pi OS with a **working graphical desktop session** (X11 or Tk-compatible Wayland).
- An SPI display driver that can show the graphical desktop.
- Python 3 with `python3-tk`, `python3-venv`, and Python dependencies from `requirements.txt`.

**Important:** Tkinter does not run directly on a bare Linux text console. It does not require Chromium, but a functioning graphical display is still essential.

## Install on Raspberry Pi OS

```bash
sudo apt update
sudo apt install -y git python3 python3-tk python3-venv python3-pip
# For a private GitHub repository, set up SSH credentials first:
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
nano .env
```

For testing Pi-only metrics, leave `REMOTE_AGENT_URL=` empty. To monitor Ubuntu Server, set `REMOTE_AGENT_URL` and `REMOTE_AGENT_TOKEN` to match the agent configuration in the root README.

Run from the graphical desktop terminal:

```bash
bash python-display/start-native.sh
```

Preview at a 480×320 window size:

```bash
bash python-display/start-native.sh --windowed
```

## Controls and troubleshooting

- Two pages auto-rotate every 12 seconds; stats refresh every 5 seconds by default.
- Tap the left or right half to switch pages; Left/Right arrow keys also work.
- Escape exits fullscreen.
- Change `ROTATE_SECONDS` and `REFRESH_SECONDS` in `.env` to adjust the timing.
- Check `python3 -m tkinter` from the Pi's desktop terminal if a GUI will not open.
- If the desktop appears only on HDMI, verify your SPI screen model, driver, OS release and display routing before changing boot overlays.
- Do not run Chromium alongside the native app on the Pi 3B if memory is tight.

Hardware testing on the specific Raspberry Pi 3B and SPI panel remains to be done. The remote agent must stay on a trusted LAN or VPN, not the open internet.
