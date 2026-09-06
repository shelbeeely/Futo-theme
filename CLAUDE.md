# Continuing: "Groovy Code" FUTO Keyboard theme

## What this is

A custom theme for **FUTO Keyboard** (Android) called "Groovy Code" — a warm-toned
70's palette (gold/orange/rust/brown) with an orange accent, set in FiraCode.
Currently at **v11**. The repo root is the theme package itself: `theme.txt` plus
PNG assets plus the font, ready to zip and sideload into the FUTO Keyboard app's
theme importer.

Repo layout:
- `theme.txt` — the theme config (TOML-like format)
- `Button-*.png` — key face assets (border/background layer)
- `Icon-*.png` — icon assets (backspace, shift, enter, emoji, globe, mic, tab, arrows)
- `FiraCode-Regular.ttf` — the font (SIL OFL 1.1)
- `GroovyCode-background.png` — keyboard background texture
- `FONT-ATTRIBUTION.txt`, `ICON-ATTRIBUTION.txt` — required attributions

## Critical facts, verified from source (don't re-derive these — they're confirmed)

I didn't guess any of this — I cloned `github.com/futo-org/keyboard-theme-editor`
and read the actual TypeScript source. If you need to re-verify anything, clone
that repo fresh rather than trusting docs/assumptions, since FUTO's theme format
is sparsely documented anywhere else.

1. **Selector syntax is pure AND-logic.** Every space-separated token in a
   `selector = "..."` string must all match (`src/keyboard/qualifiers.js`).
   Full valid token list: `normal functional action spacebar pressed popup
   stickyoff stickyon nobackground morekey morekeysbox code label icon ratio
   outputtext layout row col rowmod colmod layer`.
   `row -1` means "last row," counted from the actual rendered layout.

2. **Real icon IDs** (`src/keyboard/qualifiers-input.jsx` `ICON_NAMES`, confirmed
   against `render.ts` `DEFAULT_ICONS`): `shift_key`, `shift_key_shifted`,
   `delete_key`, `space_key`, `space_key_for_number_layout`, `enter_key`,
   `action_emoji`, `chevron_right`, `mic_fill`, `action_switch_language` (globe),
   `action_left`, `action_right`, `action_undo`, `numpad`, `tab_key`, plus ~15
   more unused ones (settings, zwnj, previous_key, etc.) — see the file directly
   for the complete list if you want to wire up more.

3. **Icons are ALWAYS force-recolored at runtime.** `drawTintedImage` in
   `render.ts` uses canvas `source-in` compositing — it discards whatever RGB
   you paint into an icon PNG and refills it with the theme's foreground color
   for that key state. **Only the alpha-channel shape matters for icons.**
   This is why `[[asset.icon]]` blocks never have `background_tint`/
   `foreground_tint` fields — they'd be silently ignored.

4. **Border/background art is the opposite** — fully preserved, never
   recolored, when `background_tint = "#ffffff"`. That's how the baked
   gradient/dish shading on the key faces survives to the real device.
   `foreground_tint` on a border asset controls the *label text* color drawn
   on top of that key, not the art itself.

5. **`padding` on `[[asset.border]]` controls hint-label corner offset**, and
   it's consumed as a raw value, NOT a fraction of key size — `padding.top`/
   `padding.right` directly become `keyHintPaddingY`/`keyHintPaddingX` in
   `render.ts`, overriding the sane built-in default (~2.5–3dp) the moment
   they're non-zero. A small decorative-looking value like `0.15` (copied
   from a reference theme without checking units) will crowd hint glyphs
   into the main letter. **Keep padding at `[0,0,0,0]` on any asset with a
   letter/hint unless you've verified the real unit semantics on-device.**

6. **Supported asset formats: `.png`, `.jpg`/`.jpeg`, `.webp` only** — verified
   in `ExportWindow.jsx`'s export validator. SVG is explicitly rejected at
   export. There's also a real size ceiling: any asset scaling to
   `max(w,h) × (640 / target_density) > 4096px` gets silently dropped.

7. **`stickyon`** is the real, confirmed caps-lock border state
   (`visualStyle === "StickyOn"`). Give it its own border asset for a clear
   locked-state look — don't rely on the icon alone (see #3, icon color is
   futile there anyway).

## Bugs found and fixed this round (don't reintroduce them)

