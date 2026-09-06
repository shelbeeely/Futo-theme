# Groovy Code — this repo's theme

"Groovy Code" is a warm-toned 70's palette (gold/orange/rust/brown) with an
orange accent, set in FiraCode. Currently at **v12**. The repo root *is* the
theme package — `theme.txt` plus PNG assets plus the font, ready to zip and
sideload into FUTO Keyboard's theme importer. See `docs/THEME-FORMAT.md` for
what every field in `theme.txt` means in general; this doc is about the
choices specific to this theme.

## Design system

- **Palette:** gold `#e19d25`, orange `#e17a25`, orange-red `#e14e25`, rust
  `#bd361e`, clay `#b37545`, brown `#874725`, near-black `#422118`-derived —
  pulled from a "Warm-toned Groovy 70's" reference palette image.
- **Row-banded letter keys:** top row = orange-red border, home row =
  orange, bottom row = brightened rust (lightened from the raw palette rust
  to clear 3:1 contrast against the key face) — mirrors the source
  palette's stacked swatch order. Implemented with `normal row 0`/
  `row 1`/`row 2` matchrules (see `theme.txt`).
- **Gold border** = "system key" signal (shift, backspace, 123, gear,
  comma/period) — i.e. the `functional` matchrules.
- **Solid gold fill** (`stickyon` asset) = caps-lock engaged. Confirmed as
  the real caps-lock-locked visual state, not just an icon change — see
  `docs/THEME-FORMAT.md`'s `stickyon` entry.
- **Orange fill** = the `action` (enter) key.
- **Keycap silhouette:** outer body + inset concave dish + shadow + rim
  highlight, not a flat blob — mimics a real physical keycap viewed head-on.
  As of v12 this is explicitly styled toward a mechanical-keyboard look
  (see below), following `docs/MECHANICAL-KEYBOARD-GUIDE.md`.
- **v12 mechanical-keyboard pass:** `gap` raised from `1` to `1.5` on every
  border asset (uniformly, so spacing stays even) to expose more
  background between keys — the single highest-leverage move in the
  mechanical guide. The dish/rim-highlight/shadow rendering was redone
  with a crisper, less-blurred highlight and a per-row gamma curve on the
  dish gradient (steeper on `row 0`, gentler on `row 2`) as a row-profile
  cue, and the spacebar got two subtle stabilizer-stem dimples.
  `stickyon` stayed deliberately flat — see the caps-lock bullet above,
  that's intentional, not something the mechanical pass missed.

## Build workflow

Assets are generated with Python + Pillow (PIL), not hand-authored, via
`scripts/generate_assets.py` — run `python3 scripts/generate_assets.py`
from the repo root to regenerate all 16 non-icon `Button-*.png` border
assets in place. Palette and geometry constants live at the top of the
script; the geometry constants (radius/outline/canvas size) must match
`theme.txt`'s `slicing` values (see `docs/THEME-FORMAT.md`'s "Computing
slicing values") if you change them. It deliberately never touches
`Icon-*.png`, `Button-morekey.png`, or `Button-morekeysbox.png` — see the
icon-regression bug below for why that boundary is load-bearing, not
incidental.

Icons: `Icon-backspace/shift/enter/emoji/globe/mic/arrow-left/arrow-right.png`
are straight rasterizations of FUTO's own SVGs — if you regenerate, re-clone
`keyboard-theme-editor` and convert `www/icons/*.svg` with `cairosvg` at
~288×288. `Icon-shift-press.png` (solid caps-lock arrow) and `Icon-tab.png`
are original, hand-drawn — no official SVG exists for either. See
`ICON-ATTRIBUTION.txt`/`FONT-ATTRIBUTION.txt` for the license terms this
theme ships under for third-party art/font.

## Bugs found and fixed (history — don't reintroduce these)

- **Icon regression (fixed v10):** the generation script originally
  hand-drew icons with PIL, then 8 were later replaced with proper
  conversions from FUTO's own SVGs. Re-running the *whole* generation
  script for unrelated changes (button shading, keycap shape) silently
  re-executed the old hand-drawn icon code and clobbered the official ones
  back — twice. **If you touch the generation script, either delete the
  dead hand-drawn icon code entirely, or make icon-restoration an atomic
  part of every regeneration run**, not a separate step you can forget.
- **Keycap dish contrast (fixed v11):** the concave "dish" inset was
  originally shaded with a fixed *absolute* RGB delta (~-14/channel). That
  reads fine on the bright orange action key (contrast ratio ~1.18) but is
  nearly invisible on near-black functional keys (~1.09) — confirmed via a
  real device screenshot where the enter key's dish was obvious and the
  letter keys' wasn't. Fixed by switching to *multiplicative* darkening
  (72%→40% of base color) plus a brighter rim highlight (alpha 40→95), so
  it scales correctly across the whole palette instead of one flat number
  tuned for one color.
- **Icon-regression boundary is now enforced by code, not just discipline:**
  `scripts/generate_assets.py` structurally cannot touch `Icon-*.png` — it
  has no code path that writes those filenames at all, closing off the
  v10 bug class (see above) at the source rather than relying on
  remembering not to reintroduce it.
- **Row-banding matchrule ordering:** row-specific border rules
  (`normal row 0/1/2` plus their `pressed` variants) must sit AFTER the
  `action`/`spacebar`/`functional` rules and BEFORE the generic
  `pressed`/`normal` fallback — matchrules are order-dependent, first match
  wins (see `docs/THEME-FORMAT.md`). Confirmed correct in the current
  `theme.txt` — preserve this order if you edit that block.
- **Hint-label padding units:** `padding` on a border asset is a *raw*
  value, not a fraction of key size (see `docs/THEME-FORMAT.md`). A small
  decorative-looking value copied from a reference theme without checking
  units will crowd hint glyphs into the main letter. This theme keeps
  `padding = [0,0,0,0]` on every asset that has a letter/hint for this
  reason.

## Verification method

Every fix in this project was validated by (a) reading the actual
`keyboard-theme-editor` TypeScript source rather than guessing at the
format, and (b) testing on a real device and comparing a screenshot —
several issues (icon overlap, dish contrast, icon regression) were only
catchable that way, not from static analysis alone. **Don't declare a
visual fix correct without one or the other.**

## Open items / not yet done

- The `?123` symbol/number layout has no custom row-banding or borders —
  untouched since there's been no screenshot of it to design against.
- ~15 other confirmed real icon IDs are unused (settings, numpad, undo,
  chevron_right, previous_key, etc. — full list in
  `docs/THEME-FORMAT.md`) — only the ones with a clear coding-relevant use
  case (tab, cursor arrows, globe, mic) have been wired up so far.
- `morekeysbox`/`morekey` (long-press accent popup) styling was added but
  never confirmed on a real device — the editor's own JS preview stubs
  these to always-false, so it can only be verified in the real Android
  app.
- v11 (multiplicative dish shading) has not yet been screenshotted/confirmed
  on-device — that's the immediate next verification step.
- **v12 (mechanical-keyboard pass) also has not been screenshotted/
  confirmed on-device.** Don't call the `gap` increase, per-row dish gamma,
  crisper highlight, or spacebar dimples "done" without a real device
  screenshot — same rule as every other visual change in this project's
  history.
- The background (`GroovyCode-background.png`) was deliberately left
  untouched in v12 — a plate/PCB-textured background (mechanical guide,
  point 1: "visible plate between keys") is a bigger, harder-to-preview
  change than the keycap rendering and was scoped out to keep v12
  reviewable. Good next step once v12 is confirmed.
