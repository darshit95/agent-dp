#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$ROOT/.runtime"
APP_PID_FILE="$RUNTIME/pockettrack.pid"
OLLAMA_PID_FILE="$RUNTIME/ollama.pid"
APP_LOG="$RUNTIME/pockettrack.log"
OLLAMA_LOG="$RUNTIME/ollama.log"
HOSTNAME_LOCAL="my-pocket-track"
CADDY_ADMIN="127.0.0.1:2020"
MODEL="${POCKETTRACK_OLLAMA_MODEL:-qwen3.5:4b}"

mkdir -p "$RUNTIME"
chmod 700 "$RUNTIME"

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


create_venv() {
    say "Creating fresh Python virtual environment"

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


# ---------------------------------------------------------------
# Self-heal a corrupt/stale venv.
# ---------------------------------------------------------------

if ! venv_is_healthy; then
    say "Existing virtual environment is unhealthy; rebuilding automatically"

    create_venv
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

say "Running tests"
"$VENV_PYTHON" -m pytest -q "$ROOT/tests"

say "Running security diagnostics"
"$VENV_POCKETTRACK" doctor

say "Preparing private local hostname"
if ! grep -Eq "(^|[[:space:]])${HOSTNAME_LOCAL}([[:space:]]|$)" /etc/hosts; then
  echo "127.0.0.1 ${HOSTNAME_LOCAL}" | sudo tee -a /etc/hosts >/dev/null
fi
sudo dscacheutil -flushcache >/dev/null 2>&1 || true
sudo killall -HUP mDNSResponder >/dev/null 2>&1 || true

say "Starting PocketTrack application"
if [[ -f "$APP_PID_FILE" ]] && kill -0 "$(cat "$APP_PID_FILE")" 2>/dev/null; then
  echo "PocketTrack app is already running (PID $(cat "$APP_PID_FILE"))."
else
  rm -f "$APP_PID_FILE"
  export POCKETTRACK_PLAID_ENVIRONMENT="${POCKETTRACK_PLAID_ENVIRONMENT:-production}"
  export POCKETTRACK_OLLAMA_MODEL="$MODEL"
  nohup "$VENV_POCKETTRACK" serve >"$APP_LOG" 2>&1 &
  echo $! > "$APP_PID_FILE"
fi

for _ in {1..30}; do
  if curl -fsS --max-time 2 http://127.0.0.1:8000/ >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS --max-time 2 http://127.0.0.1:8000/ >/dev/null 2>&1 || {
  tail -80 "$APP_LOG" >&2 || true
  fail "PocketTrack backend did not become ready."
}

say "Starting local HTTPS"
# PocketTrack uses its own Caddy admin endpoint so it does not stop or reload an unrelated Caddy instance.
sudo "$CADDY" stop --address "$CADDY_ADMIN" >/dev/null 2>&1 || true
sudo "$CADDY" start --config "$ROOT/Caddyfile" --adapter caddyfile
sudo "$CADDY" trust --address "$CADDY_ADMIN" >/dev/null

say "Installing daily 8:00 AM refresh"
"$VENV_POCKETTRACK" install-scheduler --hour 8 >/dev/null || echo "Warning: daily scheduler could not be loaded. You can retry from Settings/CLI."

say "Ready"
echo "Open:  https://${HOSTNAME_LOCAL}"
echo "Stop:  ./stop.sh"
echo "Logs:  $APP_LOG"
