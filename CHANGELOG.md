# Changelog

Notable changes to NodeWatch. Versions follow GitHub release tags.

## [Unreleased]

### Added

- **Optional Windows XP-inspired Luna theme** for the existing NodeWatch Tkinter dashboard, with original vector-drawn bright blue window chrome, taskbar and clock, raised panels and segmented progress bars.
- `DASHBOARD_THEME=xp` selects the retro look on the **Raspberry Pi or desktop displaying NodeWatch**; the original dark theme remains the default (`DASHBOARD_THEME=dark`). The Ubuntu telemetry agent and data protocol are unchanged.
- Live GUI preview override `--theme xp` and simulator preview `python3 python-display/simulate.py --theme xp`, both supporting 2–4 pages.
- Removed the initial green Start button and Start pop-up menu by request; the XP taskbar now uses the freed width to show the current page. Touchscreen taps, keyboard navigation and optional auto-rotation still work.
- Adjusted XP fonts approximately 10% smaller across the interface, reduced crowded page-one stat values, aligned labels above the progress bars, and removed the unused "Read-only disk temperatures" footer from the HDD page.
- Added real-screenshot troubleshooting to [themes documentation](docs/THEMES.md), covering cramped numbers, unwanted footer text and updating/restarting the Mac/Pi display to apply visual changes.
- Added theme selection, usage documentation and headless regression tests for page rendering, uncluttered overview metrics and removed UI elements.

No new stable release has been tagged for this unreleased feature.

## [v1.1.1](https://github.com/harrydavies1/NodeWatch/releases/tag/v1.1.1) — 2026-10-19

**Small patch release:** adds an optional **cross-platform Python/Tkinter simulator** without changing the existing v1.1.0 agent protocol, NAS storage, HDD SMART monitoring or Pi display behaviour.

- Added `python-display/simulate.py` to preview NodeWatch's actual four-page GUI with animated, clearly labelled **fake data** on **macOS, Windows and desktop Linux**.
- Removed the production dashboard's hard import dependency on `dashboard.collect_state()` for GUI-only simulation by allowing a custom telemetry collector. Normal Pi/Server Mode retains the same real collector by default.
- The simulator requires only **Python 3 and Tkinter**, not `psutil`, `python-dotenv`, credentials, network access or a server. It uses shared dashboard files from the NodeWatch repository.
- Supports a default **480×320 window**, optional fullscreen, 2/3/4-page previews, Pi Mode, manual navigation, animated refreshes and optional automatic page rotation through CLI flags.
- Added [Mac/Windows/Linux setup and troubleshooting](docs/SIMULATOR.md), README guidance and regression tests for simulated state, page selection, options and zero-third-party-dependency help.
- This does **not** replace or alter live monitoring, disk configuration, SMART data, Tailscale, Samba or Minecraft.