- **Icon regression (fixed in v10, verify it stuck):** the asset-generation
  script (see below) originally hand-drew icons with PIL, then I later
  replaced 8 of them with proper conversions from FUTO's own official SVG
  icon set (rasterized via `cairosvg` from `keyboard-theme-editor/www/icons/*.svg`,
  BSD-3-Clause, attribution in `ICON-ATTRIBUTION.txt`). Re-running the *whole*
  generation script for unrelated changes (button shading, keycap shape)
  silently re-executed the old hand-drawn icon code and clobbered the official
  ones back — twice. If you touch the generation script, either delete the
  dead hand-drawn icon code entirely, or make icon-restoration an atomic part
  of every regeneration run, not a separate step you can forget.

- **Keycap dish contrast (fixed in v11):** the concave "dish" inset on each
  key was shaded with a fixed *absolute* RGB delta (~-14/channel). That reads
  fine on the bright orange action key (contrast ratio ~1.18) but is nearly
  invisible on near-black functional keys (~1.09) — confirmed via a real
  device screenshot where the enter key's dish was obvious and the letter
  keys' wasn't. Fixed by switching to *multiplicative* darkening (72%→40% of
  base color) plus a brighter rim highlight (alpha 40→95), so it scales
  correctly across the whole palette instead of one flat number tuned for
  one color.

- **Row-banding matchrule ordering:** row-specific border rules
  (`normal row 0`, `normal row 1`, `normal row 2`, plus their `pressed`
  variants) must sit AFTER the `action`/`spacebar`/`functional` rules and
  BEFORE the generic `pressed`/`normal` fallback, since matchrules are
  order-dependent (first match wins). Confirmed correct in the current
  `theme.txt` — preserve this order if you edit that block.

## Design system currently in place

- **Palette:** gold `#e19d25`, orange `#e17a25`, orange-red `#e14e25`, rust
  `#bd361e`, clay `#b37545`, brown `#874725`, near-black `#422118`-derived —
  originally pulled from a "Warm-toned Groovy 70's" palette image the user
  uploaded.
- **Row-banded letter keys:** top row = orange-red border, home row = orange,
  bottom row = brightened rust (lightened from the raw palette rust to clear
  3:1 contrast against the key face) — mirrors the source palette's stacked
  swatch order.
- **Gold border** = "system key" signal (shift, backspace, 123, gear, comma/period).
- **Solid gold fill** (`stickyon` asset) = caps-lock engaged.
- **Orange fill** = the enter/action key.
- **Keycap silhouette:** outer body + inset concave dish + shadow + rim
  highlight, not a flat blob — mimics a real physical keycap viewed head-on.

## Build workflow

Assets are generated with Python + Pillow (PIL), not hand-authored. The
generation script does NOT currently exist in this repo — it lived in the
prior session's scratch space. You'll likely want to rebuild it from scratch
based on the descriptions above (rounded-rect key faces with gradient body +
multiplicative-darkened inset dish + rim highlight + border color per key
type), rather than trying to reverse-engineer exact pixel values from the
PNGs. The important part is the *approach* (documented above), not
reproducing byte-identical output.

Icons: 8 of them (`Icon-backspace/shift/enter/emoji/globe/mic/arrow-left/arrow-right.png`)
are straight rasterizations of FUTO's own SVGs — if you need to regenerate,
re-clone `keyboard-theme-editor` and convert `www/icons/*.svg` with `cairosvg`
at ~288×288. `Icon-shift-press.png` (solid caps-lock arrow) and `Icon-tab.png`
are original, hand-drawn — no official SVG exists for either.

## Verification checklist before calling any change "done"

Every fix in this project so far was validated by (a) reading the actual
`keyboard-theme-editor` TypeScript source rather than guessing at the format,
and (b) the user testing on a real device and sending a screenshot — several
issues (icon overlap, dish contrast, icon regression) were only catchable
that way, not from static analysis alone. Don't declare a visual fix correct
without one or the other.

## Open items / not yet done

- The `?123` symbol/number layout has no custom row-banding or borders —
  untouched since we never had a screenshot of it to design against.
- ~15 other confirmed real icon IDs are unused (settings, numpad, undo,
  chevron_right, zwnj, previous_key, etc.) — only added the ones with a clear
  coding-relevant use case (tab, cursor arrows, globe, mic).
- `morekeysbox`/`morekey` (long-press accent popup) styling was added but
  never confirmed on a real device — the editor's own JS preview stubs these
  to always-false, so it could only be verified in the real Android app.
- v11 (multiplicative dish shading) has not yet been screenshotted/confirmed
  on-device — that's the immediate next verification step.
