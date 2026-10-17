# Optional Samba NAS drive usage on NodeWatch

This feature adds a **NAS STORAGE** usage strip to the bottom of NodeWatch's **System Overview (page 1)** in Server Mode. The original **DISK** tile continues to show Ubuntu's system filesystem (`/`).

This monitors **filesystem space**, not Samba activity, transfer speeds, individual shares or file contents. It does not need Samba credentials and does not change your shares. Disabled by default.

## 1. Identify where Samba actually stores files (Ubuntu Server)

Run on your **Dell OptiPlex Ubuntu Server**, with the path changed to the folder exported by Samba:

```bash
test -d /srv/nas/shared && echo "Directory exists"
findmnt -T /srv/nas/shared -o TARGET,SOURCE,FSTYPE
df -h /srv/nas/shared
```

The directory above is **only an example** — don't use it unless it really exists on your NAS. To find your actual shares, you can inspect the Samba configuration:

```bash
testparm -s
```

Look for each share's `path = ...`, then use `findmnt -T` with that path to locate its backing filesystem. `TARGET` is the mounted volume's path (such as `/mnt/storage`); `SOURCE` is the device.

If `TARGET` is `/`, the share lives on the system filesystem rather than a separate NAS drive. NodeWatch will show **NAS ON SYSTEM DISK** instead of treating it as another disk.

## 2. Set the NAS storage path on Ubuntu Server ONLY

```bash
cd ~/pi-server-dashboard
nano .env
```

Add exactly one `NAS_STORAGE_PATH` setting pointing to the existing NAS disk's mountpoint or a folder within it:

```ini
NAS_STORAGE_PATH=/mnt/storage
```

**Replace `/mnt/storage` with your actual path.** It must be an absolute directory path on **Ubuntu Server**, not a Mac SMB URL (`smb://...`), not a Samba share name, and not a Pi path. Keep your existing `AGENT_TOKEN`, `AGENT_HOST`, and `AGENT_PORT` unchanged.

If you have several shares on the same drive, select any path on that drive: storage capacity describes the underlying filesystem, not each Samba share's folder size. Only one NAS volume is displayed currently.

## 3. Update the Ubuntu Server agent and test

If you haven't updated the checkout since this feature was added:

```bash
cd ~/pi-server-dashboard
git pull
```

Restart the existing server agent to load its new code and config:

```bash
sudo systemctl restart server-agent
sudo systemctl status server-agent --no-pager
```

Check the local metric **without printing any tokens**:

```bash
.venv/bin/python -c 'from dotenv import load_dotenv; load_dotenv(".env"); from metrics import snapshot; print(snapshot()["nas_storage"])'
```

Expected: a dictionary with your path, `status: 'ok'`, and `disk_percent`, `disk_used`, `disk_total`, `disk_free`. A status of `system_disk` means your path is on the same filesystem as Ubuntu's `/`; `unavailable` means the path is missing, inaccessible or invalid.

## 4. Update the Raspberry Pi display

On the **Raspberry Pi** (not the Ubuntu Server), keep the existing Server Mode `.env` and token. Update the code:

```bash
cd ~/pi-server-dashboard
git pull
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Mode:", s["server"]["mode"]); print("Connected:", s["server"]["connected"]); print("NAS:", (s["server"]["stats"] or {}).get("nas_storage"))'
```

If `Mode: remote` and `Connected: True`, and `NAS:` shows the configured path and `ok`, restart the existing Tkinter dashboard (reboot the Pi if it already autostarts):

```bash
sudo reboot
```

In **page 1**, CPU, RAM, the Ubuntu root **DISK** and temperature stay unchanged. The additional bottom strip shows **NAS STORAGE**, the percentage used and used/total sizes. No Pi agent configuration is needed.

## If it shows unexpected data

- **NAS STORAGE UNAVAILABLE:** check the exact directory and whether the NAS disk is mounted (`findmnt -T PATH`). A missing disk will not silently be counted as the system disk.
- **NAS ON SYSTEM DISK:** the configured directory is on the same filesystem as Ubuntu's `/`. If you meant a separate drive, verify its mount before relying on the display. This warning is intentional.
- **No NAS strip on the Pi:** ensure the Ubuntu agent is updated, `NAS_STORAGE_PATH` is set in *Ubuntu's* `.env`, its agent was restarted, and the Pi's NodeWatch code has been updated and restarted.
- **Server OFFLINE:** this is a connectivity/agent issue, not an NAS metric. Confirm Server Mode first.
- **Usage appears bigger than Samba files:** filesystem usage includes *all* files on the volume, metadata and reserved capacity — not just the size of a single shared folder.
- **Share on the root filesystem:** the system and NAS measurements may legitimately match; NodeWatch marks this explicitly.

To disable the NAS strip, remove or clear `NAS_STORAGE_PATH` **on Ubuntu**, restart `server-agent` and let the Pi refresh. No other settings need to change.
