"""One-shot health check across every component ./start.sh installs.

`autostart-status` and `scheduler-status` each answer one narrow question, which
left no single way to ask "is PocketTrack actually working right now". Debugging
a broken install meant reading start.sh to recall what it had set up. This
collects the whole picture - agent, port, HTTPS proxy, hostname, backend, Ollama
and the sync schedule - into one pass/fail report.

Checks are read-only and never raise: a check that cannot run reports FAIL with
the reason, because a diagnostic that crashes on a broken system is useless
exactly when it is needed.
"""

from __future__ import annotations

import plistlib
import socket
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from cardbudget.config import Settings
from cardbudget.scheduler import autostart as app_autostart
from cardbudget.scheduler import macos as macos_scheduler

HOSTNAME_LOCAL = "my-pocket-track"
CADDY_LABEL = "com.pockettrack.caddy"
CADDY_PLIST = Path("/Library/LaunchDaemons") / f"{CADDY_LABEL}.plist"
APP_PORT = 8000
OLLAMA_URL = "http://127.0.0.1:11434/api/tags"


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    # Advisory checks report status without failing the overall result: an
    # optional component being down degrades PocketTrack, it does not break it.
    advisory: bool = False


def _port_listening(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        return sock.connect_ex((host, port)) == 0


def _http_ok(url: str, timeout: float = 3.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _check_app_agent() -> Check:
    state = app_autostart.status()
    if not state.installed:
        return Check("App autostart agent", False, f"not installed ({state.plist_path})")
    if not state.loaded:
        return Check("App autostart agent", False, "plist present but not loaded into launchd")

    # A plist pointing at a deleted or moved checkout crash-loops silently, so
    # compare the recorded interpreter against what is actually on disk.
    try:
        with state.plist_path.open("rb") as fh:
            program = plistlib.load(fh).get("ProgramArguments", [None])[0]
    except (OSError, ValueError, IndexError):
        program = None
    if program and not Path(program).exists():
        return Check("App autostart agent", False, f"points at a missing interpreter: {program}")
    return Check("App autostart agent", True, f"loaded ({program or state.plist_path})")


def _check_backend() -> Check:
    if not _port_listening(APP_PORT):
        return Check("Backend on :8000", False, "nothing listening")
    if not _http_ok(f"http://127.0.0.1:{APP_PORT}/"):
        return Check("Backend on :8000", False, "listening but not answering HTTP")
    return Check("Backend on :8000", True, "responding")


def _check_https_proxy() -> Check:
    if not CADDY_PLIST.exists():
        return Check("HTTPS proxy (Caddy)", False, f"daemon not installed ({CADDY_PLIST})")
    if not _port_listening(443):
        return Check("HTTPS proxy (Caddy)", False, "installed but not listening on :443")
    return Check("HTTPS proxy (Caddy)", True, "listening on :443")


def _check_hostname() -> Check:
    try:
        hosts = Path("/etc/hosts").read_text(encoding="utf-8")
    except OSError as exc:
        return Check("Local hostname", False, f"cannot read /etc/hosts: {exc}")
    for line in hosts.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if HOSTNAME_LOCAL in line.split():
            return Check("Local hostname", True, f"{HOSTNAME_LOCAL} mapped to loopback")
    return Check("Local hostname", False, f"{HOSTNAME_LOCAL} missing from /etc/hosts")


def _check_site() -> Check:
    if not _http_ok(f"https://{HOSTNAME_LOCAL}/"):
        return Check("Site", False, f"https://{HOSTNAME_LOCAL} not reachable")
    return Check("Site", True, f"https://{HOSTNAME_LOCAL} reachable")


def _check_ollama(settings: Settings) -> Check:
    if not _http_ok(OLLAMA_URL, timeout=2.0):
        return Check(
            "Local AI (Ollama)",
            False,
            "not reachable; categorization falls back to rules/manual",
            advisory=True,
        )
    return Check("Local AI (Ollama)", True, f"reachable (model {settings.ollama_model})", advisory=True)


def _check_scheduler() -> Check:
    state = macos_scheduler.status()
    if not state.installed:
        return Check("Sync schedule", False, "not installed", advisory=True)
    if not state.loaded:
        return Check("Sync schedule", False, "installed but not loaded", advisory=True)
    hours = ", ".join(f"{h:02d}:00" for h in state.hours) or "unknown"
    return Check("Sync schedule", True, f"daily at {hours}", advisory=True)


def collect(settings: Settings) -> list[Check]:
    if sys.platform != "darwin":
        return [Check("Platform", False, "status checks currently support macOS only")]
    return [
        _check_app_agent(),
        _check_backend(),
        _check_https_proxy(),
        _check_hostname(),
        _check_site(),
        _check_ollama(settings),
        _check_scheduler(),
    ]


def report(settings: Settings) -> int:
    """Print the report. Returns a process exit code (0 healthy, 1 degraded)."""
    checks = collect(settings)
    width = max(len(check.name) for check in checks)
    failed_required = False

    for check in checks:
        if check.ok:
            mark = "PASS"
        elif check.advisory:
            mark = "WARN"
        else:
            mark = "FAIL"
            failed_required = True
        print(f"{mark:<5} {check.name:<{width}}  {check.detail}")

    print()
    if failed_required:
        print("PocketTrack is not fully running. Re-run ./start.sh to repair it.")
    else:
        print(f"PocketTrack is running. Open: https://{HOSTNAME_LOCAL}")
    return 1 if failed_required else 0
