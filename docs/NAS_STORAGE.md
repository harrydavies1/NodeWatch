# Monitor two separate Samba NAS drives

NodeWatch can show **both NAS drives independently** on a dedicated third page in Server Mode, without changing Samba or the data on either drive.

Your example hardware is a Dell OptiPlex with Ubuntu Server and two separate ext4 disks:

| Drive | Ubuntu mountpoint | Samba share path |
| --- | --- | --- |
| NAS Drive 1 | `/srv/nas/drive1` | `/srv/nas/drive1` |
| NAS Drive 2 | `/srv/nas/drive2` | `/srv/nas/drive2` |

You can optionally add a fourth page with actual HDD SMART temperature readings using [HDD Temperature monitoring](HDD_TEMPERATURES.md). This is a separate setting and requires restricted read-only smartctl access on Ubuntu Server.

The original **DISK** tile on page 1 still measures Ubuntu's system filesystem (`/`). The **NAS STORAGE** page separately shows each configured volume's percentage used, used/total space, free space and mount-health warnings. The network page still shows the Pi's health.

**This is filesystem capacity monitoring, not Samba traffic, client connections, drive SMART health or individual folder sizes.** An unmounted disk is flagged instead of reporting the Ubuntu system filesystem as NAS capacity.

## Step 1 — Confirm both NAS mounts (Ubuntu Server)

On **Ubuntu Server** (`harry@homeserver`), run:

```bash
findmnt -T /srv/nas/drive1 -o TARGET,SOURCE,FSTYPE
findmnt -T /srv/nas/drive2 -o TARGET,SOURCE,FSTYPE
df -h /srv/nas/drive1 /srv/nas/drive2
```

You should see the two ext4 mounts separately. If either resolves to `/` instead of its NAS mount, **check the disk mount before proceeding**. Do not format or repartition anything.

## Step 2 — Update and configure the Ubuntu Server agent

Only on **Ubuntu Server**:

```bash
cd ~/pi-server-dashboard
git pull
nano .env
```

Add **one** `NAS_STORAGE_PATHS` line exactly like this:

```ini
NAS_STORAGE_PATHS='[{"name":"NAS Drive 1","path":"/srv/nas/drive1"},{"name":"NAS Drive 2","path":"/srv/nas/drive2"}]'
```

Use the **existing mount paths** above. Keep `AGENT_TOKEN`, `AGENT_HOST` and `AGENT_PORT` unchanged.

If you previously configured the old single-drive line `NAS_STORAGE_PATH=/srv/nas/drive1`, **remove or comment out that old line** for clarity. The new setting is independent, but this avoids duplicate legacy disk reporting.

Save using Ctrl+O, Enter, Ctrl+X, then restart the agent:

```bash
sudo systemctl restart server-agent
sudo systemctl status server-agent --no-pager
```

Check the new data **locally on Ubuntu Server** without exposing the token:

```bash
.venv/bin/python -c 'from dotenv import load_dotenv; load_dotenv(".env"); from metrics import snapshot; print(snapshot()["nas_volumes"])'
```

You should see **two dictionaries**: one for each drive, with `status: 'ok'`, `disk_percent`, `disk_used`, `disk_total` and `disk_free`. The figures will reflect your live storage, not example values.

## Step 3 — Update the Raspberry Pi dashboard

On the **Raspberry Pi** (`admin@pi`), keep the existing working Server Mode `.env`, LAN address and token:

```bash
cd ~/pi-server-dashboard
git pull
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("Connected:", s["server"]["connected"]); print("NAS drives:", (s["server"]["stats"] or {}).get("nas_volumes"))'
```

Expected: `Mode: remote`, `Connected: True`, and two entries corresponding to your NAS drives.

Restart the native dashboard to load its new **three-page** display. If it already autostarts after the Pi desktop login, the simplest method is:

```bash
sudo reboot
```

Your available pages are (automatic switching defaults to every 12 seconds, but you can stop it using `AUTO_ROTATE_PAGES=false` in the Pi's `.env`):

1. **System Overview** — Ubuntu Server CPU, RAM, root disk, temperature and uptime.
2. **Network & Services** — Pi health, network totals, server connection, optional TCP checks.
3. **NAS Storage** — Drive 1 and Drive 2, each with its own used percentage, capacity and mount warning.

Tap the screen or use Left/Right arrow keys to switch pages manually. With `AUTO_ROTATE_PAGES=false`, NodeWatch stays on the chosen NAS page while still refreshing the readings. Set `AUTO_ROTATE_PAGES=true` to resume cycling every `ROTATE_SECONDS` (for example, 8 seconds). Restart the Pi's dashboard after changing this setting; no Ubuntu agent restart is required.

## Warning states and troubleshooting

- **Drive reports OK:** the configured directory is on a filesystem other than Ubuntu's root (`/`), and disk usage was readable.
- **MOUNT MISSING / SYSTEM DISK:** the configured NAS directory is now on the same filesystem as `/`. This often means the NAS drive isn't mounted, even though the directory still exists. NodeWatch deliberately **doesn't show root disk figures as NAS capacity**. Confirm with `findmnt -T /srv/nas/drive1` or `/srv/nas/drive2`.
- **UNAVAILABLE:** the configured directory is missing, inaccessible or invalid. Confirm that the directory exists and the `server-agent` service user can access it.
- **NAS CONFIG / invalid:** `NAS_STORAGE_PATHS` must be a correctly quoted JSON array with **one or two** objects, each containing a `name` and an absolute `path`; avoid duplicate `.env` keys.
- **No third page:** set `NAS_STORAGE_PATHS` on **Ubuntu Server**, not the Pi. Update both Git checkouts, restart `server-agent`, verify the Pi receives `nas_volumes`, then restart the Pi's Tkinter process.
- **Server OFFLINE:** verify the server agent/network first using the [Server Mode connection test](SERVER_MODE.md#4-check-the-connection).
- **Storage doesn't match individual Samba folder size:** the meter reads all usage on the filesystem, including files outside a particular share.

To return to the old single-drive display, clear `NAS_STORAGE_PATHS` and optionally use `NAS_STORAGE_PATH=/srv/nas/drive1` on Ubuntu. To disable NAS monitoring entirely, clear both settings and restart the Ubuntu agent. Pi and Server Mode otherwise continue working.

This does **not** change Samba, disks, mount settings, existing files or the Pi's system autostart.
