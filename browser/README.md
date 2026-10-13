# NodeWatch — Browser display

The original web dashboard remains in the repository root:

- `dashboard.py` — local Python HTTP server
- `static/` — two-page HTML/CSS/JS interface
- `start.sh` — starts the web server
- `kiosk-start.sh` — starts Chromium in kiosk mode
- `agent.py` — read-only Ubuntu Server metrics agent, shared by both versions

After installing dependencies and setting up `.env`, start it from the project root:

```bash
bash browser/start-web.sh
```

Open http://127.0.0.1:8765/ on your Raspberry Pi, or use `bash kiosk-start.sh` if Chromium works. The server can be viewed from another device only if you deliberately configure a network listener and a suitable firewall.

If Chromium will not open on your Pi 3B, use the [native Python version](../python-display/README.md) instead.
