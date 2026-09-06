# Classic-hardware variants

Eight alternate takes on this theme's keycap structure, each replicating a
real device's palette AND its physical character (corner shape, bezel
thickness, key spacing, surface finish) — not just a recolor:

- **Classic keyboards**: **IBM Model M**, **Macintosh Plus**, **Commodore
  64**, and an **amber phosphor terminal** (VT100-style).
- **Classic consoles**: **Game Boy** (DMG), **NES**, **SNES**, and **Game
  Boy Color** — yes, not keyboards, but the same "replicate a real device's
  color identity" idea applied to game consoles instead.

## Why these are separate packages, not a setting inside Groovy Code

FUTO's theme format has no in-app palette switching within one theme — a
`theme.txt` is one fixed `[colors]` block plus one fixed set of border/icon
assets (confirmed from `keyboard-theme-editor` source, see
`docs/THEME-FORMAT.md`). There's no mechanism to ship several palettes in
one package and let the user pick between them at runtime. So "alternative
color options" means more complete, independently-installable theme
packages under `variants/<slug>/`, each with its own `id`/`name`/`theme.txt`
— the user imports whichever one they want in FUTO Keyboard's theme picker,
same as Groovy Code itself.

## Structure: shared rendering code, per-variant palette AND geometry

Every variant reuses the same underlying structure -- an outer well body,
a bright inset face, a rim stroke at the boundary -- but, as of this
round, that's *all* that's shared: colors, corner radius, bezel thickness,
rim weight, key spacing, and gradient contrast are all per-variant. The
first pass at these eight variants only varied color, which made them
Groovy Code's own shape with new paint rather than unique themes -- the
user asked directly for each to be visually distinct, not just
recolored, so a geometry pass followed the color pass (see "Geometry"
below). The rendering code that makes both possible lives in
`scripts/keycap_render.py` (`render_key`, extracted from
`scripts/generate_assets.py` so it could be reused here without
duplicating the function per variant) -- every geometry/material
parameter defaults to Groovy Code v17's own original hardcoded values, so
a profile that sets none of them renders exactly like the old
one-size-fits-all look did; Groovy Code's own output was verified
byte-identical after both the color-sharing and geometry-sharing
refactors. `scripts/generate_variants.py` defines each variant as a small
profile dict (well/face/rim/legend colors, optional bloom, plus the
geometry fields below) and drives the shared renderer + a `theme.txt`
template (assembled from parts — see "Row-banded variants" below) to
produce a complete package per variant.

Run `python3 scripts/generate_variants.py` from the repo root to
(re)generate every `variants/<slug>/` directory from its profile.

## Geometry: what makes each variant an actual unique theme

Six knobs distinguish the variants from each other and from Groovy Code,
each chosen to reflect something real about the hardware, not picked
arbitrarily:

