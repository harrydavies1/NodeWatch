# Method 2 — Server Mode: monitor Ubuntu Server on your Raspberry Pi

Server Mode displays **Ubuntu/Linux server telemetry on NodeWatch's first page** and **Raspberry Pi stats on the second page**. The server runs an optional read-only metrics agent; the display stays on the Pi.

**Reference server hardware:** A basic **Dell OptiPlex** desktop running **Ubuntu Server**, with the NodeWatch display on a Raspberry Pi 3B and 3.5-inch OSOYOO SPI RPi Display V1.0. The Pi display was tested in Pi Mode; check the agent connection using the commands below to validate Server Mode end to end.

## 1. Set up the agent on your Ubuntu Server

On the **Ubuntu Server**, install the agent dependencies:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
# Public repository: HTTPS clone does not require a GitHub SSH key.
git clone https://github.com/harrydavies1/NodeWatch.git pi-server-dashboard
cd pi-server-dashboard
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
python3 -c 'import secrets; print(secrets.token_urlsafe(36))'
```

If the project is already installed on Ubuntu Server, skip cloning and installation. The repository is public and now named `NodeWatch`; the chosen `pi-server-dashboard` directory is just the local folder name.

Copy the randomly generated token. Edit **Ubuntu Server's `.env`**, setting these values. **Add `AGENT_TOKEN`, `AGENT_HOST` and `AGENT_PORT` if they are not already present**; do not add duplicate keys:

```ini
AGENT_TOKEN=PASTE_YOUR_LONG_RANDOM_TOKEN_HERE
AGENT_HOST=0.0.0.0
AGENT_PORT=8766
```

The Ubuntu Server does not need a desktop or Tkinter: `agent.py` runs headlessly.

Start the agent on the server:

```bash
bash start-agent.sh
```

To check it from another Ubuntu Server terminal:

```bash
curl -H 'Authorization: Bearer PASTE_YOUR_LONG_RANDOM_TOKEN_HERE' http://127.0.0.1:8766/api/metrics
```

You should receive JSON with server CPU, RAM, disk, uptime and other metrics. A wrong token returns `401`.

### Make the server agent start automatically (optional)

On **Ubuntu Server**, stop any manually running `start-agent.sh` first to avoid a port conflict. Copy the example service and edit the user/path placeholders to match the **Ubuntu Server** account (not the Pi account):

```bash
sudo cp deploy/server-agent.service.example /etc/systemd/system/server-agent.service
sudo nano /etc/systemd/system/server-agent.service
```

Replace **every** `YOUR_USERNAME` in the copied file, save it, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now server-agent
sudo systemctl status server-agent --no-pager
```

For a Pi connecting over the network, `AGENT_HOST=0.0.0.0` makes the agent listen on server interfaces. Restrict port 8766 to the Pi over a trusted LAN or VPN. Do not expose the unencrypted HTTP endpoint to the public internet.

## 2. Change NodeWatch to Server Mode on the Raspberry Pi

**This is the only NodeWatch display change needed once the agent is set up.** SSH into the Pi and edit its **own** `.env`:

```bash
cd ~/pi-server-dashboard
nano .env
```

Edit the **existing keys** in the Pi's `.env` (only add a key if it is missing — do not create duplicate `REMOTE_AGENT_URL` or `REMOTE_AGENT_TOKEN` lines):

```ini
SERVER_NAME="Ubuntu Home Server"
REMOTE_AGENT_URL=http://YOUR_UBUNTU_SERVER_LAN_IP:8766
REMOTE_AGENT_TOKEN=PASTE_YOUR_LONG_RANDOM_TOKEN_HERE
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

Replace the example IP with **your server's real IP**, and use the **same token** as `AGENT_TOKEN` on the Ubuntu Server. Do not put the Pi's own IP in `REMOTE_AGENT_URL` unless the agent actually runs on that Pi.

A **non-empty `REMOTE_AGENT_URL`** selects Server Mode. If the server is unreachable, NodeWatch marks it OFFLINE rather than showing Pi readings under a remote-server label.

For optional TCP connection checks, use something like:

```ini
SERVICES_JSON='[{"name":"SSH","host":"YOUR_UBUNTU_SERVER_LAN_IP","port":22}]'
```

These are TCP port availability checks, not deep application health checks. The native 480×320 display renders **up to three checks**.

## 3. Restart the Tkinter display on the Pi

If running manually, stop it with Ctrl+C and restart from the Pi's graphical desktop:

```bash
cd ~/pi-server-dashboard
bash python-display/start-native.sh
```

If NodeWatch starts automatically when you log into the Pi desktop, **reboot the Pi to reload `.env`**:

```bash
sudo reboot
```

No Python code changes and no browser are required. The next launch reads the new configuration.

## 4. Check the connection

On the Pi:

```bash
cd ~/pi-server-dashboard
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("Connected:", s["server"]["connected"]); print("Pi IP:", s["pi"]["ip"])'
```

Expect `Mode: remote` and `Connected: True`. This verifies that the Pi can reach the agent and receive data; it doesn't test the physical display by itself. Page 1 now shows server CPU/RAM/disk/an available temperature sensor/uptime, while page 2 shows the connection and the Raspberry Pi's own health.

## Troubleshooting Server Mode

- **`Mode: pi`:** `REMOTE_AGENT_URL` is still empty or you edited the wrong `.env`. Edit the **Pi's** configuration and restart NodeWatch.
- **`Mode: remote`, `Connected: False`:** check that the Ubuntu Server agent is running, the server IP/port are correct, and port 8766 is reachable from the Pi.
- **`401 Unauthorized`:** `REMOTE_AGENT_TOKEN` on the Pi and `AGENT_TOKEN` on Ubuntu Server must match exactly. On Ubuntu Server, use the authenticated `curl` test in step 1 to confirm the agent accepts the token.
- **Server shows OFFLINE:** the Pi dashboard still works and displays local Pi stats; correct the server connection rather than changing display code.
- **No temperature reading:** the server may not expose supported sensors.

To use **Pi Mode** again, clear both `REMOTE_AGENT_URL` and `REMOTE_AGENT_TOKEN` in the Pi's `.env` and restart NodeWatch. See [Pi Mode](PI_MODE.md).

## Optional automatic startup on the Pi

To launch the Tkinter dashboard automatically when the Pi desktop logs in, see [Optional desktop autostart](AUTOSTART.md). This is opt-in and works with Server Mode without changing the agent configuration.
