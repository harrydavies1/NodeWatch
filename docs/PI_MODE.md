# Method 1 — Pi Mode (monitor the Raspberry Pi itself)

**Use this mode if you want NodeWatch to show live stats for the Raspberry Pi running the dashboard.** You do **not** need an Ubuntu Server, a second computer, a remote agent or an API token.

Pi Mode works with both the [native Python display](../python-display/README.md) and the [browser display](../browser/README.md).

## 1. Install NodeWatch on the Raspberry Pi

On Raspberry Pi OS:

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv python3-tk

# If the private repo is not already cloned, use SSH with authorized GitHub access:
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard

python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

If you already have `~/pi-server-dashboard`, **do not clone again**. Enter that directory and use its existing environment/configuration. A private repository requires appropriate GitHub credentials.

## 2. Set Pi Mode in the Pi's `.env`

Edit `~/pi-server-dashboard/.env` and use:

```ini
SERVER_NAME="Raspberry Pi"
REMOTE_AGENT_URL=
REMOTE_AGENT_TOKEN=
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

**The key setting is `REMOTE_AGENT_URL=` (empty).** NodeWatch automatically selects Pi Mode and reads the Pi's actual local telemetry with `psutil`. No remote server connection is attempted.

Do not commit your real `.env` file.

## 3. Start the display

Choose **one** display implementation.

**Native Python (no Chromium), from the Pi's graphical desktop:**

```bash
cd ~/pi-server-dashboard
bash python-display/start-native.sh
```

For a small 480×320 preview window instead of fullscreen:

```bash
bash python-display/start-native.sh --windowed
```

The native display requires Tkinter and a functioning graphical display; it does not run from a bare text-only console.

**Browser display:**

```bash
cd ~/pi-server-dashboard
bash browser/start-web.sh
```

Open `http://127.0.0.1:8765/` on the Pi. The browser version can also be opened elsewhere if you intentionally configure a reachable listener and network access.

## 4. What you'll see

- **Page 1 — System Overview:** Pi CPU, RAM, root disk, temperature (if available), hostname and uptime.
- **Page 2 — Network & Services:** Pi hostname/IP, CPU, RAM, uptime, cumulative network traffic and any optional TCP port checks.
- The status shows **PI ONLY** (native) or **LOCAL PI MODE** (browser), rather than pretending a remote Ubuntu Server is connected.

By default, readings refresh every 5 seconds and pages alternate every 12 seconds.

## 5. Confirm Pi Mode

From the project root:

```bash
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("Pi CPU:", s["pi"]["cpu_percent"]); print("Pi IP:", s["pi"]["ip"])'
```

Expected mode: `pi`. CPU usage and IP are live values from the Raspberry Pi.

To monitor an Ubuntu Server **as well as** the Pi, follow [Method 2 — Server Mode](SERVER_MODE.md). Set `REMOTE_AGENT_URL` and `REMOTE_AGENT_TOKEN` on the Pi, then restart the dashboard. The local Pi telemetry remains visible on page 2.