- **`radius`/`space_radius`** — corner roundedness. Small radius reads as
  boxy/blocky (Model M's slab PBT caps, NES's famously rectangular
  buttons, the terminal's flat function keys); large radius reads as
  rounded/pillowy (Mac Plus's low-profile keys, SNES's glossy concave
  buttons).
- **`margin_top`/`margin_side`/`margin_bottom`** — bezel thickness, i.e.
  how much of the well shows around the inset face. Thick margins read as
  a chunky physical housing (Model M, the Game Boy's brick-like shell);
  thin margins read as a minimal design where the key nearly fills its
  housing (Mac Plus, SNES).
- **`rim_width`** — the rim stroke's weight, from a thin hairline (Mac
  Plus, SNES) to a chunky border (Model M) to a thin bright wireframe
  outline that's doing most of the visual work on an otherwise flat board
  (amber terminal).
- **`gap`** — key-to-key spacing (this is `theme.txt`'s own `gap` field,
  now per-variant instead of Groovy Code's fixed `1.15`). Tight for
  keyboards/consoles with closely-packed keys (Model M, SNES); wide for
  the terminal's more schematic, grid-like feel.
- **`face_top_blend`/`face_bottom_scale`** — the inset face's gradient
  contrast, i.e. how deep/glossy/flat the surface reads. High contrast
  with a bright top blend reads as glossy/concave (SNES); low contrast
  reads as flat/matte/digital (the amber terminal's keys are barely
  distinguishable from a flat fill, on purpose -- a terminal function key
  is a slab behind a wireframe outline, not a physically sculpted cap).
- **`roundedness`** (a `theme.txt` `[options]` field, mostly affecting
  auto-generated fallback borders) — derived from `radius` automatically
  (`min(0.95, max(0.15, radius / 40))`) rather than set by hand, so it
  never drifts out of sync with the actual drawn corner shape.

Changing `radius` also changes the 9-patch stretch boundary a theme.txt
needs (see `docs/THEME-FORMAT.md` "Computing slicing values") -- Groovy
Code's own fixed `0.18`/`0.052`/`0.206` values only work for its own
radius 26. `scripts/keycap_render.py`'s `compute_slicing(radius, size)`
generalizes that formula, and `generate_variant()` calls it per profile
so every variant's `slicing` values are always correct for its own
radius, never copy-pasted from Groovy Code's.

## "Match the real hardware" is the one rule across both batches

Asked directly, for the first (keyboard) batch, whether variants should
keep Groovy Code's row-banding or go flat like the keyboard they're
copying, the user chose **flat, matching the real keyboard**. That
principle — match the real hardware, don't invent color-coding it doesn't
have — is what actually governs every variant in both batches, which is
why the second (console) batch isn't uniformly flat: it just happens that
three of the four keyboards were monochrome, and three of the four
consoles are too.

### Classic keyboards

- **IBM Model M** and **Macintosh Plus** are the most literal — the real
  keyboards are genuinely monochrome (no per-row or per-key color coding at
  all), so `face_function`/`face_action`/`face_space` all default to the
  same `face_default` color. The *only* place either variant departs from
  strict monochrome is the `stickyon` (caps-lock-engaged) state, which has
  no on-key equivalent on either real keyboard (both indicate caps-lock via
  a case LED, not a key color change) but still needs to read as "locked"
  in a touchscreen theme — each gets a brightened face plus a small colored
  bloom (amber for Model M, a soft System-6 blue for Mac Plus, a nod to the
  classic Mac UI highlight color rather than any real indicator).
- **Commodore 64** keeps a little more differentiation because the real
  keyboard actually has it: beige keys overall, but a distinct blue-gray
  for the function/system row and a reddish-brown RETURN key — both real
  features of the hardware, not an invented accent. `stickyon` gets a
  bright "blue screen" glow, an artistic nod rather than a literal feature.
- **Amber terminal** is deliberately the flattest of all: every key face is
  the same near-black, with *zero* face-color variation anywhere — the only
  color on the whole board is the amber rim and amber legends (plus a soft
  amber bloom on `action`/`stickyon` to draw the eye, evoking a lit
  terminal cursor block).

### Classic consoles

- **Game Boy (DMG)**, **NES**, and **Game Boy Color** are all genuinely
  monochrome-button hardware (a colored case/shell at most, but every
  button the same color) — same treatment as Model M/Mac Plus: flat, with
  one small accent bloom nodding to a real detail that has no on-button
  equivalent. DMG's `stickyon` bloom is red (the console's actual power
  LED); NES's `action`/`stickyon` bloom is red (a nod to the console's red
  logotype, not a real indicator); Game Boy Color's `stickyon` bloom is
  green (its power LED is green, unlike the original DMG's red one — a
  deliberate, small, correct distinction between the two).
- **SNES is the one exception in either batch**, and deliberately so: the
  SNES controller's entire visual identity IS its four-color face-button
  scheme (Y green / X blue / A red / B yellow), so a flat lavender variant
  would fail to evoke "SNES" at all — going flat here would be the
  inauthentic choice, not the authentic one. So SNES opts back INTO
  row-banding (`"row_banded": True`), the exact mechanism the first batch's
  keyboards deliberately avoided: green across the top row (Y), blue across
  the home row (X), yellow across the bottom row (B), and red on the
  action/enter key (A — the confirm button, so mapping it to "Enter" isn't
  arbitrary), all in a lavender-gray body matching the console's own
  shoulder-button color.

## Row-banded variants: how `theme.txt` assembly handles it

