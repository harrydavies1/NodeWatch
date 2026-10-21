# NodeWatch themes — dark and classic Windows XP

NodeWatch includes two visual themes for its **native Python/Tkinter interface**:

| Theme | Appearance | Default? |
| --- | --- | --- |
| `dark` | The existing blue-black NodeWatch interface | **Yes** |
| `xp` | Bright Windows XP Luna-inspired blue window, green Start control, blue taskbar, classic panels and chunky blue progress bars | No, opt in |

The Windows XP mode is intentionally **very old-school** while keeping all current NodeWatch functionality: system overview, network and services, NAS storage and HDD temperatures. It draws original vector artwork in Tkinter. No licensed Windows wallpaper, Microsoft branding assets, custom fonts, browser or additional dependencies are needed.

## Raspberry Pi: make XP the default

On the **Raspberry Pi running the screen**, update your existing checkout:

```bash
cd ~/pi-server-dashboard
git pull --ff-only
nano .env
```

Add this setting **once** (or edit it if it is present):

```ini
DASHBOARD_THEME=xp
```

Save and restart the NodeWatch Tkinter dashboard. If your Pi automatically launches NodeWatch on desktop login, you can reboot the Pi to reload it:

```bash
sudo reboot
```

Your Ubuntu Server's `server-agent` and its settings **do not need to change**; this is a display-only feature. `DASHBOARD_THEME` belongs in the display machine's local configuration file, **not** the Ubuntu server agent's configuration file.

### Switch back to the original theme

Edit the **same Pi `.env`** and use:

```ini
DASHBOARD_THEME=dark
```

Then restart the dashboard. Unknown/missing theme values also use the original dark look.

## Mac or Linux: try the XP theme with real server stats

If NodeWatch is already configured on your Mac or other desktop to fetch real Ubuntu metrics over Tailscale or your private network:

```bash
cd nodewatch
git pull --ff-only
bash python-display/start-native.sh --windowed --theme xp
```

The exact checkout folder name may instead be `NodeWatch`; run the commands **from that folder**. The one-off `--theme xp` flag overrides `.env` without modifying the file. Omit `--windowed` to run fullscreen.

To make XP the default, add `DASHBOARD_THEME=xp` to the **desktop's own** `.env` and launch normally. The Ubuntu agent's network settings, token and other secrets remain unchanged.

**If the remote server shows OFFLINE or 401 Unauthorized, that is an existing connection/authentication issue, not a theme issue.** Fix the existing `REMOTE_AGENT_URL` and `REMOTE_AGENT_TOKEN` as described in [Server Mode](SERVER_MODE.md). The theme doesn't modify Tailscale, tokens, firewall rules or network calls.

## No server? Use the built-in simulator

For a quick offline preview on macOS, Windows or desktop Linux with **Python 3 and Tkinter**, use a complete GitHub checkout:

```bash
python3 python-display/simulate.py --theme xp
```

It shows all four pages with clearly marked **SIMULATION / FAKE DATA** and needs no `.env`, agent, SSH, pip packages or network connection. To watch it automatically cycle:

```bash
python3 python-display/simulate.py --theme xp --auto-rotate --rotate-seconds 8
```

To preview Pi-only mode:

```bash
python3 python-display/simulate.py --theme xp --pi-mode
```

Windows users can replace `python3` with `py`. See [Simulator Setup](SIMULATOR.md).

## Interacting with the old-school theme

- **Green Start button:** opens a working Start-style menu containing the available NodeWatch pages. Select a page by clicking or tapping its entry.
- **Window controls:** minimise, toggle fullscreen or close NodeWatch, using the three small controls at the top-right of the XP-style window.
- **Tap left/right:** outside those controls, tap the left or right half of the screen to change pages (identical to the dark theme).
- **Keyboard:** Left/Right arrows or Space navigate; Escape closes the dashboard.
- **Automatic page cycling:** unchanged. Set `AUTO_ROTATE_PAGES=true` and `ROTATE_SECONDS=12` in the Pi/desktop `.env`, or set `AUTO_ROTATE_PAGES=false` to stop automatic changes. The simulator uses `--auto-rotate` instead.
- **System tray:** bottom-right displays the clock and the current page number. The taskbar highlights the current dashboard page.

This is an **XP-inspired skin**, not a copy of Windows XP, a Windows virtual machine, or a desktop operating system. The original NodeWatch fonts may fall back to your platform's available Tahoma-like font; exact rendering can vary slightly by operating system and SPI display driver.

## Troubleshooting

| Issue | Fix |
| --- | --- |
| Still looks dark after updating | Check `DASHBOARD_THEME=xp` in the **display machine's** `.env` and restart the Tkinter dashboard. Or override with `--theme xp` once. |
| My Pi changed but the Mac did not | Each display machine has its **own local** theme setting; set the Mac's `.env` separately or use `--theme xp`. |
| The Ubuntu agent was updated but nothing happened | Update the Pi/Mac **display checkout** instead. The agent doesn't draw the GUI and doesn't select the theme. |
| No fourth page | The optional NAS and HDD pages still require the Ubuntu Server to send configured data. See [HDD temperature troubleshooting](HDD_TEMPERATURES.md). |
| No Tkinter window on desktop | Run `python3 -m tkinter` to test your Python GUI environment and make sure you have an active graphical desktop. |
| Text or fonts differ slightly | Tkinter uses locally available system fonts. The design is optimized for the 480×320 Pi display, but font rasterisation varies by platform. |

**Safe upgrade:** this visual option doesn't modify NAS storage, Samba, SMART readings, the Minecraft server, Tailscale or your Ubuntu systemd services.
