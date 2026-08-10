#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
REPO="${1:-}"
VISIBILITY="${2:---public}"
if [[ -z "$REPO" ]]; then echo "Usage: ./scripts/publish-github.sh OWNER/pockettrack [--public|--private]" >&2; exit 2; fi
if [[ "$VISIBILITY" != "--public" && "$VISIBILITY" != "--private" ]]; then echo "Visibility must be --public or --private" >&2; exit 2; fi
if ! command -v gh >/dev/null 2>&1; then
  command -v brew >/dev/null 2>&1 || { echo "Install GitHub CLI first: https://cli.github.com/" >&2; exit 2; }
  brew install gh
fi
gh auth status >/dev/null 2>&1 || gh auth login
[[ -d .git ]] || git init -b main
git add .
if ! git diff --cached --quiet; then git commit -m "Publish PocketTrack"; fi
if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin HEAD
else
  gh repo create "$REPO" --source=. "$VISIBILITY" --remote=origin --push
fi
echo "Published: https://github.com/$REPO"
