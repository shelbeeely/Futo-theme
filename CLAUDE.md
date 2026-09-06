# Continuing: "Groovy Code" FUTO Keyboard theme

## What this is

A custom theme for **FUTO Keyboard** (Android) called "Groovy Code" — a warm-toned
70's palette (gold/orange/rust/brown) with an orange accent, set in FiraCode.
Currently at **v12**. The repo root is the theme package itself: `theme.txt` plus
PNG assets plus the font, ready to zip and sideload into the FUTO Keyboard app's
theme importer.

Repo layout:
- `theme.txt` — the theme config (TOML-like format)
- `Button-*.png` — key face assets (border/background layer)
- `Icon-*.png` — icon assets (backspace, shift, enter, emoji, globe, mic, tab, arrows)
- `FiraCode-Regular.ttf` — the font (SIL OFL 1.1)
- `GroovyCode-background.png` — keyboard background texture
- `FONT-ATTRIBUTION.txt`, `ICON-ATTRIBUTION.txt` — required attributions
- `docs/` — full written-up documentation, see below

## Read `docs/` first — it's the current source of truth

This file is working notes; `docs/` is the maintained reference and is
where new findings get written up going forward:

- `docs/THEME-FORMAT.md` — the complete `theme.txt` format reference,
  verified from `keyboard-theme-editor` source AND cross-checked against
  every theme published at https://keyboard.futo.tech/themes (Pet Keys,
  Christmas 2025, Theme with OpenDyslexic) plus this one. More complete
  than the "Critical facts" list below — that list is kept only for the
  facts specific enough to this theme's own bug history to matter inline.
- `docs/GROOVY-CODE-THEME.md` — this theme's design system, build
  workflow, and fixed-bug history (a cleaner rewrite of the sections
  below — keep both in sync if you change one).
- `docs/MECHANICAL-KEYBOARD-GUIDE.md` — the design direction for the
  *next* theme: making a FUTO theme read as a mechanical/desktop keyboard
  rather than a soft phone keyboard. This is the user's current stated
  goal — read this before starting new design work.

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

8. **Every section past top-level metadata + `[options]` + `[colors]` is
   optional.** Confirmed by the published "Theme with OpenDyslexic" theme,
   which ships no `[options.background]`, no matchrules, and no asset
   blocks at all — just a color scheme and a font swap, relying entirely
   on auto-generated borders. Don't add image assets/matchrules to a theme
   that only needs a palette+font change.

9. **Fonts: both `.ttf` and `.otf` work** (`FiraCode-Regular.ttf` here,
   `OpenDyslexic-Regular.otf` in the gallery theme of the same name).

10. **`row`/`col` negative indexing and combined `rowmod`+`colmod` are both
    real, confirmed in the wild** (Christmas 2025 theme:
    `normal row 1 col -1`, and `normal rowmod 1 2 colmod 3 5` to scatter a
    decorative key variant across a repeating-but-sparse set of positions
    instead of full rows/columns — useful for novelty-keycap placement).

11. **Matchrule ordering doesn't have to go strict-specific-to-generic.**
    Christmas 2025 places a bare, type-agnostic `pressed` rule third in its
    list — before any `spacebar pressed`/`action pressed`/
    `functional pressed` variant — so *every* pressed key renders identical
    art regardless of type. That's a deliberate, valid alternative to this
    theme's approach (vary pressed art per key type): order matchrules by
    how much you want a *state* to vary by key type, not just by literal
    selector specificity.

12. **Border art isn't limited to rounded rectangles.** Christmas 2025's
    keys are gingerbread-cookie silhouettes, several with a literal "bite"
    cut out of the shape — the border asset PNG defines the actual
    silhouette, not just a color fill inside a fixed rounded-rect frame.

13. **A transparent `morekey` asset** (`slicing = [0,0,1,1]`, otherwise
    blank/empty) suppresses individual long-press accent-key chips so only
    the containing `morekeysbox` reads as a single surface — a real
    technique from Christmas 2025, not a hypothetical.

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

- **v12 (mechanical-keyboard pass, not yet screenshotted/confirmed):** the
  design goal changed from "generic keycap-shaped keys" to "reads as a
  mechanical/desktop keyboard," per `docs/MECHANICAL-KEYBOARD-GUIDE.md`.
  Changes: `gap` bumped from `[1,1,1,1]` to `[1.5,1.5,1.5,1.5]` on every
  `[[asset.border]]` (uniformly, so key spacing stays even across the
  board) to expose more background between keys for a "floating keycap"
  look; the dish/rim-highlight/contact-shadow rendering was redone with a
  crisper, less-blurred highlight line and a per-row gamma curve on the
  dish gradient (steeper falloff on `row 0`, gentler on `row 2`) as a
  row-profile cue; the spacebar got two subtle stabilizer-stem dimples.
  `stickyon` was deliberately left flat (no dish) — that's an intentional
  design choice (see "Design system" below), not an oversight. **This
  finally gives the repo the generation script that was missing** —
  `scripts/generate_assets.py` (Pillow) regenerates all 16 non-icon
  `Button-*.png` border assets from constants; it intentionally never
  touches `Icon-*.png`/`Button-morekey.png`/`Button-morekeysbox.png`, which
  closes off the v10 icon-clobbering bug class at the source rather than
  just avoiding it by discipline.

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

Assets are generated with Python + Pillow (PIL), not hand-authored, via
`scripts/generate_assets.py` (run `python3 scripts/generate_assets.py` from
the repo root — it writes the `Button-*.png` files in place). It covers all
16 non-icon border assets: `default`, `function`, `row0`/`row1`/`row2`,
`action`, `space`, `stickyon`, each with a `-press`/`-pressed` pair.
Palette/geometry constants live at the top of the script — see its
docstring before changing radius/canvas-size constants, since `theme.txt`'s
`slicing` values are computed from them (`docs/THEME-FORMAT.md` has the
math). It deliberately never touches `Icon-*.png`, `Button-morekey.png`, or
`Button-morekeysbox.png` — see the v12 entry above for why.

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
- **v12 (mechanical-keyboard pass) has not yet been screenshotted/confirmed
  on-device either** — same rule applies (see "Verification checklist"
  above): don't call the `gap` increase, the crisper rim highlight, the
  per-row dish gamma curve, or the spacebar stabilizer dimples "done" on
  the strength of the generated PNGs alone. This repo's own history (dish
  contrast, icon regression) is exactly why.
- The background (`GroovyCode-background.png`) was deliberately left
  untouched this pass — the mechanical guide's "visible plate between
  keys" idea (`docs/MECHANICAL-KEYBOARD-GUIDE.md`, point 1) calls for a
  plate/PCB-textured background instead of the current soft dark
  sparkle texture, but that's a bigger, harder-to-preview change than the
  keycap rendering and was scoped out to keep this pass reviewable. Good
  next step once v12 is confirmed on-device.
- `scripts/generate_assets.py`'s per-row gamma values (`0.72`/`1.0`/`1.35`
  for row0/row1/row2) and the `gap = 1.5` value are first guesses, not
  device-measured — adjust them in the script (not by hand-editing the
  PNGs) if a real screenshot shows the effect is too subtle or too strong.
