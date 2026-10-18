# Optional HDD temperatures — NodeWatch Server Mode

NodeWatch can display **SMART HDD temperatures** on a dedicated page on the Raspberry Pi. With the existing optional NAS storage-usage page enabled, this becomes **page 4**:

1. System Overview
2. Network & Services
3. NAS Storage (optional, `NAS_STORAGE_PATHS`)
4. HDD Temperatures (optional, `HDD_TEMP_DRIVES`)

If NAS storage usage is not configured, temperatures appear as page 3. No changes to Samba, partitions, mounts or files are made by this feature. It does not control fans or report disk SMART health. Temperature labels (normal below 45°C, warm at 45–49.9°C, hot at 50°C and above) are *advisory*, not device-specific manufacturer limits.

The data comes from `smartctl` running **on Ubuntu Server**, not from the Pi. Readings are cached for **60 seconds** even if the Pi refreshes more often. The `-n standby` option is used to avoid spinning up sleeping ATA drives where supported. A sleeping drive displays `DRIVE SLEEPING`; a missing drive or a SMART permission error displays `UNAVAILABLE`.

## Step 1 — Confirm the drives (Ubuntu Server)

```bash
lsblk -o NAME,SIZE,MODEL,FSTYPE,MOUNTPOINTS
sudo apt update
sudo apt install -y smartmontools
```

For the reference Dell server, the original disks were Seagate `/dev/sdb` (NAS Drive 1) and Hitachi `/dev/sdc` (NAS Drive 2). **Device letters can change after reboot or replacement.** Prefer a stable `/dev/disk/by-id/` symlink tied to each physical disk:

```bash
ls -l /dev/disk/by-id/ | grep -E 'ata-|wwn-'
```

Choose the `ata-` or `wwn-` entry pointing to the whole disk (`../../sdb`, not `../../sdb1`; similarly for `sdc`). Never include partition suffixes such as `-part1`.

## Step 2 — Add the configuration to the Ubuntu agent

Update the **existing checkout** on Ubuntu Server (do not overwrite `.env`):

```bash
cd ~/pi-server-dashboard
git remote set-url origin https://github.com/harrydavies1/NodeWatch.git
git pull --ff-only
nano .env
```

Add this example line to Ubuntu Server's `.env`, adjusting the device paths if yours differ:

```ini
HDD_TEMP_DRIVES='[{"name":"NAS Drive 1","device":"/dev/sdb"},{"name":"NAS Drive 2","device":"/dev/sdc"}]'
```

**Recommended:** replace `/dev/sdb` and `/dev/sdc` with the stable `/dev/disk/by-id/ata-...` or `wwn-...` paths from Step 1, *both here and in the sudoers rule below*. The `device` field must be a whole-disk path. If a disk is replaced, update its device path and the sudoers rule; the dashboard handles an unavailable/missing disk without inventing a temperature.

## Step 3 — Grant only read-only SMART access

The Ubuntu agent runs as your ordinary Linux user (`harry` in this example). SMART usually needs elevated access. **Do not run the entire NodeWatch agent as root or add it to the disk group.** Instead permit only two exact read-only commands.

Run on Ubuntu Server:

```bash
sudo visudo -f /etc/sudoers.d/nodewatch-smartctl
```

Paste **one line** (substitute your actual agent service username and the device names from Step 2):

```sudoers
harry ALL=(root) NOPASSWD: /usr/sbin/smartctl -j -A -n standby /dev/sdb, /usr/sbin/smartctl -j -A -n standby /dev/sdc
```

Save and close the editor. Ubuntu's `visudo` validates the file. Check permissions if needed:

```bash
sudo chmod 440 /etc/sudoers.d/nodewatch-smartctl
sudo visudo -cf /etc/sudoers.d/nodewatch-smartctl
```

Test the exact command as the agent user; no password should be requested:

```bash
sudo -n /usr/sbin/smartctl -j -A -n standby /dev/sdb
```

The command should print SMART JSON. The `sudo -n` flag fails instead of prompting if sudoers isn't configured correctly. The program never uses `shell=True`, and malformed device paths aren't executed.

**Security:** Keep the agent endpoint private and token-protected; do not forward port 8766 to the internet. The sudoers entry should only permit the two *exact* read-only smartctl commands. It does not grant control of HDDs or fan speeds.

## Step 4 — Verify telemetry and restart the agent

On **Ubuntu Server**:

```bash
cd ~/pi-server-dashboard
.venv/bin/python -c 'from dotenv import load_dotenv; load_dotenv(".env"); from metrics import snapshot; print(snapshot()["hdd_temperatures"])'
sudo systemctl restart server-agent
sudo systemctl status server-agent --no-pager
```

Expected readings resemble `{"name": "NAS Drive 1", "device": "/dev/sdb", "status": "ok", "temperature_c": 33.0}` (actual values vary). If `status` is `unavailable`, check SMART permissions, disk connectivity and that your sudoers command matches the `device` string exactly. The server agent running under a different account may require a matching sudoers username.

## Step 5 — Update NodeWatch on the Raspberry Pi

On the **Pi**, retain your existing `.env` (server address, token, rotation controls) and run:

```bash
cd ~/pi-server-dashboard
git remote set-url origin https://github.com/harrydavies1/NodeWatch.git
git pull --ff-only
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Connected:",s["server"]["connected"]); print("HDDs:",(s["server"]["stats"] or {}).get("hdd_temperatures"))'
```

