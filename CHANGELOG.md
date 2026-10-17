# Changelog

Notable changes to NodeWatch. Versions follow GitHub release tags.

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
