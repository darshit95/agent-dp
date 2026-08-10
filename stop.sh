#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$ROOT/.runtime"
APP_PID_FILE="$RUNTIME/pockettrack.pid"
OLLAMA_PID_FILE="$RUNTIME/ollama.pid"
CADDY_ADMIN="127.0.0.1:2020"

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

stop_pid_file "$APP_PID_FILE" "PocketTrack"

if command -v caddy >/dev/null 2>&1; then
  sudo "$(command -v caddy)" stop --address "$CADDY_ADMIN" >/dev/null 2>&1 || true
  echo "Stopped PocketTrack HTTPS proxy."
fi

# Only stop Ollama if PocketTrack started that process itself.
stop_pid_file "$OLLAMA_PID_FILE" "PocketTrack-managed Ollama"

echo "PocketTrack is stopped. The local hostname entry is intentionally kept for the next start."
