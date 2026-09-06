#!/usr/bin/env bash
# Stop hook: if theme.txt or the Button-*/Icon-*.png assets changed since
# the last auto-render, re-run the preview-theme pipeline and block the
# stop with a reason pointing at the screenshot -- so a visual change
# actually gets looked at instead of silently sitting on disk.
#
# Deliberately cheap when nothing changed: just a content hash compare,
# no dev-server/zip/browser work, so it doesn't slow down every turn.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
cd "$REPO_DIR" || exit 0

[ -f theme.txt ] || exit 0

HASH_FILE=".claude/skills/preview-theme/.last-preview-hash"
CURRENT_HASH=$(cat theme.txt Button-*.png Icon-*.png 2>/dev/null | sha256sum | cut -d' ' -f1)
PREV_HASH=$(cat "$HASH_FILE" 2>/dev/null || echo "")

if [ "$CURRENT_HASH" = "$PREV_HASH" ] && [ -n "$CURRENT_HASH" ]; then
  exit 0
fi

OUT_DIR="/tmp/theme-preview-autohook"
LOG="/tmp/preview-hook.log"
export PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers

: > "$LOG"
if ! bash "$SCRIPT_DIR/setup_editor.sh" >>"$LOG" 2>&1; then
  echo "{\"decision\":\"block\",\"reason\":\"theme.txt/assets changed but preview-theme's setup_editor.sh failed -- see $LOG. The change has NOT been visually verified.\"}"
  exit 0
fi

ZIP=$(bash "$SCRIPT_DIR/build_zip.sh" "$REPO_DIR" /tmp 2>>"$LOG")
if [ -z "$ZIP" ] || [ ! -f "$ZIP" ]; then
  echo "{\"decision\":\"block\",\"reason\":\"theme.txt/assets changed but preview-theme's build_zip.sh failed to produce a zip -- see $LOG. The change has NOT been visually verified.\"}"
  exit 0
fi

EDITOR_DIR="$HOME/.cache/futo-preview-theme-editor/keyboard-theme-editor"
cp "$SCRIPT_DIR/capture_preview.mjs" "$EDITOR_DIR/" 2>>"$LOG"

if (cd "$EDITOR_DIR" && node capture_preview.mjs "$ZIP" "$OUT_DIR") >>"$LOG" 2>&1; then
  echo "$CURRENT_HASH" > "$HASH_FILE"
  echo "{\"decision\":\"block\",\"reason\":\"theme.txt or the Button-*/Icon-*.png assets changed since the last render. preview-theme auto-rendered the update to $OUT_DIR/preview.png (real FUTO rendering code, via keyboard-theme-editor) -- read that image now with the Read tool and check it (dish proportions, row-banding colors, hint-label spacing, icon shapes) before treating this change as done. It's still not an on-device confirmation.\"}"
else
  echo "{\"decision\":\"block\",\"reason\":\"theme.txt/assets changed but preview-theme's capture_preview.mjs failed -- see $LOG. The change has NOT been visually verified.\"}"
fi
exit 0
