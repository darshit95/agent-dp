#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$ROOT/.runtime"
APP_PID_FILE="$RUNTIME/pockettrack.pid"
OLLAMA_PID_FILE="$RUNTIME/ollama.pid"
APP_LOG="$RUNTIME/pockettrack.log"
OLLAMA_LOG="$RUNTIME/ollama.log"
APP_LOG_DIR="$HOME/.pockettrack/logs"
HOSTNAME_LOCAL="my-pocket-track"
CADDY_ADMIN="127.0.0.1:2020"
CADDY_LABEL="com.pockettrack.caddy"
CADDY_PLIST="/Library/LaunchDaemons/${CADDY_LABEL}.plist"
CADDY_CONFIG_DIR="/Library/Application Support/PocketTrack"
CADDY_CONFIG="${CADDY_CONFIG_DIR}/Caddyfile"
MODEL="${POCKETTRACK_OLLAMA_MODEL:-qwen3.5:4b}"

mkdir -p "$RUNTIME"
chmod 700 "$RUNTIME"

# Make the package importable no matter what state the venv's .pth file is in.
# A checkout inside a cloud-synced folder (iCloud Desktop, Dropbox, ...) can get
# its .pth marked hidden, which Python then skips - the venv looks installed but
# "import cardbudget" fails. Every command below, and the server we launch,
# inherits this.
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

say() { printf '\n\033[1;34mPocketTrack\033[0m  %s\n' "$*"; }
fail() { printf '\n\033[1;31mERROR\033[0m  %s\n' "$*" >&2; exit 1; }

if [[ "$(uname -s)" != "Darwin" ]]; then
  fail "The one-command HTTPS launcher currently supports macOS. See README.md for manual launch instructions."
fi

say "Preparing system dependencies"
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required for the local HTTPS proxy. Installing Homebrew..."
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
  if [[ -x /usr/local/bin/brew ]]; then eval "$(/usr/local/bin/brew shellenv)"; fi
fi
command -v brew >/dev/null 2>&1 || fail "Homebrew installation did not complete."

brew list python@3.12 >/dev/null 2>&1 || brew install python@3.12
brew list caddy >/dev/null 2>&1 || brew install caddy
PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
CADDY="$(command -v caddy)"

if ! command -v ollama >/dev/null 2>&1; then
  say "Installing Ollama"
  curl -fsSL https://ollama.com/install.sh | sh
fi
command -v ollama >/dev/null 2>&1 || fail "Ollama installation did not complete."

say "Preparing Python environment"

VENV="$ROOT/.venv"
VENV_PYTHON="$VENV/bin/python"
VENV_POCKETTRACK="$VENV/bin/pockettrack"


VENV_FRESHLY_BUILT=0

create_venv() {
    say "Creating fresh Python virtual environment"
    VENV_FRESHLY_BUILT=1

    rm -rf "$VENV"

    "$PYTHON" -m venv "$VENV"

    "$VENV/bin/python" -m pip install \
        --upgrade pip setuptools wheel

    "$VENV/bin/python" -m pip install \
        -e "${ROOT}[dev]"
}


install_project() {
    "$VENV_PYTHON" -m pip install \
        --upgrade pip setuptools wheel

    # IMPORTANT:
    # Always install PocketTrack itself before tests or CLI commands.
    "$VENV_PYTHON" -m pip install \
        -e "${ROOT}[dev]"
}


