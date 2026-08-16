#!/bin/zsh
# Periodically merges origin/main into the local dp-fp branch of agent-dp.
#
# Rules:
#   - Only runs if dp-fp is the currently checked-out branch.
#   - Only runs if the working tree is clean (no stash, no guessing -
#     if there's uncommitted work, skip this run entirely).
#   - On a merge conflict: abort the merge immediately, leave the repo
#     exactly as it was, and notify.
#   - On success (including "already up to date"): notify.
#
# Installed as a launchd agent - see
# ~/Library/LaunchAgents/com.darshitp.agent-dp-autopull.plist
# (that plist points here; ~/.local/bin/agent-dp-autopull.sh is a symlink
# to this file for convenient manual invocation from a shell)

set -uo pipefail

# launchd runs jobs with a minimal environment (no ~/.zshrc, no Homebrew on
# PATH) - set PATH explicitly so `git` and `terminal-notifier` resolve.
export PATH="/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

REPO_DIR="/Users/darshitp/Desktop/agent-dp"
BRANCH="dp-fp"
SOURCE_BRANCH="main"
LOG="$HOME/Library/Logs/agent-dp-autopull.log"

notify() {
    # $1 = title, $2 = message
    #
    # NOTE: this deliberately uses terminal-notifier, not
    # `osascript -e 'display notification ...'`. osascript-triggered
    # notifications never registered an app identity in Notification
    # Center on this machine (confirmed via a live launchd test - no
    # "Script Editor" entry ever appeared in System Settings, with
    # Focus off, from a real launchd-spawned process) so they silently
    # no-op. terminal-notifier ships as a real .app bundle, which macOS
    # will actually grant notification permission to.
    if command -v terminal-notifier >/dev/null 2>&1; then
        terminal-notifier -title "$1" -message "$2" -sound Glass >/dev/null 2>&1
    fi
}

{
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="

    cd "$REPO_DIR" || {
        echo "ERROR: repo directory not found at $REPO_DIR"
        notify "agent-dp auto-pull" "Failed: repo directory not found"
        exit 1
    }

    current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ "$current_branch" != "$BRANCH" ]; then
        echo "Skipped: currently on '$current_branch', not '$BRANCH'."
        exit 0
    fi

    if [ -n "$(git status --porcelain)" ]; then
        echo "Skipped: working tree has uncommitted changes - won't touch it."
        exit 0
    fi

    before=$(git rev-parse HEAD)

    if git pull origin "$SOURCE_BRANCH" --no-edit 2>&1; then
        after=$(git rev-parse HEAD)
        if [ "$before" = "$after" ]; then
            echo "Already up to date with origin/$SOURCE_BRANCH."
        else
            short_before=$(git rev-parse --short "$before")
            short_after=$(git rev-parse --short "$after")
            echo "Pulled successfully: $short_before..$short_after"
            notify "agent-dp auto-pull" "$BRANCH updated from $SOURCE_BRANCH ($short_before -> $short_after)"
        fi
    else
        echo "Pull failed (merge conflict or other error) - aborting merge to leave repo clean."
        git merge --abort 2>&1
        notify "agent-dp auto-pull" "⚠️ $BRANCH <- $SOURCE_BRANCH pull hit a conflict. Aborted - resolve manually."
    fi
} >> "$LOG" 2>&1
