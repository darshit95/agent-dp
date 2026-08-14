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
# Labels shipped by earlier releases. install()/uninstall() boot them out and
# delete them, otherwise an old agent keeps firing on its own schedule alongside
# the current one — invisible to `scheduler-status`, which only checks LABEL.
LEGACY_LABELS = (
    "com.cardbudget.daily-sync",
    "com.cardbudget.monthly-sync",
    "com.pockettrack.bidaily-sync",
    "com.pockettrack.monthly-sync",
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
    hours: tuple[int, ...] = ()


DEFAULT_SYNC_HOURS: tuple[int, ...] = (8, 20)


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


def scheduled_hours(path: Path | None = None) -> tuple[int, ...]:
    """Hours the installed agent is set to run, read back from the plist."""
    target = path or launch_agent_path()
    try:
        with target.open("rb") as fh:
            payload = plistlib.load(fh)
    except (OSError, ValueError):
        return ()
    interval = payload.get("StartCalendarInterval")
    entries = interval if isinstance(interval, list) else [interval]
    hours = [int(e["Hour"]) for e in entries if isinstance(e, dict) and "Hour" in e]
    return tuple(sorted(set(hours)))


def status() -> SchedulerStatus:
    path = launch_agent_path()
    return SchedulerStatus(
        installed=path.exists(),
        loaded=_launchctl_loaded(),
        plist_path=path,
        hours=scheduled_hours(path),
    )


def is_installed() -> bool:
    return launch_agent_path().exists()


def _program_arguments() -> list[str]:
    # sys.executable points at the active venv Python at install time, which keeps
    # the background task independent from shell PATH configuration.
    return [sys.executable, "-m", "cardbudget", "daily-sync"]


def _import_root() -> str:
    """Directory that must be importable for `python -m cardbudget` to work.

    Pinned into the agent's environment because a venv's .pth file can silently
    stop being read — for example when the checkout lives in a cloud-synced
    folder that flags files as hidden — which leaves the scheduled sync failing
    with ModuleNotFoundError where nobody sees it.
    """
    import cardbudget

    return str(Path(cardbudget.__file__).resolve().parents[1])


def normalize_hours(hours) -> tuple[int, ...]:
    cleaned = sorted({int(hour) for hour in hours})
    if not cleaned:
        raise ValueError("At least one sync hour is required.")
    for hour in cleaned:
        if not 0 <= hour <= 23:
            raise ValueError("Hours must be between 0 and 23.")
    return tuple(cleaned)


def build_plist(settings: Settings, *, hours=DEFAULT_SYNC_HOURS) -> dict:
    if sys.platform != "darwin":
        raise RuntimeError("The built-in scheduler installer currently supports macOS only.")
    resolved = normalize_hours(hours)

    logs_dir = settings.data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(logs_dir, 0o700)

    environment = {
        "POCKETTRACK_HOST": "127.0.0.1",
        "POCKETTRACK_DATA_DIR": str(settings.data_dir),
        "POCKETTRACK_PLAID_ENVIRONMENT": settings.plaid_environment,
        "POCKETTRACK_OLLAMA_MODEL": settings.ollama_model,
        "PYTHONPATH": _import_root(),
    }
    return {
        "Label": LABEL,
        "ProgramArguments": _program_arguments(),
        "StartCalendarInterval": [{"Hour": hour, "Minute": 0} for hour in resolved],
        # A laptop that is asleep at a scheduled hour gets one catch-up run from
        # launchd on wake; RunAtLoad additionally syncs after a reboot or login.
        "RunAtLoad": True,
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


def _read_plist(path: Path) -> dict | None:
    try:
        with path.open("rb") as fh:
            return plistlib.load(fh)
    except (OSError, ValueError):
        return None


def install(settings: Settings, *, hours=DEFAULT_SYNC_HOURS) -> SchedulerInstallResult:
    plist_path = launch_agent_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_plist(settings, hours=hours)

    # RunAtLoad means every reload fires an immediate sync + local-LLM
    # categorization pass. install() used to unconditionally bootout+bootstrap
    # on every call, so e.g. start.sh re-running it on every ordinary restart
    # triggered a full background sync burst each time, whether or not
    # anything had actually changed. Skip the reload when the agent is already
    # installed, loaded, and configured identically (same hours, env,
    # program path, etc. - anything that would change the plist).
    if payload == _read_plist(plist_path) and _launchctl_loaded():
        return SchedulerInstallResult(
            plist_path=plist_path,
            loaded=True,
            detail="already up to date; left running (skipped reload, no re-sync triggered)",
        )

    for label, legacy in zip(LEGACY_LABELS, _legacy_paths()):
        _bootout(legacy, label)
        legacy.unlink(missing_ok=True)

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
