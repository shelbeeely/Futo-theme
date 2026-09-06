#!/usr/bin/env bash
# Idempotent setup: clone futo-org/keyboard-theme-editor into a cache dir
# (outside this git repo -- it's a third-party checkout with its own
# node_modules, never commit it), install its deps + a local Playwright,
# and make sure its esbuild dev server is listening on port 8000.
#
# Safe to run every time before capture_preview.mjs -- each step is
# skipped if already done, and the dev server check is a live HTTP probe,
# not a pid file, so it self-heals if the server died since last run.
set -euo pipefail

CACHE_DIR="${PREVIEW_THEME_CACHE:-$HOME/.cache/futo-preview-theme-editor}"
REPO_DIR="$CACHE_DIR/keyboard-theme-editor"
PORT="${PREVIEW_THEME_PORT:-8000}"
LOG_FILE="$CACHE_DIR/dev-server.log"

mkdir -p "$CACHE_DIR"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Cloning futo-org/keyboard-theme-editor into $REPO_DIR ..."
  git clone --depth 1 https://github.com/futo-org/keyboard-theme-editor.git "$REPO_DIR"
fi

if [ ! -d "$REPO_DIR/node_modules" ]; then
  echo "Installing keyboard-theme-editor dependencies ..."
  (cd "$REPO_DIR" && npm install)
fi

if [ ! -d "$REPO_DIR/node_modules/playwright" ]; then
  echo "Installing Playwright (using the pre-installed browser, not re-downloading) ..."
  (cd "$REPO_DIR" && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-save playwright@1.56.1)
fi

if curl -sS -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/" 2>/dev/null | grep -q '^200$'; then
  echo "Dev server already running on port $PORT."
else
  echo "Starting dev server on port $PORT (log: $LOG_FILE) ..."
  # esbuild's --servedir stops itself the instant it sees stdin close, which
  # happens immediately for a bare backgrounded process -- `tail -f /dev/null`
  # as stdin never closes, so the server keeps running.
  (cd "$REPO_DIR" && nohup bash -c 'tail -f /dev/null | npm run dev' > "$LOG_FILE" 2>&1 &)

  for _ in $(seq 1 20); do
    sleep 0.5
    if curl -sS -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/" 2>/dev/null | grep -q '^200$'; then
      echo "Dev server is up."
      exit 0
    fi
  done
  echo "Dev server did not come up within 10s -- check $LOG_FILE" >&2
  exit 1
fi
