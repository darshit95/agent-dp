#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$ROOT/.runtime"
APP_PID_FILE="$RUNTIME/pockettrack.pid"
OLLAMA_PID_FILE="$RUNTIME/ollama.pid"
CADDY_ADMIN="127.0.0.1:2020"
CADDY_LABEL="com.pockettrack.caddy"
CADDY_PLIST="/Library/LaunchDaemons/${CADDY_LABEL}.plist"
VENV_POCKETTRACK="$ROOT/.venv/bin/pockettrack"

# Keep the CLI importable even if the venv's .pth has been marked hidden by a
# cloud-sync agent; otherwise stop.sh cannot unload the autostart agent.
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

stop_pid_file() {
  local file="$1" label="$2"
  if [[ -f "$file" ]]; then
    local pid
    pid="$(cat "$file" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      for _ in {1..20}; do kill -0 "$pid" 2>/dev/null || break; sleep .2; done
      kill -9 "$pid" 2>/dev/null || true
      echo "Stopped $label (PID $pid)."
    fi
    rm -f "$file"
  fi
}

# The app is a KeepAlive LaunchAgent, so killing the process would only make
# launchd restart it. Unloading the agent is the actual off switch.
if [[ -x "$VENV_POCKETTRACK" ]] && "$VENV_POCKETTRACK" uninstall-autostart 2>/dev/null; then
  :
else
  # Fall back to launchctl directly if the CLI is unavailable for any reason.
  launchctl bootout "gui/$(id -u)/com.pockettrack.app" >/dev/null 2>&1 || true
  rm -f "$HOME/Library/LaunchAgents/com.pockettrack.app.plist"
fi
echo "Stopped PocketTrack and disabled start-at-login."

# Older releases started the server with nohup and recorded a PID file.
stop_pid_file "$APP_PID_FILE" "PocketTrack (legacy process)"

if [[ -f "$CADDY_PLIST" ]]; then
  sudo launchctl bootout "system/$CADDY_LABEL" >/dev/null 2>&1 || true
  sudo rm -f "$CADDY_PLIST"
  echo "Stopped PocketTrack HTTPS proxy."
elif command -v caddy >/dev/null 2>&1; then
  sudo "$(command -v caddy)" stop --address "$CADDY_ADMIN" >/dev/null 2>&1 || true
  echo "Stopped PocketTrack HTTPS proxy."
fi

# Only stop Ollama if PocketTrack started that process itself.
stop_pid_file "$OLLAMA_PID_FILE" "PocketTrack-managed Ollama"

echo
echo "PocketTrack is stopped and will stay stopped after a restart."
echo "The local hostname entry is intentionally kept for the next start."
echo "Scheduled transaction syncs are still installed and keep running at 8:00 AM and 8:00 PM."
echo "  Stop those too with:  ./.venv/bin/pockettrack uninstall-scheduler"
echo "  Start everything:     ./start.sh"
