# NodeWatch — Browser display

The web dashboard uses Python for telemetry/API and HTML/CSS/JavaScript for its two-page interface.

- `dashboard.py` — web server and shared metrics collector
- `static/` — two-page web UI
- `browser/start-web.sh` — starts the browser version's Python server
- `agent.py` — optional read-only Ubuntu Server metrics agent

## Choose a monitoring method

**[Pi Mode](../docs/PI_MODE.md):** In the Pi's `.env`, set `REMOTE_AGENT_URL=` (empty) and `REMOTE_AGENT_TOKEN=`. The web dashboard uses the Pi's real local CPU, RAM, disk, temperature and uptime; the badge shows **LOCAL PI MODE**. No Ubuntu Server required.

**[Server Mode](../docs/SERVER_MODE.md):** Run `agent.py` on Ubuntu Server and set the Pi's `REMOTE_AGENT_URL` and `REMOTE_AGENT_TOKEN`. Page 1 shows Ubuntu Server metrics, while page 2 still shows the Pi's local health. The badge shows **REMOTE SERVER** or **SERVER OFFLINE**.

## Launch

After installing Python dependencies and configuring the Pi's root `.env`, run from the project root:

```bash
bash browser/start-web.sh
```

Open `http://127.0.0.1:8765/` in a browser on the Raspberry Pi, or use `bash kiosk-start.sh` if Chromium works. Restart the dashboard after switching monitoring modes.

The web server binds to localhost by default. To view it from another device, deliberately configure a network listener and appropriate firewall restrictions.

If Chromium does not work on your Pi 3B, use the [native Python version](../python-display/README.md).
