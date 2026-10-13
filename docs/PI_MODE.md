# Method 1 — Pi Mode: monitor the Raspberry Pi itself

Pi Mode displays **live stats from the Raspberry Pi running NodeWatch**. You do not need a separate server, an agent, or an agent token.

## 1. Install NodeWatch on the Pi

```bash
sudo apt update
sudo apt install -y git python3 python3-tk python3-venv python3-pip
# For private repositories, configure GitHub SSH access before cloning.
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

If you already have `~/pi-server-dashboard`, do not clone again. Continue in the existing directory.

## 2. Set Pi Mode

Edit the Raspberry Pi's `~/pi-server-dashboard/.env`:

```ini
SERVER_NAME="Raspberry Pi"
REMOTE_AGENT_URL=
REMOTE_AGENT_TOKEN=
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

**Keep `REMOTE_AGENT_URL` empty.** This selects local Pi telemetry collected by `metrics.py` using `psutil`. No remote connection is attempted.

## 3. Run the Tkinter display

From the Pi's graphical desktop:

```bash
cd ~/pi-server-dashboard
bash python-display/start-native.sh
```

For a windowed 480×320 preview, use:

```bash
bash python-display/start-native.sh --windowed
```

This is a native Python application, not a browser application. It needs a graphical display and screen driver.

## 4. Confirm the mode

```bash
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("CPU:", s["pi"]["cpu_percent"]); print("IP:", s["pi"]["ip"])'
```

Expected mode: `pi`. CPU and IP are read directly from the Pi.

Page 1 shows CPU, RAM, disk, temperature and uptime. Page 2 shows Pi networking, host information and any optional TCP port checks. The status reads **PI ONLY**. Network counters are total bytes since boot, not current transfer rates.

To switch to remote monitoring when an Ubuntu Server becomes available, follow [Method 2 — Server Mode](SERVER_MODE.md). Your Pi's metrics remain visible on the second page.
