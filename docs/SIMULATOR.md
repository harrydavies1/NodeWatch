# NodeWatch simulator — preview on macOS, Windows or Linux

The optional **NodeWatch simulator** runs the **same Tkinter GUI code** as the Raspberry Pi display using **fake, animated metrics**. It previews the full interface without a Raspberry Pi, Ubuntu Server, network access, token, configuration file, NAS disks, SMART permissions or pip dependencies.

You need **Python 3 with Tkinter and a graphical desktop**. Tkinter is a Python standard-library GUI package but may be missing from some Python installations. The simulator shares the existing `native_dashboard.py` and `ui_helpers.py` files; use a **full NodeWatch repository checkout**, not just the simulator script copied on its own.

## macOS quick start

Open Terminal:

```bash
git clone https://github.com/harrydavies1/NodeWatch.git
cd NodeWatch
python3 -m tkinter
```

The Tkinter check should open a test window. Close it before launching NodeWatch. If your Mac's Python reports `No module named tkinter`, install a Python 3 distribution with matching Tcl/Tk (the official macOS installer at python.org is a common option), then retry. No `pip install -r requirements.txt` is needed.

```bash
python3 python-display/simulate.py
```

Already cloned NodeWatch? Use `cd NodeWatch && git pull --ff-only` instead of cloning again.

## Windows

Install Python 3 with its optional **tcl/tk and IDLE** component enabled. From PowerShell in your NodeWatch checkout:

```powershell
py -m tkinter
py python-display/simulate.py
```

## Ubuntu / Debian / Raspberry Pi OS

```bash
sudo apt install -y python3 python3-tk
python3 -m tkinter
python3 python-display/simulate.py
```

On other Linux distributions, install the matching Python Tkinter package and run from a graphical desktop.

## Preview commands

```bash
# Default: 480x320 window, 4 pages, manual navigation
python3 python-display/simulate.py

# Automatic page switching every 8 seconds
python3 python-display/simulate.py --auto-rotate --rotate-seconds 8

# Two-page Pi Mode mockup
python3 python-display/simulate.py --pi-mode

# Three-page server dashboard preview
python3 python-display/simulate.py --pages 3

# Fullscreen, fake stats updated every 5 seconds
python3 python-display/simulate.py --fullscreen --refresh-seconds 5

# CLI help works even without Tkinter installed
python3 python-display/simulate.py --help
```

Flags: `--pages {2,3,4}`, `--pi-mode`, `--fullscreen`, `--auto-rotate`, `--rotate-seconds` and `--refresh-seconds`.

- Click **left or right half** of the screen or use the **Left/Right arrow keys** to change pages. Space advances one page.
- Press **Escape** to quit; in windowed mode, you can also close the window normally.
- Auto-rotation is **disabled by default** for easier previews. Turn it on with `--auto-rotate`. The real Pi's setting is not changed.

## Displayed fake pages

1. **System Overview** — simulated CPU, RAM, root disk, temperature and uptime
2. **Network & Services** — simulated server connection, Pi health and service checks
3. **NAS Storage** — two fake NAS drive storage readings
4. **HDD Temperatures** — two fake SMART temperatures, including a hot-drive demonstration

The screen is clearly labelled **SIMULATION / FAKE DATA**. Animated numbers are *examples only*. The simulator **does not call the real metrics collector**, contact your server, read SMART data, check ports or use any real network or disk information. The normal Pi and Ubuntu NodeWatch monitoring software is unchanged.

## Troubleshooting

| Symptom | Solution |
| --- | --- |
| `ModuleNotFoundError: tkinter` | Install Python/Tkinter, then run `python3 -m tkinter` to verify. |
| `No module named native_dashboard` or `ui_helpers` | Use a full repository checkout, with all three files in `python-display/`. |
| `TclError` / no GUI window | Start from a graphical desktop session; headless terminals without GUI forwarding cannot show windows. |
| Only two/three pages | Remove `--pi-mode` or `--pages 2`/`--pages 3` flags. Four pages is the default. |
| Pages don't rotate | Add `--auto-rotate`; default preview mode is manual. |
| Slight font differences | Tkinter uses locally available fonts, so different OSes may substitute fonts while keeping the same page layout. |

This is a preview tool, **not actual monitoring**. For live stats see the [Server Mode guide](SERVER_MODE.md). It never changes your real configuration files or NAS drives.
