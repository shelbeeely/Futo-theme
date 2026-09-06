---
name: preview-theme
description: Render a real, on-screen preview of this repo's FUTO Keyboard theme (theme.txt + Button-*.png/Icon-*.png assets) using FUTO's own keyboard-theme-editor rendering code, without needing a real Android device. Use this any time theme.txt or the generated assets change and you want to sanity-check the result -- after running scripts/generate_assets.py, after hand-editing theme.txt (colors, matchrules, gap, slicing, padding), or whenever the user asks to "preview", "render", "screenshot", or "check how the theme looks" before asking for an on-device confirmation. Composition-level bugs (like a keycap dish squeezed by a slicing/gap mismatch, or a color that reads wrong once tiled next to its neighbors) are often invisible when looking at one asset PNG in isolation but obvious in this render -- reach for this before asking the user for a phone screenshot, not instead of it.
---

# Preview the theme with FUTO's real rendering code

## Why this exists

This repo's own rule (see `CLAUDE.md` / `docs/GROOVY-CODE-THEME.md`) is that a
visual change doesn't count as "done" without either reading the render
source or a real device screenshot -- several past bugs (icon regression,
dish contrast, a dish squeezed by a slicing/gap mismatch) were only visible
that way, not from looking at an isolated asset PNG. A real Android device
isn't available in this environment, but `keyboard-theme-editor` -- the same
open-source project whose `render.ts` actually draws the keyboard in the app
-- is a plain browser app (esbuild + vanilla JS, not Electron), so it can be
run locally and driven headlessly. That gives a **real** render, using the
actual app's rendering code, cheaply and repeatably, while iterating.