**Full changes:** [v1.1.0...v1.1.1](https://github.com/harrydavies1/NodeWatch/compare/v1.1.0...v1.1.1)

## [v1.1.0](https://github.com/harrydavies1/NodeWatch/releases/tag/v1.1.0) — 2026-10-18

**HDD temperatures and deployment troubleshooting**, following [v1.0.0](https://github.com/harrydavies1/NodeWatch/releases/tag/v1.0.0).

### Added

- **Opt-in SMART HDD temperature page:** Server Mode shows two configurable physical HDD temperatures on a dedicated 480×320 Tkinter page. It is **page 4** when the existing NAS storage page is enabled, or **page 3** without NAS storage monitoring.
- **Read-only Ubuntu SMART collector:** `HDD_TEMP_DRIVES` configures up to two whole-disk devices on Ubuntu Server. Temperatures are read via `smartctl`, cached for 60 seconds, and reported through the existing authenticated server agent.
- **Clear hardware states:** sleeping or unavailable HDDs, bad configuration, and advisory temperature statuses are visible rather than shown as healthy readings. Normal/warm/hot thresholds (below 45°C, 45–49.9°C, 50°C+) are **general guidance, not drive specifications**.
- **Least-privilege SMART setup guide:** restricted read-only `sudoers` example, no root-owned agent, and stable `/dev/disk/by-id/` paths for future disk replacement.

### Troubleshooting documented from the real setup

- **Symptom:** Raspberry Pi was updated, but NodeWatch still displayed **only three pages**.
- **Diagnosis:** the Pi creates the temperature page only when the **Ubuntu Server agent** supplies a non-empty `hdd_temperatures` list; updating Pi code alone does not enable it.
- **Fix/checklist:** update both checkouts; configure `HDD_TEMP_DRIVES` on **Ubuntu Server**; verify `snapshot()["hdd_temperatures"]` locally; restart `server-agent`; check the Pi's `collect_state()` output; restart the Pi's Tkinter display. `None` indicates no temperature field, `[]` indicates an unconfigured list, and a populated list means the screen should be available.
- **Outcome:** the user confirmed the fourth page works after troubleshooting. The single missing step was not isolated, so the guide covers the full path rather than claiming an unverified root cause.
- Added the diagnostic command and decision table to [HDD temperature setup](docs/HDD_TEMPERATURES.md#troubleshooting-case-updated-the-pi-but-still-only-see-three-pages) and cross-linked it from the README.

### Compatibility and upgrade

- Pi Mode, authenticated Server Mode, existing NAS page, touchscreen/keyboard navigation, and `AUTO_ROTATE_PAGES` settings remain compatible.
- `HDD_TEMP_DRIVES` is **optional**. Install `smartmontools` and permit the precise read-only `smartctl` commands only if enabling the feature.
- No NAS mounts, Samba shares, Minecraft services, partitions, or user data are changed.
- Unit and integration test coverage expanded for SMART parsing, caching, failures and optional page counts.

**Full changes:** [v1.0.0...v1.1.0](https://github.com/harrydavies1/NodeWatch/compare/v1.0.0...v1.1.0)

## [v1.0.0](https://github.com/harrydavies1/NodeWatch/releases/tag/v1.0.0) — 2026-10-17

**First stable release**, following the [v0.1.0 beta](https://github.com/harrydavies1/NodeWatch/releases/tag/v0.1.0).

### Added since v0.1.0 beta

- **Ubuntu Server agent autostart:** optional managed systemd service, with `enable`, `disable`, `status`, and `logs` commands. Starts on boot without a desktop login, restarts after failures, and validates the agent's configuration before installation.
- **Samba/NAS filesystem monitoring:** opt-in monitoring of the filesystem backing a Samba share, separate from the Ubuntu system disk. Missing paths and shares on the system filesystem are labelled rather than silently displayed as a healthy separate drive.
- **Independent dual-drive NAS page:** optional third 480×320 Tkinter page showing two configured NAS volumes separately, with used/free/total space, percentage used and mount-status warnings. Configure `NAS_STORAGE_PATHS` **on Ubuntu Server**; the older single-volume `NAS_STORAGE_PATH` still works.
- **Optional automatic page switching:** `AUTO_ROTATE_PAGES=false` **on the Raspberry Pi** turns off timed page changes while preserving touchscreen/keyboard navigation and live data updates. The default is `true` for backwards compatibility; `ROTATE_SECONDS` controls the interval when enabled.

### Improved since v0.1.0 beta

- Verified the native Pi display and authenticated Ubuntu Server connection on a Raspberry Pi 3B / OSOYOO SPI display and Dell OptiPlex Ubuntu Server setup.
- Expanded setup guides for Server Mode, local/remote configuration separation, LAN access, agent startup, NAS mounts, and remote connection troubleshooting.
- Added agent-to-Pi HTTP integration coverage, systemd helper tests, documentation checks, dual NAS monitoring tests, and page-rotation setting tests. **35 automated tests passed** in GitHub Actions for the pre-release stable code.
- Clarified monitoring boundaries: TCP probes are not application-health checks, network counters are cumulative, and NAS usage is filesystem capacity (not Samba traffic or per-share directory size).

### Compatibility / upgrading

- No mandatory configuration migration. Existing Pi Mode and authenticated Server Mode configurations continue to work.
- New features are **optional** and off by default except auto-rotation, which stays on by default to preserve the beta behavior.
- Update your existing checkout(s) with `git pull`; keep your local `.env` and `.venv`. Restart the Ubuntu `server-agent` service after updating its code and restart the Pi's Tkinter dashboard after updating its code.
- NodeWatch is provided as **Python source** for use on supported Linux/Raspberry Pi setups, not as a Windows installer or standalone compiled application.

See the [v1.0.0 release notes](releases/v1.0.0.md) for upgrade steps and configuration examples.

## [v0.1.0](https://github.com/harrydavies1/NodeWatch/releases/tag/v0.1.0) — 2026-10-13 (beta)

- Initial native Python/Tkinter Raspberry Pi monitoring dashboard; no Chromium/browser required.
- Pi Mode with live local CPU, RAM, root disk, available temperature, uptime and network metrics.
- Optional authenticated Server Mode using a read-only Python HTTP agent on Ubuntu/Linux.
- Two-screen 480×320 interface with touchscreen/keyboard navigation and automatic page rotation.
- Optional graphical desktop autostart on the Pi, plus project setup guides.

**Full changes:** [v0.1.0...v1.0.0](https://github.com/harrydavies1/NodeWatch/compare/v0.1.0...v1.0.0).
