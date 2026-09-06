#!/usr/bin/env bash
# Package the theme in the given repo (default: cwd) into an importable
# zip the same way .github/workflows/package-theme.yml does -- same
# exclude list, same theme.txt-driven name/version. Keep this in sync
# with that workflow if the exclude list ever changes.
set -euo pipefail

REPO_DIR="${1:-.}"
OUT_DIR="${2:-/tmp}"

cd "$REPO_DIR"
if [ ! -f theme.txt ]; then
  echo "No theme.txt in $REPO_DIR -- is this the theme repo root?" >&2
  exit 1
fi

name=$(grep -m1 '^name = ' theme.txt | sed -E 's/^name = "(.*)"$/\1/')
version=$(grep -m1 '^version = ' theme.txt | sed -E 's/^version = ([0-9]+)$/\1/')
slug=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed -E 's/^-+//; s/-+$//')

zip_path="$OUT_DIR/${slug}-v${version}.zip"
rm -f "$zip_path"
zip -qr "$zip_path" . \
  -x '.git/*' '.github/*' 'docs/*' 'scripts/*' '.claude/*' 'CLAUDE.md' 'README.md'

echo "$zip_path"