It is still not a full substitute for an on-device screenshot: real screen
color/gamma, actual pressed-state touch interaction, and `morekeysbox`/
`morekey` (the editor's own preview stubs long-press to always-false) can
only be confirmed on a real device. Use this to catch everything else first
so on-device rounds are spent confirming, not discovering.

## This also runs automatically

`.claude/settings.json` wires `scripts/on_stop_preview.sh` into the **Stop**
hook: whenever an assistant turn ends with `theme.txt` or a
`Button-*.png`/`Icon-*.png` asset changed since the last render (tracked by
a content hash at `.claude/skills/preview-theme/.last-preview-hash`,
gitignored), it re-runs the full pipeline and blocks the stop with a reason
pointing at the fresh screenshot -- so a visual change gets looked at
without anyone having to remember to invoke this skill by hand. It's a
no-op (a single hash compare, no dev server/zip/browser work) on every turn
where nothing theme-related changed, so it doesn't slow down unrelated
work. Run the steps below yourself only when you want a preview mid-turn,
want to control the output location, or are debugging the hook itself.

## Usage

Run from the theme repo root (the directory with `theme.txt` in it):

```bash
# 1. One-time-per-session setup: clone the editor (if not cached), install
#    deps, start its dev server. Safe to re-run -- skips finished steps and
#    self-heals if the dev server died.
bash .claude/skills/preview-theme/scripts/setup_editor.sh

# 2. Package the current working tree into an importable zip.
ZIP=$(bash .claude/skills/preview-theme/scripts/build_zip.sh . /tmp)

# 3. Import it into the running editor and screenshot the rendered keyboard.
#    (Node resolves `playwright` by walking up from the script's own path,
#    so run it from inside the cached checkout where playwright was
#    installed -- copy it in rather than fighting module resolution.)
EDITOR_DIR="$HOME/.cache/futo-preview-theme-editor/keyboard-theme-editor"
cp .claude/skills/preview-theme/scripts/capture_preview.mjs "$EDITOR_DIR/"
(cd "$EDITOR_DIR" && PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node capture_preview.mjs "$ZIP" /tmp/theme-preview)
```

This writes `/tmp/theme-preview/preview.png` -- **read that file with the
Read tool** (it's an image) to actually look at the render. Don't just
report that the script ran; the point is to look at the picture.

## Reading the result

- Check the things this session's own history has shown are easy to get
  wrong: does the dish/inset actually look proportioned right on differently
  shaped keys (letter keys vs. spacebar vs. function row), not squeezed into
  a sliver? Does row-banding/color-per-role read correctly once keys sit
  next to their real neighbors? Are hint labels (small corner glyphs)
  clearly separated from the main letter, not crowding it? Do icons look
  right (correct shape, correctly recolored)?
- If something looks off, it's more informative to crop and zoom into the
  specific key/region than to eyeball the full 1600x1000 screenshot -- e.g.
  a quick inline Python/Pillow crop-and-2x-upscale of the offending key
  before re-reading it as an image. `#workcanvas`'s default view is centered
  and at 100% zoom on load, so key positions are reasonably predictable, but
  if you need a specific key reliably, it's more robust to compute its pixel
  box from a first full screenshot than to hardcode coordinates.
- A `[console.error] data.asset[other] is absent` line in the script's
  output is expected and benign for a theme with no `[[asset.other]]` block
  (font/background assets don't require one) -- it's filtered out of
  `capture_preview.mjs`'s own output already; don't chase it if you see it
  elsewhere (e.g. running the flow manually in a browser).

## Known gotchas (already worked around in the scripts, explained so you
## can debug if something changes upstream)

- **The dev server exits immediately if started the naive way.** esbuild's
  `--servedir` mode watches stdin and stops the instant it sees EOF, which
  happens right away for a bare backgrounded process. `setup_editor.sh`
  works around this with `tail -f /dev/null | npm run dev`, which never
  closes stdin.
- **The About window covers part of the canvas on first load.** A
  screenshot taken before it's closed will have a real chunk of the
  keyboard hidden behind it -- `capture_preview.mjs` closes any open window
  (`.win .bar button`) before doing anything else. If this ever needs
  debugging, it's easy to misread a partially-hidden row as a real
  rendering bug (this happened once already while building this skill).
- **Import goes through the real "File > Import theme..." flow**, which
  accepts a zip (not a bare `theme.txt`) and fully reconstructs the project
  -- matchrules, both border and icon assets, background image + cropping,
  font -- via `src/systems/toml.ts`'s `importToml`. Don't try to shortcut
  this by poking at `theme.txt` fields directly in the page; the real import
  path is what actually gets exercised on a device too.
- **The zip must match what a real device import expects**: `theme.txt`'s
  header comment must literally contain `Format version: 1.0` (the importer
  regex-matches this), and the zip must be built the same way
  `.github/workflows/package-theme.yml` builds the release zip (same
  exclude list) -- `build_zip.sh` mirrors that logic; keep them in sync if
  the exclude list changes (e.g. a new dev-only top-level file or folder).
- **Playwright needs to resolve as a real node_modules dependency.** It's
  installed once into the cached editor checkout
  (`$HOME/.cache/futo-preview-theme-editor/keyboard-theme-editor/node_modules`),
  not globally, because Node's ESM resolution walks up from the *script's
  own path* looking for `node_modules` -- run `capture_preview.mjs` from
  inside (or copied into) that checkout, not from an arbitrary directory.
- The pre-installed Chromium lives at `/opt/pw-browsers` — pass
  `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` (already exported in most
  sessions, but don't assume it) rather than letting Playwright try to
  download its own copy.

## If this breaks

`keyboard-theme-editor` is a live upstream project; if `setup_editor.sh`'s
clone starts failing to build, or `capture_preview.mjs`'s selectors
(`#menuBar`, `.win .bar button`, `li.item >> text=Import theme...`,
`#workcanvas`) stop matching, the upstream UI likely changed. Re-clone fresh
and grep `src/ui.js` (menu structure), `src/systems/toml.ts` (import logic),
and `src/panels/workcanvas.jsx` (canvas element) rather than guessing --
that's how these selectors were found in the first place.