unhide_venv_metadata() {
    # Undo the "hidden" flag a cloud-sync agent may have put on the venv's .pth
    # files, so PocketTrack also works when run outside this script.
    [[ -d "$VENV" ]] || return 0
    chflags nohidden "$VENV"/lib/python*/site-packages/*.pth 2>/dev/null || true
}


venv_is_healthy() {
    [[ -x "$VENV_PYTHON" ]] || return 1
    [[ -x "$VENV_POCKETTRACK" ]] || return 1

    "$VENV_PYTHON" - <<'PYHEALTH' >/dev/null 2>&1
import cardbudget
import fastapi
import uvicorn
from cardbudget.cli import main
PYHEALTH
}


# ---------------------------------------------------------------
# Create venv if it does not exist.
# ---------------------------------------------------------------

if [[ ! -x "$VENV_PYTHON" ]]; then
    create_venv
else
    say "Existing virtual environment found"

    # Reinstall current repository into the existing venv.
    install_project
fi

unhide_venv_metadata


# ---------------------------------------------------------------
# Self-heal a corrupt/stale venv.
# ---------------------------------------------------------------

if ! venv_is_healthy; then
    say "Existing virtual environment is unhealthy; rebuilding automatically"

    create_venv
    unhide_venv_metadata
fi


# ---------------------------------------------------------------
# Hard validation.
# ---------------------------------------------------------------

if ! venv_is_healthy; then
    fail "PocketTrack Python environment could not be initialized."
fi


say "Python environment ready"

"$VENV_PYTHON" - <<'PYVERIFY'
import sys
import cardbudget
from cardbudget.cli import main

print(f"Python:      {sys.executable}")
print(f"PocketTrack: {cardbudget.__file__}")
print("Package:     OK")
print("CLI:         OK")
PYVERIFY

say "Starting local AI"
if ! curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  nohup ollama serve >"$OLLAMA_LOG" 2>&1 &
  echo $! > "$OLLAMA_PID_FILE"
  for _ in {1..20}; do
    curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
    sleep 1
  done
fi
if curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  ollama pull "$MODEL"
else
  echo "Warning: Ollama is not reachable; PocketTrack will still run and use manual/heuristic categorization."
fi

say "Verifying PocketTrack installation"

"$VENV_PYTHON" - <<'PYAPPVERIFY'
import cardbudget
from cardbudget.app import create_app
from cardbudget.cli import main

print("PocketTrack application import: OK")
PYAPPVERIFY

if [[ "$VENV_FRESHLY_BUILT" == "1" ]]; then
  say "Running tests"
  "$VENV_PYTHON" -m pytest -q "$ROOT/tests"
else
  say "Skipping test suite (existing, healthy virtual environment)"
  echo "Run '.venv/bin/python -m pytest -q tests' manually after pulling code changes."
fi

say "Running security diagnostics"
"$VENV_POCKETTRACK" doctor

say "Preparing private local hostname"
if ! grep -Eq "(^|[[:space:]])${HOSTNAME_LOCAL}([[:space:]]|$)" /etc/hosts; then
  echo "127.0.0.1 ${HOSTNAME_LOCAL}" | sudo tee -a /etc/hosts >/dev/null
fi
sudo dscacheutil -flushcache >/dev/null 2>&1 || true
sudo killall -HUP mDNSResponder >/dev/null 2>&1 || true

say "Starting PocketTrack application"

# ----------------------------------------------------------------
# Robust port-8000 handling
#
# PID files and macOS process names are not always reliable because
# a running PocketTrack/Uvicorn process may appear simply as Python.
#
# If port 8000 is already occupied:
#   1. Probe the HTTP service.
#   2. If it identifies itself as PocketTrack, stop the stale instance.
#   3. If it is not PocketTrack, fail safely and do not kill it.
# ----------------------------------------------------------------

get_port_8000_pid() {
  lsof -tiTCP:8000 -sTCP:LISTEN 2>/dev/null | head -1 || true
}

port_8000_is_pockettrack() {
  local response

  response="$(
    curl -fsS \
      --max-time 3 \
      -H "Host: my-pocket-track" \
      http://127.0.0.1:8000/ \
      2>/dev/null || true
  )"

  [[ -n "$response" ]] || return 1

  # PocketTrack pages consistently expose the product name.
  printf '%s' "$response" | grep -qi "PocketTrack"
}

stop_existing_pockettrack() {
  local pid="$1"

  [[ -n "$pid" ]] || return 0

  echo "Existing PocketTrack instance found on port 8000 (PID $pid)."
  echo "Stopping stale instance so the current repository version can start..."

  kill "$pid" 2>/dev/null || true

  for _ in {1..20}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done

  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true
  fi

  for _ in {1..20}; do
    if [[ -z "$(get_port_8000_pid)" ]]; then
      break
    fi
    sleep 0.25
  done

  if [[ -n "$(get_port_8000_pid)" ]]; then
    fail "PocketTrack could not release port 8000."
  fi

  rm -f "$APP_PID_FILE"

  echo "Previous PocketTrack instance stopped."
}

# Clean stale PID metadata first.
if [[ -f "$APP_PID_FILE" ]]; then
  RECORDED_PID="$(cat "$APP_PID_FILE" 2>/dev/null || true)"

  if [[ -z "$RECORDED_PID" ]] || ! kill -0 "$RECORDED_PID" 2>/dev/null; then
    echo "Removing stale PocketTrack PID file."
    rm -f "$APP_PID_FILE"
  fi
fi

# Check the actual TCP listener instead of trusting process metadata.
PORT_PID="$(get_port_8000_pid)"

if [[ -n "$PORT_PID" ]]; then

  if port_8000_is_pockettrack; then
    stop_existing_pockettrack "$PORT_PID"
  else
    echo >&2
    echo "ERROR: Port 8000 is already being used by another application:" >&2
    ps -ww -p "$PORT_PID" -o pid=,command= >&2 || true
    echo >&2
    echo "PocketTrack verified that the service is not PocketTrack." >&2
    echo "It will not terminate an unrelated application automatically." >&2
    exit 1
  fi
fi

# Port must now be free.
if [[ -n "$(get_port_8000_pid)" ]]; then
  fail "Port 8000 is still occupied."
fi

rm -f "$APP_PID_FILE"

export POCKETTRACK_PLAID_ENVIRONMENT="${POCKETTRACK_PLAID_ENVIRONMENT:-production}"
export POCKETTRACK_OLLAMA_MODEL="$MODEL"

# The app runs as a LaunchAgent, not a bare nohup process, so it comes back after
# a restart and restarts itself if it crashes. It must be a user agent (not a
# root daemon) because its secrets live in the user's login Keychain.
# KeepAlive means killing the process is not enough to stop it - ./stop.sh
# unloads the agent, which is the supported way to shut PocketTrack down.
if "$VENV_POCKETTRACK" install-autostart; then
  echo "PocketTrack will start automatically when you log in."
else
  fail "PocketTrack autostart agent could not be loaded. See $APP_LOG"
fi

for _ in {1..30}; do
  if curl -fsS --max-time 2 http://127.0.0.1:8000/ >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS --max-time 2 http://127.0.0.1:8000/ >/dev/null 2>&1 || {
  tail -80 "$APP_LOG_DIR/app-error.log" >&2 2>/dev/null || true
  fail "PocketTrack backend did not become ready."
}

say "Starting local HTTPS"
# Caddy needs root to bind 443, so it is a system LaunchDaemon rather than a user
# agent. That also means HTTPS is up from boot, before anyone logs in.
sudo "$CADDY" stop --address "$CADDY_ADMIN" >/dev/null 2>&1 || true
sudo launchctl bootout system/"$CADDY_LABEL" >/dev/null 2>&1 || true

# macOS blocks background/root processes from reading inside Desktop, Documents,
# and Downloads unless the specific binary has been granted Full Disk Access -
# regardless of Unix file permissions. A checkout under any of those folders
# (as opposed to e.g. ~/code or /opt) would make Caddy fail to read
# "$ROOT/Caddyfile" with "operation not permitted" and silently loop-crash.
# Copying the config to a system path outside those protected folders sidesteps
# that for every user, no matter where they cloned the repo.
sudo mkdir -p "$CADDY_CONFIG_DIR"
sudo cp "$ROOT/Caddyfile" "$CADDY_CONFIG"
sudo chown root:wheel "$CADDY_CONFIG"
sudo chmod 644 "$CADDY_CONFIG"

# The Caddyfile points Caddy's storage (its local CA root + issued certs) at
# this fixed path explicitly - see the comment in Caddyfile for why. Lock it
# down since it holds the local CA's private key, not just non-secret config.
sudo mkdir -p "$CADDY_CONFIG_DIR/data"
sudo chown -R root:wheel "$CADDY_CONFIG_DIR/data"
sudo chmod 700 "$CADDY_CONFIG_DIR/data"

sudo tee "$CADDY_PLIST" >/dev/null <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>${CADDY_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${CADDY}</string>
        <string>run</string>
        <string>--config</string>
        <string>${CADDY_CONFIG}</string>
        <string>--adapter</string>
        <string>caddyfile</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>${RUNTIME}/caddy.log</string>
    <key>StandardErrorPath</key><string>${RUNTIME}/caddy.log</string>
</dict>
</plist>
PLIST

sudo chown root:wheel "$CADDY_PLIST"
sudo chmod 644 "$CADDY_PLIST"
sudo launchctl bootstrap system "$CADDY_PLIST"

for _ in {1..20}; do
  curl -fsS --max-time 2 "http://$CADDY_ADMIN/config/" >/dev/null 2>&1 && break
  sleep 1
done
sudo "$CADDY" trust --address "$CADDY_ADMIN" >/dev/null

say "Installing automatic refresh (8:00 AM and 8:00 PM)"
if "$VENV_POCKETTRACK" install-scheduler --hours 8,20; then
  "$VENV_POCKETTRACK" scheduler-status || true
else
  echo "Warning: the sync scheduler could not be loaded. Retry later with: pockettrack install-scheduler --hours 8,20"
fi

say "Ready"
echo "Open:  https://${HOSTNAME_LOCAL}"
echo "Stop:  ./stop.sh"
echo "Logs:  $APP_LOG"