Restart the native Tkinter dashboard (reboot the Pi if it auto-launches at desktop login). Your configured HDDs appear on their own page. Swipe/tap left/right or press arrow keys to move between pages. `AUTO_ROTATE_PAGES=false` still disables automatic page changes and `ROTATE_SECONDS` still controls the optional rotation interval.

## Troubleshooting case: updated the Pi but still only see three pages

**Reported during the v1.1.0 setup:** After installing the latest NodeWatch code on the Raspberry Pi, the touchscreen still showed the original **three pages** instead of a fourth HDD-temperature page. We diagnosed this by checking what the **Pi receives from the Ubuntu Server agent**; the user subsequently confirmed the fourth page working.

**Key point:** Updating the **Pi display code alone does not enable the extra page**. The remote Ubuntu agent must also run the new code, have `HDD_TEMP_DRIVES` configured **on Ubuntu**, and be restarted. The Pi dashboard must then be restarted to use the updated code. The exact missing step in the reported installation was not isolated, so check each stage rather than assuming a particular cause.

### A. Inspect the Pi's live response

On the **Raspberry Pi**, run **only this valid diagnostic command**:

```bash
cd ~/pi-server-dashboard
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print("Connected:",s["server"]["connected"]); print("HDD temperatures:",(s["server"]["stats"] or {}).get("hdd_temperatures"))'
```

| Output | Meaning | Action |
| --- | --- | --- |
| `Connected: False` | Agent connection failed; server data is unavailable | Check `server-agent`, Pi `REMOTE_AGENT_URL` and matching tokens |
| `HDD temperatures: None` | No `hdd_temperatures` field in the response (or no remote stats) | Update and restart the **Ubuntu** agent, then recheck |
| `HDD temperatures: []` | New agent is responding but HDD monitoring has no configured drives | Add `HDD_TEMP_DRIVES` to the **Ubuntu** `.env`, then restart the agent |
| `HDD temperatures: [{...}, {...}]` | Two configured HDD entries are arriving | Restart the **Pi** display; check page navigation and the optional NAS page |

A non-empty drive list creates the temperature page even if a drive's `status` is `unavailable` or `invalid`: permissions affect the *readings*, not whether the page exists.

### B. Update and verify the Ubuntu agent

On **Ubuntu Server** (`harry@homeserver` in the reference setup):

```bash
cd ~/pi-server-dashboard
git pull --ff-only
nano .env
```

Ensure `HDD_TEMP_DRIVES` exists **in Ubuntu's `.env`**, not just on the Pi. Use the correct whole-disk paths, with no duplicate setting lines. Confirm the restricted sudoers rule from Step 3 above is present when you expect temperatures.

```bash
.venv/bin/python -c 'from dotenv import load_dotenv; load_dotenv(".env"); from metrics import snapshot; print(snapshot()["hdd_temperatures"])'
sudo systemctl restart server-agent
sudo systemctl status server-agent --no-pager
```

If the local agent snapshot prints two drive entries, the Ubuntu configuration is being read. An `unavailable` state means troubleshoot SMART permissions or drive connectivity; it should **not** remove the page.

### C. Refresh the Raspberry Pi code and screen

On the **Raspberry Pi**:

```bash
cd ~/pi-server-dashboard
git pull --ff-only
.venv/bin/python -c 'from dashboard import collect_state; s=collect_state(); print((s["server"]["stats"] or {}).get("hdd_temperatures"))'
```

Restart the Tkinter application, or reboot the Pi if NodeWatch is launched automatically at desktop login:

```bash
sudo reboot
```

With both `NAS_STORAGE_PATHS` **and** `HDD_TEMP_DRIVES` configured on Ubuntu, the four pages are **System Overview → Network & Services → NAS Storage → HDD Temperatures**. Without `NAS_STORAGE_PATHS`, HDD Temperatures is the **third** page. You can tap the left/right sides of the screen or use arrow keys to navigate. `AUTO_ROTATE_PAGES=false` stops automatic cycling, but does **not** hide the page.

---

## Troubleshooting and removal

- **Temperature page missing:** `HDD_TEMP_DRIVES` must be set **on Ubuntu**, both checkouts must be updated, and both processes restarted. Confirm the agent sends a non-empty `hdd_temperatures` list.
- **CONFIG warning:** fix malformed JSON or unsupported drive path.
- **UNAVAILABLE:** run the `sudo -n /usr/sbin/smartctl ...` test as the agent account. A disconnected/replaced disk or unsupported SMART device also returns this state.
- **DRIVE SLEEPING:** the drive was not woken for temperature collection; its reading remains unavailable until it spins up for normal I/O.
- **No NAS Storage page:** configure `NAS_STORAGE_PATHS` separately on Ubuntu if you want the HDD temperature page to be page 4. See [NAS Storage](NAS_STORAGE.md).
- **Disabling:** remove `HDD_TEMP_DRIVES` from Ubuntu's `.env` and restart `server-agent`. If no longer needed, remove `/etc/sudoers.d/nodewatch-smartctl` using `sudo rm`.

**Important:** A SMART health result of `PASSED` does not guarantee reliability. If a drive is running hot or has reallocated sectors, prioritise cooling, replacement and independent backups. The temperature page is monitoring only.
