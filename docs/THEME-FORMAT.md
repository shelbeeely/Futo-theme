# FUTO Keyboard theme format reference

This is a from-source reference for the `theme.txt` format used by
[FUTO Keyboard](https://keyboard.futo.tech/) (Android). It's written from
reading the actual TypeScript source of
[`futo-org/keyboard-theme-editor`](https://github.com/futo-org/keyboard-theme-editor)
(`src/keyboard/render.ts`, `qualifiers.js`, `qualifiers-input.jsx`) and from
comparing every theme published at https://keyboard.futo.tech/themes plus
our own, side by side:

- **Groovy Code** (this repo, `theme.txt`) — a from-scratch dark theme with
  row-banded key colors and a generated keycap look.
- **Pet Keys** by TrashKittyQueen (`p.trashkittyqueen.petkeys`) — a
  Material-3-generated light theme with per-column/per-letter border
  overrides.
- **Christmas 2025** by zilluzion (`art.zilluzion.xmas2025`, downloaded from
  `dl.keyboard.futo.org/christmas-theme-2025.zip`) — a candy/gingerbread
  theme with "bitten cookie" key variants scattered across the board.
- **Theme with OpenDyslexic** by alex (`tech.futo.keyboard.OpenDyslexic`,
  downloaded from `dl.keyboard.futo.org/dyslexic-theme.zip`) — the simplest
  possible real-world theme: just a color scheme and a font swap, no image
  assets or matchrules at all.

None of the last three are included in this repo (different fonts/art, own
licenses) — they're referenced here only for what they demonstrate about the
format. Nothing here is guesswork: every field below was either confirmed in
the editor source or observed working in one of these real theme files. If
you change the format assumptions in this doc, re-verify against a fresh
clone of `keyboard-theme-editor` (and/or re-download the gallery themes)
rather than trusting this file indefinitely — it's a snapshot.

The official (sparser) docs and live editor are at
https://docs.keyboard.futo.tech/theme/advanced and
https://keyboard.futo.tech/theme-editor. The theme gallery is at
https://keyboard.futo.tech/themes.

## File layout

A theme is a folder (zipped for import) containing:

- `theme.txt` — the config, in a TOML-like format (`[section]`,
  `[[array-of-tables]]`, `key = value`).
- Image assets referenced by name from `theme.txt` — key border/background
  art (`Button-*.png` by convention, but any filename works) and icon shapes
  (`Icon-*.png` by convention).
- A font file, if the theme sets `[options.font]`.
- Attribution files for any third-party font/art (not read by the app —
  for humans, and often required by the asset's license).

Supported image formats: **`.png`, `.jpg`/`.jpeg`, `.webp` only** — this is
enforced by the export validator in `ExportWindow.jsx`. SVG is explicitly
rejected. There is also a real size ceiling: any asset that scales to
`max(width, height) × (640 / target_density) > 4096px` is silently dropped
at render time, not rejected at import — a theme can "work" (import cleanly)
and still have missing art on-device because of this.

## Top-level metadata

```toml
name = "Theme Name"
author = "Your Name"
id = "com.example.themename"      # reverse-DNS-style unique id
version = 1                        # integer, bump on every change
description = "Shown in the theme picker. Include font/asset attribution here too."
```

## `[options]`

Global rendering knobs, all confirmed applied in `render.ts`:

| Key | Effect |
|---|---|
| `auto_borders` | `true`/`false` — when true the renderer synthesizes default key borders; themes that supply their own border assets for every state still set this `true` in both example themes (it doesn't appear to disable custom `matchrules.border` — it's closer to "use border-drawing at all" than "ignore my assets"). |
| `center_hints` | Whether corner hint labels (long-press previews) are centered vs. corner-anchored. |
| `roundedness` | Multiplier on the built-in corner radius: `radius = dp(style.radius, density) * options.roundedness`. `1` = default FUTO roundedness, `0.6` = noticeably squarer (used in Groovy Code for a more "keycap" look), `0` would be sharp rectangles. |
| `scale_text` | Multiplier applied to the main label font size (`size *= options.scaleText`). |
| `scale_hints` | Same, for the small corner-hint glyphs. |
| `weight_text` | CSS-style font weight for the main label — literally interpolated into the canvas font string (`` `${weight} ${size*1.1}px theme-font` ``), so it only has a visible effect with a variable-weight font; with a fixed-weight font like FiraCode-Regular it's inert but harmless. |
| `weight_hints` | Same, for hint glyphs. |

## `[colors]`

A full Material 3 color scheme. Every field below is read by the renderer;
`# inherited` comments in the example themes are just editor-tool annotations
("this was auto-derived from `primary` by the Material You generator and I
haven't manually overridden it") — the app itself doesn't care about that
comment, so you can hand-author every value.

Material 3 roles: `primary`, `on_primary`, `primary_container`,
`on_primary_container`, `inverse_primary`, `secondary`, `on_secondary`,
`secondary_container`, `on_secondary_container`, `tertiary`, `on_tertiary`,
`tertiary_container`, `on_tertiary_container`, `background`, `on_background`,
`surface`, `on_surface`, `surface_variant`, `on_surface_variant`,
`surface_tint`, `inverse_surface`, `inverse_on_surface`, `error`, `on_error`,
`error_container`, `on_error_container`, `outline`, `outline_variant`,
`scrim`, `surface_bright`, `surface_dim`, `surface_container`,
`surface_container_high`, `surface_container_highest`,
`surface_container_low`, `surface_container_lowest`.

Keyboard-specific roles (these are the ones that actually paint the visible
keyboard surface/keys when you're *not* overriding everything with border
assets, and they still show through in gaps/background):
`keyboard_surface`, `keyboard_surface_dim`, `keyboard_container`,
`keyboard_container_variant`, `on_keyboard_container`, `keyboard_press`,
`keyboard_container_pressed`, `on_keyboard_container_pressed`.

**Color format is `#RRGGBBAA`** (8 hex digits — alpha last). Both example
themes use this consistently, including for translucent overlay colors like
`keyboard_container_pressed = "#e19d2544"`.

## `[options.font]`

```toml
[options.font]
font = "SomeFont-Regular.ttf"
```

Just a filename relative to the theme package root. Both `.ttf`
(`FiraCode-Regular.ttf` in this repo, `SourGummy-Regular.ttf` in Christmas
2025) and `.otf` (`OpenDyslexic-Regular.otf`) are confirmed working.

## Minimal valid theme

`[options.background]`, every `[[matchrules.*]]` block, and every
`[[asset.*]]` block are **all optional**. The published "Theme with
OpenDyslexic" theme is nothing more than metadata + `[options]` +
`[colors]` + `[options.font]` — no background image, no border/icon
overrides, no asset declarations at all. With no matchrules the renderer
falls back entirely to its own auto-generated key borders (driven by
`auto_borders` and the `[colors]` `keyboard_*` roles), so a theme that only
needs to change the color scheme and/or font doesn't need to touch image
assets at all. This is the right starting point if you're theming for
something like accessibility (a dyslexia-friendly font, a high-contrast
palette) rather than a visual key-face redesign.

## `[options.background]`

```toml
[options.background]
image = "MyTheme-background.png"
opacity = 1                          # background layer's own opacity
action_bar_opacity = 0.3             # opacity of the background under the top action bar strip
cropping = [0.0, 0.0, 1.0, 1.0]      # [left, top, right, bottom] as fractions of image size
```

Confirmed in source: `opacity` feeds `forceAlpha(theme.colors.keyboardSurface, 1.0 - opacity)`
— i.e. it's blended against `keyboard_surface`, so at `opacity = 1` the
`keyboard_surface` color is fully hidden behind the image, and lower values
let the flat color show through underneath/blended with it. `cropping` is a
plain crop rect in image-fraction coordinates (Pet Keys uses
`[0.06, 0.06, 0.9, 0.9]` to crop in from all four edges rather than showing
the whole source image edge-to-edge).

## Matchrules — selectors

```toml
[[matchrules.border]]
selector = "action pressed"
asset = "Button-action-press.png"

[[matchrules.icon]]
selector = "icon delete_key"
asset = "Icon-backspace.png"
```

**Matching is order-dependent and AND-only.** For each key, the renderer
walks the `matchrules.border` (and separately `matchrules.icon`) list top to
bottom and uses the **first** rule whose selector's tokens *all* match
(`matchesKey`: `for (const q of qualifiers) { if (!q.fn(key, kb)) return false; }`).
Space-separated tokens within one `selector` string are pure AND-logic —
there is no OR. To cover multiple cases, write multiple `[[matchrules.*]]`
blocks. **Put your most specific rules first, generic fallbacks
(`pressed`, `normal`) last** — this is why both example themes end their
border matchrules with a bare `pressed` / `normal` catch-all pair.

### Full confirmed selector token vocabulary

| Token | Matches |
|---|---|
| `normal` | Default (unpressed, not sticky) key visual state. |
| `pressed` | Key currently pressed. |
| `functional` | Non-letter functional keys (shift, backspace, 123, etc). |
| `action` | The primary action key (usually enter, context-dependent). |
| `spacebar` | The space key. |
| `stickyoff` | Sticky key (e.g. shift) in the off/unlocked state. |
| `stickyon` | Sticky key in the on/locked state — confirmed as the real caps-lock-engaged state (`visualStyle === "StickyOn"`). |
| `nobackground` | Key drawn with no background layer at all. |
| `morekey` | A long-press popup accent key. |
| `morekeysbox` | The long-press popup's container box. |
| `popup` | Popup-related state, used alongside `functional`/`normal` in both example themes for a distinct popup border look. |
| `code <n>` | Matches by literal numeric keycode. |
| `label <text>` | Matches by the key's literal rendered label string — e.g. `label b` matches a key labeled "b", `label 3` matches one labeled "3". Case-sensitive, exact match, confirmed as `key.label == arg0` in source. |
| `icon <name>` | Matches by icon id — see icon table below. Used only in `matchrules.icon`. |
| `outputtext <text>` | Matches by the text the key actually outputs (useful when label ≠ output, e.g. some symbol keys). |
| `layout <name>` | Matches by which keyboard layout/layer is active (e.g. main letters vs. symbols page). |
| `row <n>` | Matches by row index, 0-based from the top. **Negative counts from the bottom of the *rendered* layout** — `row -1` is always the last row, however many rows that layout actually has. Christmas 2025 uses `functional row -1 col 0` for the bottom-row leftmost functional key (the emoji/settings-adjacent key), same pattern as this repo's use of `row -1`. |
| `col <n>` | Matches by column index, 0-based from the left; negative counts from the right — confirmed in Christmas 2025 (`normal row 1 col -1`, `col -2`) for keys near the right edge, the same way `row -1` counts from the bottom. |
| `rowmod <offset> <mod>` | `(key.row + offset) % mod == 0` — periodic row banding without one rule per row. |
| `colmod <offset> <mod>` | Same, for columns. **A single selector can combine one `rowmod` and one `colmod` together** — Christmas 2025 does this (`selector = "normal rowmod 1 2 colmod 3 5"`) to scatter a handful of "bitten cookie" key variants across the board in a repeating diagonal/checkerboard-like pattern, rather than banding whole rows or whole columns. Since selector tokens are pure AND-logic, this just narrows the match to keys satisfying both periodic conditions at once — useful any time you want a *sparse, deterministic* pattern instead of full-row or full-column theming. |
| `ratio <name>` | Matches by the key's width\:height bucket. Named buckets confirmed in source: `Tallest`, `Tall`, `Squarish`, `Wide`, `ExtraWide`, `Widest` (numeric boundaries aren't in the qualifier-input file itself — treat as a coarse "how wide is this key" hint, e.g. distinguishing spacebar-wide keys from a normal letter key without hardcoding `col`). |
| `layer <n>` | Not a filter — always matches, and instead **tags** the match with a layer value (`obj.layer = arg0`) for the renderer's own bookkeeping. Order it like any other token but don't expect it to narrow the match. |

### Confirmed real icon IDs (`matchrules.icon` values)

From `qualifiers-input.jsx` `ICON_NAMES` (~36 total) cross-checked against
`render.ts` `DEFAULT_ICONS`. Ones both example themes actually wire up:
`shift_key`, `shift_key_shifted`, `delete_key`, `enter_key`, `action_emoji`,
`action_switch_language` (globe/language switch), `mic_fill`
(voice input — note the source list's canonical action name is
`action_voice_input`; `mic_fill` is the icon asset id actually referenced in
this repo's `theme.txt` and it renders correctly, so both may resolve, but
prefer whichever your on-device test confirms), `tab_key`, `action_left`,
`action_right`.

Other confirmed IDs with no theme here wiring them up yet: `space_key`,
`space_key_for_number_layout`, `chevron_right`, `action_undo`, `numpad`,
`settings_key`, `search_key`, `send_key`, `action_settings`, `action_paste`,
`action_text_edit`, `action_themes`, `action_redo`,
`action_clipboard_history`, `action_cut`, `action_copy`, `action_select_all`,
`action_more`, `action_up`, `action_down`. Some of these (zwnj,
previous_key, etc.) may exist in the source but weren't re-confirmed this
pass — check `qualifiers-input.jsx` directly before relying on an ID not in
this list.

**Icons are always force-recolored at render time.** `drawTintedImage` uses
canvas `source-in` compositing: it fills a temp canvas with the theme's
current foreground color for that key state, then composites your icon PNG
in as an alpha mask (`tempCtx.globalCompositeOperation = 'source-in'`).
Whatever RGB you painted into the icon is discarded — **only the
alpha-channel silhouette matters.** This is why `[[asset.icon]]` blocks have
no `background_tint`/`foreground_tint` fields: they'd be silently ignored if
you added them.

## `[[asset.border]]` — key face art

```toml
[[asset.border]]
name = "Button-default.png"
background_tint = "#ffffff"    # "#ffffff" = fully preserve the art's own RGB
foreground_tint = "#f0dfc0"    # color of the label/hint TEXT drawn on top of this key
padding = [0, 0, 0, 0]          # [left, top, right, bottom] — see warning below
slicing = [0.18, 0.18, 0.82, 0.82]  # 9-patch stretch-region bounds, fractions of image size
gap = [1, 1, 1, 1]              # per-edge key-gap multiplier
target_density = 480
```

- **`background_tint`** recolors the border art the same `source-in` way
  icons are recolored, *unless* it's exactly `"#ffffff"`, in which case the
  art's baked-in RGB (your gradient, dish shading, rim highlight — anything
  you painted) survives untouched to the device. Every border asset in both
  example themes uses `"#ffffff"` here for this reason — if you want any
  hand-painted shading to actually show up, keep this white.
- **`foreground_tint`** is unrelated to the art pixels — it sets the color
  the renderer uses to draw the key's **label text** on top of this border,
  independent of the icon-recoloring path.
- **`slicing`** is the 9-patch definition: `[left, top, right, bottom]` as
  fractions (0–1) of the source image's width/height, marking where the
  non-stretching border region ends and the stretchable middle begins (and,
  symmetrically, where the middle ends and the opposite non-stretching edge
  begins). A symmetric key like `Button-default.png` uses
  `[0.3, 0.3, 0.7, 0.7]` — outer 30% on every edge is fixed (so rounded
  corners/rim don't smear when the key is resized), the middle 40% stretches
  to fill whatever key size is needed. An asymmetric asset like a spacebar
  needs asymmetric fractions computed from its actual pixel dimensions (see
  worked example in "Computing slicing values" below).
- **`gap`** shrinks/grows the key's drawn footprint relative to its hit-box,
  per edge, as a multiplier on half the layout's built-in inter-key gap
  (confirmed: `x = key.x + (key.horizontalGap / 2) * gap.left`, etc.). `1` on
  all four edges (both example themes' default) reproduces the standard
  visual gap between keys unmodified. This is the knob to reach for if you
  want keys to look like they have exaggerated (or none) space between them
  — e.g. wider gutters read more like isolated mechanical keycaps, `0` reads
  like a flat continuous surface.
- **`padding`** — **not a fraction of key size**, a raw value consumed
  directly as `keyHintPaddingX`/`keyHintPaddingY` (only when non-zero on
  both the relevant axis pair; otherwise the built-in ~2.5–3dp default is
  used). It controls the corner hint-label offset, nothing about the border
  art itself. A small decorative-looking value like `0.15` copied from a
  reference theme without checking units will crowd hint glyphs into the
  main letter. **Keep `[0,0,0,0]` on any key that has a letter/hint unless
  you've verified real on-device unit semantics** — this was a real,
  previously-shipped bug in this repo (see `docs/GROOVY-CODE-THEME.md`).
- **`target_density`** — the reference density (dp-per-pixel baseline) your
  asset was authored at. Feeds directly into the size-ceiling check
  (`max(w,h) × (640/target_density) > 4096` gets dropped) and into how the
  asset is scaled for the actual device density at render time. `480` and
  `640` are the two values seen in the wild so far (icons in this repo use
  `480` to match their border counterparts; Pet Keys uses `640`
  everywhere). Pick one value and use it consistently for every asset in a
  theme — don't mix without a reason, since it's a scaling reference, not a
  cosmetic label.

### Computing slicing values (worked example, from this repo)

For a 160×160 key with corner radius 26px and a 3px outline, the safe
(non-curved) interior starts at `radius + outline = 29px` from each edge:
`29/160 ≈ 0.18` → `slicing = [0.18, 0.18, 0.82, 0.82]`. For a 640×160
spacebar with radius 30, the interior starts at 33px:
`33/640 ≈ 0.052` horizontally, `33/160 ≈ 0.206` vertically → `slicing =
[0.052, 0.206, 0.948, 0.794]`. **Compute this from your actual asset's pixel
geometry — don't eyeball or copy another theme's numbers**, since they only
make sense relative to that theme's specific corner radius and canvas size.

## `[[asset.icon]]` — icon art

```toml
[[asset.icon]]
name = "Icon-backspace.png"
target_density = 480
```

Deliberately minimal — no tint/padding/slicing/gap fields exist here because
none of them apply (see "Icons are always force-recolored" above; icons
aren't 9-sliced, they're drawn at a fixed size).

## Four real themes, side by side: what they demonstrate

**Groovy Code** (this repo) leans on **periodic/positional** selectors —
`row 0`/`row 1`/`row 2` banding plus the generic `functional`/`action`/
`spacebar`/`stickyon` state buckets — because the design goal is "every key
in this row/role looks the same," authored procedurally (see
`docs/GROOVY-CODE-THEME.md`).

**Pet Keys** leans on **per-key overrides by exact position and label** —
rules like `selector = "normal col 0 row 0"`, `selector = "normal label b"`,
`selector = "pressed col 1 row 2"` layered on top of broader
`functional`/`action`/`spacebar`/`normal` fallbacks. It also ships multiple
named "alt" border variants (`Button-alt1/2/3.png`, `Button-function2.png`,
plus `-dark` variants of the same key for use on different backgrounds) so
individual keys can get one-off decorative treatment (paw prints / animal
motifs at specific letters) without a matchrule for every single key —
just one rule per key that needs to be different, falling through to the
generic asset otherwise. Its border matchrules also show the "specific-
before-generic" ordering this format expects by default: per-position rules
first, then `spacebar`/`action`/`functional`, then `popup`, then the bare
`pressed`/`normal` catch-alls last.

**Christmas 2025** leans on **sparse scatter patterns** via combined
`rowmod`/`colmod` selectors (see the selector table above) to place
"bitten cookie" key variants across the board without hand-picking every
position, plus a genuinely different matchrule *ordering strategy*: its
list starts with `popup`, `morekeysbox`, then a **bare, type-agnostic
`pressed`** rule third — before any `spacebar pressed`/`action pressed`/
`functional pressed` variant even gets a chance to differ. The effect is
deliberate, not a bug: every pressed key in this theme (letter, spacebar,
functional, action alike) renders the same flat "pressed cookie" art,
because nothing more specific for pressed states was ever placed before
that catch-all. This is a legitimate alternative to Groovy Code's/Pet
Keys' approach of differentiating pressed-state art per key type — **group
your matchrules by "how much do I want this state to vary by key type"**,
not just by literal specificity. If you want one uniform pressed look
everywhere, put a bare `pressed` rule early, the same as Christmas 2025
does; if you want pressed state to look different per key role (as this
repo and Pet Keys do), keep the type-specific `pressed` variants ahead of
the generic one instead. Christmas 2025 also demonstrates mapping `morekey`
(the long-press popup accent key) to a fully transparent/blank asset
(`blank.png`, `slicing = [0, 0, 1, 1]`) — a way to suppress individual
accent-key chips so only the containing `morekeysbox` reads as one unified
surface.

**Theme with OpenDyslexic** demonstrates the minimal end of the spectrum —
see "Minimal valid theme" above: no image assets or matchrules needed at
all if you're only changing color/font.

Takeaway if you're designing a new theme: decide up front (a) whether your
per-key variation is **rule-based** (a formula like "row parity" or
"function vs letter" — reach for `row`/`col`/`rowmod`/`colmod` and generic
state tokens), **one-off** (this specific key needs this specific art —
reach for `label`/`code`/exact `row N col M`), or **sparse/scattered**
(combine `rowmod`+`colmod` in one selector); and (b) whether pressed/sticky
states should vary by key type or render uniformly, since that decision is
what actually determines your matchrule ordering, not just "specific
before generic" as a blanket rule. Most real themes mix techniques: broad
rule-based fallbacks with a handful of exact-position or scatter-pattern
overrides layered in front.
