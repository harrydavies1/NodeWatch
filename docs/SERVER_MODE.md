# Method 2 — Server Mode (monitor Ubuntu Server from the Raspberry Pi)

**Use this mode if you want NodeWatch running on the Raspberry Pi to show live metrics from a separate Ubuntu Server.** The Raspberry Pi's own health remains visible too.

Architecture:

```text
Ubuntu Server (agent.py) -- authenticated /api/metrics over trusted LAN or VPN --> Raspberry Pi (NodeWatch display)
     CPU / RAM / disk / uptime                                            Remote server: page 1
                                                                           Local Pi health: page 2
```

Both the [native Python display](../python-display/README.md) and the [browser display](../browser/README.md) support Server Mode. The Ubuntu Server **does not need a graphical desktop**.

## 1. Install the metrics agent on Ubuntu Server

Run **on the Ubuntu Server**:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip

# For a private repo, configure authorized GitHub SSH access first:
git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
python3 -c 'import secrets; print(secrets.token_urlsafe(36))'
```

Copy the random token printed by the last command. Set these entries in **Ubuntu Server's** `.env`:

```ini
AGENT_TOKEN=PASTE_A_LONG_RANDOM_TOKEN_HERE
AGENT_HOST=0.0.0.0
AGENT_PORT=8766
```

Start the read-only agent:

```bash
./start-agent.sh
```

In a second shell on Ubuntu Server, verify the authenticated endpoint:

```bash
curl -H 'Authorization: Bearer PASTE_A_LONG_RANDOM_TOKEN_HERE' http://127.0.0.1:8766/api/metrics
```

You should receive JSON metrics. A missing or incorrect token returns HTTP 401.

For a long-running agent, see `deploy/server-agent.service.example`. Configure the service paths/user for your machine before enabling it.

**Security:** `AGENT_HOST=0.0.0.0` listens on all server interfaces. Restrict TCP port 8766 to the Pi's trusted LAN/VPN address using your firewall, and never expose this HTTP agent to the public internet. If using UFW, allow SSH access before changing firewall rules. HTTP bearer tokens are not encrypted without TLS or a secure tunnel.

## 2. Install NodeWatch on the Raspberry Pi

Run **on the Raspberry Pi** (skip cloning if the project is already installed):

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv python3-tk

git clone git@github.com:harrydavies1/pi-server-dashboard.git
cd pi-server-dashboard

python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
```

A private repository requires appropriate GitHub access on each machine that clones it.

## 3. Set Server Mode in the Pi's `.env`

Edit **the Raspberry Pi's** `.env`:

```ini
SERVER_NAME="Ubuntu Home Server"
REMOTE_AGENT_URL=http://YOUR_UBUNTU_SERVER_LAN_IP:8766
REMOTE_AGENT_TOKEN=PASTE_THE_SAME_LONG_RANDOM_TOKEN_HERE
REFRESH_SECONDS=5
ROTATE_SECONDS=12
SERVICES_JSON='[]'
```

Replace the server IP and token with your own. Optionally add TCP reachability checks:

```ini
SERVICES_JSON='[{"name":"SSH","host":"YOUR_UBUNTU_SERVER_LAN_IP","port":22}]'
```

Service checks indicate whether a TCP port accepts a connection; they do not verify full application health.

**The key setting is a non-empty `REMOTE_AGENT_URL`.** This selects Server Mode. When the agent is unreachable, NodeWatch displays a server-offline state instead of mislabeling the Pi's stats as remote stats.

## 4. Start the dashboard on the Raspberry Pi

Choose one display:

**Native Python (no Chromium), from the Pi's graphical desktop:**

```bash
cd ~/pi-server-dashboard
bash python-display/start-native.sh
```

**Browser display:**

```bash
cd ~/pi-server-dashboard
bash browser/start-web.sh
```

Then visit `http://127.0.0.1:8765/` from a browser on the Pi.

## 5. Confirm Server Mode

From the **Pi's** project root:

```bash
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("Connected:", s["server"]["connected"]); print("Pi IP:", s["pi"]["ip"])'
```

Expected: `Mode: remote` and `Connected: True`. If `Connected: False`, check the server agent, token, LAN/VPN routing and firewall. Local Pi telemetry remains available under `s["pi"]`.

## 6. What you'll see

- **Page 1 — System Overview:** Ubuntu Server CPU, RAM, disk, temperature (when available), hostname and uptime.
- **Page 2 — Network & Services:** Server connection status, optional TCP checks, plus the Raspberry Pi's own CPU/RAM/IP/uptime and cumulative network traffic.

To switch back to [Pi Mode](PI_MODE.md), clear `REMOTE_AGENT_URL` on the Pi and restart the dashboard. The Ubuntu Server agent is optional in Pi Mode.
