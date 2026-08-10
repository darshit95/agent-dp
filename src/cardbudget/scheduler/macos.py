from __future__ import annotations

import os
import plistlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from cardbudget.config import Settings

LABEL = "com.pockettrack.daily-sync"
PLIST_NAME = f"{LABEL}.plist"
LEGACY_LABELS = (
    "com.cardbudget.daily-sync",
    "com.cardbudget.monthly-sync",
)


@dataclass(frozen=True)
class SchedulerInstallResult:
    plist_path: Path
    loaded: bool
    detail: str


@dataclass(frozen=True)
class SchedulerStatus:
    installed: bool
    loaded: bool
    plist_path: Path


def launch_agents_dir() -> Path:
    return Path.home() / "Library" / "LaunchAgents"


def launch_agent_path() -> Path:
    return launch_agents_dir() / PLIST_NAME


def _legacy_paths() -> tuple[Path, ...]:
    return tuple(launch_agents_dir() / f"{label}.plist" for label in LEGACY_LABELS)


def _launchctl_loaded(label: str = LABEL) -> bool:
    if sys.platform != "darwin":
        return False
    domain = f"gui/{os.getuid()}/{label}"
    result = subprocess.run(
        ["launchctl", "print", domain],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def status() -> SchedulerStatus:
    path = launch_agent_path()
    return SchedulerStatus(installed=path.exists(), loaded=_launchctl_loaded(), plist_path=path)


def is_installed() -> bool:
    return launch_agent_path().exists()


def _program_arguments() -> list[str]:
    # sys.executable points at the active venv Python at install time, which keeps
    # the background task independent from shell PATH configuration.
    return [sys.executable, "-m", "cardbudget", "daily-sync"]


def build_plist(settings: Settings, *, hour: int = 8) -> dict:
    if sys.platform != "darwin":
        raise RuntimeError("The built-in scheduler installer currently supports macOS only.")
    if not 0 <= hour <= 23:
        raise ValueError("Hour must be between 0 and 23.")

    logs_dir = settings.data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(logs_dir, 0o700)

    environment = {
        "POCKETTRACK_HOST": "127.0.0.1",
        "POCKETTRACK_DATA_DIR": str(settings.data_dir),
        "POCKETTRACK_PLAID_ENVIRONMENT": settings.plaid_environment,
        "POCKETTRACK_OLLAMA_MODEL": settings.ollama_model,
    }
    return {
        "Label": LABEL,
        "ProgramArguments": _program_arguments(),
        "StartCalendarInterval": {"Hour": hour, "Minute": 0},
        "EnvironmentVariables": environment,
        "StandardOutPath": str(logs_dir / "daily-sync.log"),
        "StandardErrorPath": str(logs_dir / "daily-sync-error.log"),
        "ProcessType": "Background",
    }


def _bootout(path: Path, label: str | None = None) -> None:
    if sys.platform != "darwin":
        return
    domain = f"gui/{os.getuid()}"
    if path.exists():
        subprocess.run(
            ["launchctl", "bootout", domain, str(path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif label:
        subprocess.run(
            ["launchctl", "bootout", f"{domain}/{label}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def install(settings: Settings, *, hour: int = 8) -> SchedulerInstallResult:
    plist_path = launch_agent_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    for label, legacy in zip(LEGACY_LABELS, _legacy_paths()):
        _bootout(legacy, label)
        legacy.unlink(missing_ok=True)

    payload = build_plist(settings, hour=hour)
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
    return SchedulerInstallResult(plist_path=plist_path, loaded=loaded, detail=detail)


def uninstall() -> bool:
    removed = False
    all_paths = ((LABEL, launch_agent_path()),) + tuple(zip(LEGACY_LABELS, _legacy_paths()))
    for label, path in all_paths:
        if path.exists() or _launchctl_loaded(label):
            _bootout(path, label)
            path.unlink(missing_ok=True)
            removed = True
    return removed
