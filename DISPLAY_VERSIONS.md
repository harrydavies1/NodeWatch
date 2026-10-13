# Choose your NodeWatch display

Both versions use the same Python telemetry collector, optional Ubuntu Server agent and `.env` file. No second GitHub repository is needed.

| Version | Interface | Launch command |
| --- | --- | --- |
| [Browser](browser/README.md) | HTML, CSS and JavaScript in Chromium or another browser | `bash browser/start-web.sh` |
| [Native Python](python-display/README.md) | Tkinter canvas with no Chromium | `bash python-display/start-native.sh` |

Both show two auto-switching pages with system overview and network/service stats. The native Python version is designed for small screens, including a common 480×320 SPI panel on the Raspberry Pi 3B.

## Quick native setup on Raspberry Pi OS

```bash
sudo apt update
sudo apt install -y python3-tk python3-venv python3-pip
cd ~/pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
bash python-display/start-native.sh
```

**No Chromium required**, but Tkinter still needs a **working graphical desktop and SPI driver**. If the panel only shows Linux console text, the native GUI will not work without additional display configuration. Check the version READMEs for full instructions.

Your real `.env` must **never** be committed to GitHub.
