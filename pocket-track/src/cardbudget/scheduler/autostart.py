"""launchd agent that keeps the PocketTrack web app running.

This is a LaunchAgent rather than a LaunchDaemon on purpose: PocketTrack reads
its Plaid credentials and database key from the *user's* login Keychain, which a
root daemon cannot unlock. The trade-off is that the app starts at login rather
than at boot.

KeepAlive means a crashed server comes back on its own — and that stopping it
requires unloading the agent, not killing the process. ``stop.sh`` does exactly
that; see ``uninstall()``.
"""

from __future__ import annotations

import os
import plistlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from cardbudget.config import Settings
from cardbudget.scheduler.macos import (
    _bootout,
    _import_root,
    _launchctl_loaded,
    launch_agents_dir,
)

LABEL = "com.pockettrack.app"
PLIST_NAME = f"{LABEL}.plist"


@dataclass(frozen=True)
class AutostartStatus:
    installed: bool
    loaded: bool
    plist_path: Path


def launch_agent_path() -> Path:
    return launch_agents_dir() / PLIST_NAME


def status() -> AutostartStatus:
    path = launch_agent_path()
    return AutostartStatus(installed=path.exists(), loaded=_launchctl_loaded(LABEL), plist_path=path)


def build_plist(settings: Settings) -> dict:
    if sys.platform != "darwin":
        raise RuntimeError("The built-in autostart installer currently supports macOS only.")

    logs_dir = settings.data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(logs_dir, 0o700)

    return {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, "-m", "cardbudget", "serve"],
        "RunAtLoad": True,
        "KeepAlive": True,
        "EnvironmentVariables": {
            "POCKETTRACK_HOST": "127.0.0.1",
            "POCKETTRACK_DATA_DIR": str(settings.data_dir),
            "POCKETTRACK_PLAID_ENVIRONMENT": settings.plaid_environment,
            "POCKETTRACK_OLLAMA_MODEL": settings.ollama_model,
            "PYTHONPATH": _import_root(),
        },
        "StandardOutPath": str(logs_dir / "app.log"),
        "StandardErrorPath": str(logs_dir / "app-error.log"),
    }


def install(settings: Settings) -> tuple[Path, bool, str]:
    """Write and load the agent. Returns (path, loaded, detail)."""
    plist_path = launch_agent_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_plist(settings)
    tmp_path = plist_path.with_suffix(".plist.tmp")
    with tmp_path.open("wb") as fh:
        plistlib.dump(payload, fh, sort_keys=False)
    if os.name == "posix":
        os.chmod(tmp_path, 0o600)
    tmp_path.replace(plist_path)

    domain = f"gui/{os.getuid()}"
    _bootout(plist_path, LABEL)
    result = subprocess.run(
        ["launchctl", "bootstrap", domain, str(plist_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    loaded = result.returncode == 0
    detail = "loaded with launchd" if loaded else (result.stderr.strip() or "plist written; launchd load failed")
    return plist_path, loaded, detail


def uninstall() -> bool:
    """Unload and remove the agent.

    KeepAlive restarts the server if the process is merely killed, so this is the
    only reliable way to stop it.
    """
    path = launch_agent_path()
    existed = path.exists() or _launchctl_loaded(LABEL)
    if existed:
        _bootout(path, LABEL)
        path.unlink(missing_ok=True)
    return existed