Since SNES needs the same `row0`/`row1`/`row2` matchrules and border assets
as Groovy Code's own root theme (which the flat variants skip entirely),
`scripts/generate_variants.py` builds `theme.txt` from parts rather than
one flat template: a shared `HEAD_TEMPLATE` (metadata/colors/options/
background through the `functional` matchrule), an optional
`MATCHRULES_ROWBANDED` block spliced in only when a profile sets
`"row_banded": True`, a shared `TAIL_TEMPLATE` (the generic pressed/normal
fallback, icon matchrules, and the non-row asset blocks), an optional
`ASSETS_ROWBANDED` block for the row0/1/2 border asset configs, and a
shared `ICON_ASSETS` block. `build_theme_txt()` concatenates the right
parts and formats the whole thing once. A row-banded profile also needs a
`row_faces` dict (`{0: color, 1: color, 2: color}`) and generates six extra
`Button-row*.png` assets (`generate_variant()` handles this automatically
whenever `row_banded` is set) — everything else about the profile dict is
identical to a flat one.

## Per-variant profiles (`scripts/generate_variants.py`)

Color and notable color departure:

| Variant | slug | Well | Face (default) | Rim | Notable color departure |
|---|---|---|---|---|---|
| IBM Model M | `ibm-model-m` | `#8c846d` | `#e8e0c4` ivory | `#6b6455` | none — fully monochrome except `stickyon` |
| Macintosh Plus | `mac-plus` | `#8b8680` | `#d4d0c8` platinum | `#706b62` | none — fully monochrome except `stickyon` |
| Commodore 64 | `commodore-64` | `#6e5738` | `#d6be94` beige | `#4a3b26` | function keys `#7c8a9c` blue-gray, action (RETURN) `#8b4432` rust |
| Amber terminal | `amber-terminal` | `#0a0a0a` | `#161616` near-black | `#ffb000` amber | legend color is the rim color (amber-on-black everywhere) |
| Game Boy (DMG) | `gameboy-dmg` | `#c4bea4` putty | `#3a3a38` dark gray | `#5a584e` | none — fully monochrome except `stickyon` (red LED bloom) |
| NES | `nes` | `#b8b8b2` light gray | `#2b2b2b` near-black | `#8c8c86` | action key gets a soft red bloom (logotype nod), on top of `stickyon`'s |
| SNES | `snes` | `#57536b` lavender | `#8983a0` lavender | `#c8c4d8` | **row-banded**: row0 `#00954c` green, row1 `#0074bf` blue, row2 `#f5a800` yellow, action `#e60012` red |
| Game Boy Color | `gameboy-color` | `#4a2f5e` grape | `#3a2a4a` dark violet | `#8a6ba8` | none — fully monochrome except `stickyon` (green LED bloom) |

Geometry/material (see "Geometry" above for what each column means) —
this is what makes each one an actual unique theme rather than a recolor:

| Variant | radius | bezel (T/S/B) | rim | gap | face gradient | character |
|---|---|---|---|---|---|---|
| IBM Model M | 14 | 16/16/26 | 4 | 1.05 | 0.10 → 0.76 | boxy, thick bezel, deep matte dish, tight-set |
| Macintosh Plus | 32 | 7/7/12 | 2 | 1.1 | 0.08 → 0.90 | rounded, thin bezel, nearly flat |
| Commodore 64 | 20 | 12/12/22 | 3 | 1.15 | 0.16 → 0.80 | baseline chunky sculpted retro key |
| Amber terminal | 6 | 10/10/16 | 2 | 1.3 | 0.04 → 0.94 | blocky, near-flat, wide grid spacing |
| Game Boy (DMG) | 22 | 15/15/24 | 3 | 1.2 | 0.12 → 0.80 | chunky plastic, thick shell bezel |
| NES | 8 | 13/13/22 | 3 | 1.15 | 0.10 → 0.82 | rectangular, minimal rounding |
| SNES | 36 | 8/8/14 | 2 | 1.05 | 0.22 → 0.78 | roundest, thinnest bezel, glossiest |
| Game Boy Color | 28 | 13/13/22 | 3 | 1.15 | 0.14 → 0.80 | rounder/softer than DMG, moderate bezel |

