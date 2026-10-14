# Optional Ubuntu Server boot startup — NodeWatch metrics agent

**Off by default.** This option starts the Ubuntu Server's read-only `agent.py` automatically at boot, without anyone logging in. This is different from the [optional Pi desktop autostart](AUTOSTART.md), which opens the Tkinter dashboard on the Raspberry Pi.

The Ubuntu agent **listens for incoming requests**; it does not push data by itself. NodeWatch on the Pi polls the agent, normally every five seconds.

## 1. Finish Server Mode setup first

Complete [Server Mode setup](SERVER_MODE.md) on the **Ubuntu Server**. Install Python dependencies, create `.venv` and configure the **server's** `.env`:

```ini
AGENT_TOKEN=YOUR_GENERATED_LONG_RANDOM_TOKEN
AGENT_HOST=0.0.0.0
AGENT_PORT=8766
```

Generate a random token as described in the Server Mode guide. The startup helper requires a token of at least 24 characters. Do **not** use the example token above literally.

`AGENT_HOST=0.0.0.0` makes the agent listen on the server's LAN interfaces. Restrict its TCP port to the Raspberry Pi through your firewall or a trusted VPN. Do not expose this unauthenticated-transport HTTP endpoint publicly.

First start the agent manually on **Ubuntu Server**:

```bash
cd ~/pi-server-dashboard
bash start-agent.sh
```

From another terminal on that same server, test it (replace the token):

```bash
curl -H 'Authorization: Bearer YOUR_ACTUAL_TOKEN' http://127.0.0.1:8766/api/metrics
```

You should get JSON containing CPU and memory statistics. **Stop the manual agent using Ctrl+C** before enabling autostart, or the service can fail with "address already in use".

## 2. Enable autostart on Ubuntu Server

Run as your **regular Ubuntu login user** (the script calls `sudo` for system changes):

```bash
cd ~/pi-server-dashboard
bash deploy/server-agent-autostart.sh enable
```

The helper validates the server installation and `.env`, generates a `systemd` service at `/etc/systemd/system/server-agent.service` using your real username and checkout location, then enables and starts it.

The systemd service starts automatically on future Ubuntu boots **without desktop login**. It also restarts if the agent crashes. Network initialization may delay the service briefly.

The helper does **not** overwrite an existing custom `server-agent.service`. If you previously installed the example manually, use `sudo systemctl enable --now server-agent` to activate your existing service instead.

## 3. Check the service, logs and disable

On **Ubuntu Server**:

```bash
cd ~/pi-server-dashboard
bash deploy/server-agent-autostart.sh status
bash deploy/server-agent-autostart.sh logs
```

Successful status normally shows **enabled** for boot and **active** for the current session. To stop the agent **now and on subsequent boots**:

```bash
bash deploy/server-agent-autostart.sh disable
```

Run the `enable` command again to restore it. Disabling doesn't erase the service unit or your token.

## 4. Test after an Ubuntu reboot

After you confirm SSH access and the service is running, you can reboot **Ubuntu Server**:

```bash
sudo reboot
```

Reconnect, then check:

```bash
cd ~/pi-server-dashboard
bash deploy/server-agent-autostart.sh status
```

The Pi's `.env` should have `REMOTE_AGENT_URL=http://YOUR_UBUNTU_SERVER_LAN_IP:8766` and `REMOTE_AGENT_TOKEN` matching the server's `AGENT_TOKEN`. If your Pi starts before Ubuntu Server is ready, NodeWatch may show **OFFLINE** temporarily and reconnect on a later refresh.

## Troubleshooting

- **No `.venv/bin/python`:** complete the server-side installation first.
- **`AGENT_TOKEN` error:** edit **Ubuntu Server's** `.env` and use a newly generated token of 24+ characters.
- **`Address already in use`:** stop `bash start-agent.sh` or any second copy of the agent before enabling systemd.
- **An existing unit was not created by the helper:** it intentionally refuses to overwrite your manual service. Use `sudo systemctl enable --now server-agent` with that existing unit, or back it up and manage it yourself.
- **Server service is active but Pi shows OFFLINE:** ensure `AGENT_HOST=0.0.0.0` or the correct LAN binding, check the Ubuntu firewall, actual server IP and matching tokens. Try the authenticated `curl` test on the server and the [Pi connection check](SERVER_MODE.md#4-check-the-connection).
- **Project path unsupported:** the helper needs a simple path without spaces or special systemd syntax characters, such as `/home/ubuntu/pi-server-dashboard`.
- **Logs show a crash:** inspect `bash deploy/server-agent-autostart.sh logs` and try `bash start-agent.sh` manually after disabling the service to identify Python errors.

This option only changes the agent startup **on Ubuntu Server**. It does not modify the Raspberry Pi display or its autostart settings.
