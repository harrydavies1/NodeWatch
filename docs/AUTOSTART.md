# Optional startup — launch NodeWatch automatically after desktop login

**This feature is optional.** Nothing is installed, enabled or modified simply by cloning NodeWatch. Pi Mode and Server Mode use the exact same startup setup.

The native Tkinter dashboard requires an **already-working graphical desktop**. This method uses the standard per-user XDG desktop autostart mechanism, compatible with LXDE and many other Linux desktops. It does not start a browser or create a headless system service.

## 1. Requirements

- NodeWatch is installed on the Raspberry Pi, including `.venv` and the Pi's `.env`.
- The Tkinter dashboard already launches manually on the Pi's graphical desktop:
  `bash python-display/start-native.sh`.
- You want it to open when the **same user** logs in to the desktop.
- Make sure other dashboards are not separately configured to open at the same time.

You do **not** need to install a second copy of NodeWatch. New public-repository installs can use `git clone https://github.com/harrydavies1/NodeWatch.git pi-server-dashboard`; existing installations keep their current folder. The paths below assume the local checkout is `~/pi-server-dashboard`.

## 2. Enable startup (optional)

Run on the **Raspberry Pi**, not on your Mac/Windows/Linux workstation:

```bash
cd ~/pi-server-dashboard
bash python-display/autostart.sh enable
```

This creates `~/.config/autostart/nodewatch.desktop`, with an absolute path to the NodeWatch launcher in the current repository. The launcher inherits the graphical session environment and delays startup by 8 seconds. No `sudo` is needed.

**If the entry already exists, the command leaves it untouched.** This protects a working custom NodeWatch launcher. No new window opens until a subsequent desktop login.

If you want it to appear right after boot, use your Pi's **desktop auto-login** option. Otherwise, it starts only after someone logs into the Pi desktop.

## 3. Check or disable startup

```bash
cd ~/pi-server-dashboard
bash python-display/autostart.sh status
bash python-display/autostart.sh disable
```

The disable command moves the existing startup file to `~/.config/nodewatch/nodewatch.desktop.disabled` instead of deleting it. It doesn't kill a dashboard already open on the screen.

Re-enable with:

```bash
bash python-display/autostart.sh enable
```

If a saved file exists, it is restored **without altering its contents**. If your existing startup configuration already works, you do not need to re-install it.

## 4. Test

Log out of the graphical desktop and log back in, or reboot if desktop auto-login is configured. NodeWatch should start fullscreen after a short delay. The same launcher works with **Pi Mode** and **Server Mode** because it reads the Pi's `.env`.

If NodeWatch does not appear, connect over SSH and run:

```bash
cd ~/pi-server-dashboard
bash python-display/autostart.sh status
pgrep -af '[n]ative_dashboard.py'
tail -n 40 ~/nodewatch-autostart.log
```

The log is created when the provided autostart launcher runs; if the desktop never launched it, the log may not exist. If you already had a custom startup entry, check the logs for **that existing launcher** instead.

### Common issues

- **Desktop only, no NodeWatch:** Check that you are logged in to the graphical desktop, the startup entry is enabled and your desktop supports XDG autostart.
- **Tkinter display error:** Confirm the Tkinter dashboard opens normally from the Pi desktop; an SSH terminal does not automatically provide a graphical display.
- **Two dashboards overlap:** Disable any separate dashboard autostart entry; only configure one launcher per dashboard.
- **Project moved or renamed:** Disable and then re-enable the entry after removing an obsolete generated file, or update the path in `~/.config/autostart/nodewatch.desktop`.
- **No startup log:** The optional launcher may never have executed; check the desktop autostart entry first.

This setup intentionally does **not** alter your Pi's graphical-session configuration or any system services. It only enables/disables a file in your own account.