(Groovy Code itself, for comparison, is radius 26, bezel 12/12/20, rim 3,
gap 1.15, gradient 0.14 → 0.82 — untouched by any of this, since these
are `render_key`'s own default parameter values.)

## What's shared vs. generated per variant

Each `variants/<slug>/` directory is fully self-contained (a separate zip
import needs everything present, not references back to the repo root):

- **Generated per variant**: `theme.txt` (own `id`/`name`/`description`/
  `[colors]`/matchrules), border assets (`default`/`function`/`action`/
  `space`/`stickyon`, each with a `-press`/`-pressed` pair — plus
  `row0`/`row1`/`row2` pairs for SNES), and a simple gradient background
  PNG matching the variant's case tone.
- **Copied unchanged from the repo root**: `Icon-*.png` (icons are always
  force-recolored at runtime via canvas `source-in` compositing — see
  `CLAUDE.md` fact #3 — so the same alpha-shape PNGs work for every
  variant's `foreground_tint`), `FiraCode-Regular.ttf`, `FONT-
  ATTRIBUTION.txt`, `ICON-ATTRIBUTION.txt`, and `Button-morekey.png`/
  `Button-morekeysbox.png` (the long-press popup styling — still the
  original gold-ring look from Groovy Code v11, not restyled per variant;
  see "Open items" in `docs/GROOVY-CODE-THEME.md`, same low-priority
  reasoning applies here).

## Packaging and releases

`.github/workflows/package-theme.yml` packages the root Groovy Code theme
(unchanged job) AND, in a separate `discover-variants` + `package-variant`
matrix job, zips and releases each `variants/<slug>/` directory the same
way — one GitHub release per variant, tagged `<slug>-v<version>` (distinct
from the root theme's `v<version>` tags so they never collide). The variant
list is discovered from the `variants/` directory at build time rather than
hardcoded, so adding another variant only requires adding it to `PROFILES`
in `scripts/generate_variants.py` and regenerating — no workflow edit
needed.

## Verification

All eight variants were checked with the `preview-theme` skill (`.claude/
skills/preview-theme/scripts/build_zip.sh variants/<slug>` works directly,
since each variant directory already has a `theme.txt` at its root) on
QWERTY, both after the initial color-only pass and again after the
geometry pass -- the second render is what actually confirmed the eight
read as distinct shapes (boxy vs. rounded, thick-bezel vs. thin, tight vs.
spaced) side by side, not just distinct colors. The amber terminal and
SNES variants were additionally checked on the `?123` Symbols layout
(amber terminal for icon/hint legibility on a uniform-black board, SNES to
confirm row-banding survives onto a different layout the same way Groovy
Code's own row-banding does). Row/hint-label spacing, rim/legend
legibility, and icon recoloring all read correctly on every variant after
both passes. **None of the eight have been confirmed on a real device
yet** — same outstanding gap as Groovy Code itself.

## Adding another variant

1. Add a profile dict to `KEYBOARD_PROFILES` or `CONSOLE_PROFILES` (or a
   new category list, then include it in `PROFILES`) in
   `scripts/generate_variants.py`: `slug`, `name`, `theme_id`,
   `reference_note`, `description`, `well`, `face_default`, `rim`,
   `legend`, plus any of `face_function`/`face_action`/`face_space`/
   `face_stickyon` that should differ from `face_default`, and optional
   `bloom_action_color`/`bloom_action_alpha`/`bloom_stickyon_color`/
   `bloom_stickyon_alpha`. If the real hardware's identity is genuinely
   its color-coding (the SNES case), add `"row_banded": True` and a
   `row_faces` dict instead of forcing it flat.
2. **Also give it its own geometry** — don't just default to Groovy
   Code's shape (that's the mistake this doc's "Geometry" section above
   exists to prevent from recurring). Pick `radius`/`space_radius`,
   `margin_top`/`margin_side`/`margin_bottom`, `rim_width`, `gap`, and
   `face_top_blend`/`face_bottom_scale` that reflect something real about
   the hardware (boxy vs. rounded, thick-cased vs. minimal, glossy vs.
   matte) — see the geometry table above for the range already in use and
   what reads as what.
3. Run `python3 scripts/generate_variants.py` (this also recomputes that
   profile's `slicing`/`gap`/`roundedness` in its `theme.txt` — never hand-
   copy Groovy Code's or another variant's values).
4. Verify with `preview-theme` the same way as the others (see above) --
   specifically confirm the new variant reads as visually distinct from
   its nearest neighbor in the table, not just differently colored.
5. The packaging workflow picks up the new `variants/<slug>/` directory
   automatically on the next push to `main` — no workflow changes needed.
