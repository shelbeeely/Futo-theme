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

## v19: organic shapes + motifs, inspired by "Animal Keys"

Every variant here (and Groovy Code's own root theme) was rebuilt in v19
around a technique borrowed from a real published FUTO theme, **Animal
Keys** by TrashKittyQueen (`p.trashkittyqueen.petkeys`,
https://keyboard.futo.tech/themes) — downloaded and inspected directly
rather than guessed at from its name. Its actual technique turned out to be:

- **Irregular, organic ("cookie"-shaped) key silhouettes** — not clean
  rounded rectangles. Each key's corner radius is perturbed per-angle by a
  few sine harmonics, so the outline reads as hand-cut rather than
  vector-precise.
- **A small motif glyph baked into one or two accent keys' faces** (its
  own paw-print) plus **the same motif scattered across the background**
  at low alpha — the way a theme signs itself without needing photographic
  art.

The user's explicit direction, after seeing this, was to apply it to *all
nine* themes in this repo (Groovy Code included, even though Groovy Code
had just been fixed in v18 to match a different, clean-rounded-rect
reference SVG) — not just the 8 hardware variants. Groovy Code's key
**silhouette** therefore moved away from that SVG's literal shape in v19;
its **color identity** (uniform orange, rust enter key, gold caps-lock) is
what still "matches the reference," unchanged. See
`docs/GROOVY-CODE-THEME.md`'s v19 changelog entry for the full reasoning.

Each of the 8 variants below got its own motif, playing the same role
Animal Keys' paw print plays for itself — baked into `Button-stickyon.png`
only (never `action`, to avoid competing with the enter-key icon glyph)
and scattered across that variant's background.

### 8BitDo research

The user also asked to ground the console variants against 8BitDo's real
retro-keyboard line rather than console hardware alone. Confirmed via web
search: 8BitDo's actual **"Retro Mechanical Keyboard"** product has exactly
four color editions — **N** (NES), **Fami** (Famicom), **M**, and **C64**
(Commodore 64) — which validates this repo's existing Commodore 64 variant
as matching a real, currently-sold product category, not just an invented
idea. 8BitDo's "M Edition" colorway is distinct from either of this repo's
Game Boy or SNES references (it's 8BitDo's own naming, not Nintendo's), so
it didn't inform any specific palette change here — noted for completeness
about what was and wasn't acted on, not as a claim that every variant traces
to an 8BitDo product.

## Structure: shared rendering code, per-variant palette AND geometry

Every variant reuses the same underlying structure — an outer well body, an
inset face with an organic silhouette, a rim stroke at the boundary, and an
optional bloom/motif — but nearly everything about *how* that structure
looks is per-variant: colors, corner radius, wobble (how irregular the
silhouette is), bezel thickness, rim weight, key spacing, gradient
contrast, and motif glyph. The shared rendering code lives in
`scripts/keycap_render.py`:

- `organic_mask(size, seed, radius_frac, wobble, harmonics, supersample)` —
  builds the irregular silhouette itself: a rounded-rectangle signed-
  distance field (distance to an inset "inner rectangle," not distance from
  center — an early ellipse-based attempt produced pointy spacebar ends,
  since an ellipse's curvature scales with aspect ratio and the spacebar
  canvas is 4:1) with the effective radius perturbed per-angle by a few
  sine harmonics seeded per key, supersampled 3x and Lanczos-downsampled
  for clean anti-aliasing.
- `render_organic_key(size, seed, face_color, well_color, rim_color, ...)`
  — composites well/face/rim/bloom as nested masks generated from the
  *same seed* at shrinking `radius_frac` (so shape details agree at every
  layer), plus gradients, optional stabilizer dimples on the spacebar, and
  an optional motif clipped to the face.
- Eight `motif_*` functions (`motif_sunburst`, `motif_switch_cross`,
  `motif_crt`, `motif_chip`, `motif_cursor`, `motif_dpad`,
  `motif_button_pair`, `motif_diamond_cluster`), each simple Pillow
  primitive line-art, one per theme.
- `scatter_motifs(size, motif_fn, color, count, seed, alpha, scale_frac)`
  — scatters a motif across a background at low alpha, per-instance
  jittered size/rotation-free placement.
- `compute_slicing(radius_frac, size, outline)` — the 9-patch stretch
  boundary a `theme.txt` needs, recomputed per variant's own `radius_frac`
  (see `docs/THEME-FORMAT.md` "Computing slicing values").

`scripts/generate_variants.py` defines each variant as a small profile
dict (well/face/rim/legend colors, optional blooms, motif choice, plus the
geometry fields below) and drives the shared renderer + a `theme.txt`
template (assembled from parts — see "Row-banded variants" below) to
produce a complete package per variant.

Run `python3 scripts/generate_variants.py` from the repo root to
(re)generate every `variants/<slug>/` directory from its profile.

## Geometry: what makes each variant an actual unique theme

Four knobs distinguish the variants' silhouette/material from each other
and from Groovy Code, each chosen to reflect something real about the
hardware, not picked arbitrarily:

- **`radius_frac`** — corner roundedness, as a fraction of the key's
  shorter dimension. Small reads as boxy/blocky (Model M's slab PBT caps,
  NES's famously rectangular buttons, the terminal's flat function keys);
  large reads as rounded/pillowy (Mac Plus's low-profile keys, SNES's
  glossy concave buttons).
- **`wobble`** — how far the silhouette departs from a clean rounded
  rectangle, i.e. how "organic"/hand-cut it looks. Low wobble reads as
  precision-molded (Model M, the amber terminal's wireframe-slab keys);
  higher wobble reads as a more irregular, tactile cap (Commodore 64,
  Game Boy Color).
- **`margin_frac`** — bezel thickness, i.e. how much of the well shows
  around the inset face, as a fraction of key size. Thick margins read as
  a chunky physical housing (Model M, the Game Boy's brick-like shell);
  thin margins read as a minimal design where the key nearly fills its
  housing (Mac Plus, SNES).
- **`rim_frac`** — the rim stroke's weight. Thin hairline (Mac Plus, SNES)
  to a chunky border (Model M) to a thin bright wireframe outline doing
  most of the visual work on an otherwise flat board (amber terminal).

Plus two material/spacing knobs, unchanged in role from earlier versions:

- **`gap`** — key-to-key spacing (`theme.txt`'s own `gap` field). Tight
  for keyboards/consoles with closely-packed keys (Model M, SNES); wide
  for the terminal's more schematic, grid-like feel.
- **`face_top_blend`/`face_bottom_scale`** — the inset face's gradient
  contrast, i.e. how deep/glossy/flat the surface reads. High contrast
  with a bright top blend reads as glossy/concave (SNES); low contrast
  reads as flat/matte/digital (the amber terminal's keys are barely
  distinguishable from a flat fill, on purpose).

`roundedness` (a `theme.txt` `[options]` field, mostly affecting
auto-generated fallback borders) is derived automatically from
`radius_frac` (`round(min(0.95, max(0.15, radius_frac * 2.1)), 2)`) rather
than set by hand, so it never drifts out of sync with the actual drawn
corner shape. `key_slicing`/`space_slicing` are likewise always computed
per profile via `compute_slicing(radius_frac, size)`, never copy-pasted
from Groovy Code's or another variant's values.

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
  bloom (amber for Model M, a soft System-6 blue for Mac Plus) and its own
  motif: a switch-stem cross for Model M, a CRT-monitor glyph for Mac Plus.
- **Commodore 64** keeps a little more differentiation because the real
  keyboard actually has it: beige keys overall, but a distinct blue-gray
  for the function/system row and a reddish-brown RETURN key — both real
  features of the hardware, not an invented accent. `stickyon` gets a
  bright "blue screen" glow, an artistic nod rather than a literal feature,
  plus a small IC-chip motif.
- **Amber terminal** is deliberately the flattest of all: every key face is
  the same near-black, with *zero* face-color variation anywhere — the only
  color on the whole board is the amber rim and amber legends (plus a soft
  amber bloom on `action`/`stickyon` to draw the eye, evoking a lit
  terminal cursor block) and a small cursor-prompt motif.

### Classic consoles

- **Game Boy (DMG)**, **NES**, and **Game Boy Color** are all genuinely
  monochrome-button hardware (a colored case/shell at most, but every
  button the same color) — same treatment as Model M/Mac Plus: flat, with
  one small accent bloom nodding to a real detail that has no on-button
  equivalent, plus a D-pad-cross motif (button-pair motif for NES). DMG's
  `stickyon` bloom is red (the console's actual power LED); NES's
  `action`/`stickyon` bloom is red (a nod to the console's red logotype,
  not a real indicator); Game Boy Color's `stickyon` bloom is green (its
  power LED is green, unlike the original DMG's red one — a deliberate,
  small, correct distinction between the two).
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
  shoulder-button color. Its motif is a four-dot diamond cluster tinted in
  the same Y/X/A/B colors, via `motif_diamond_cluster`'s `colors` kwarg —
  the only variant whose motif isn't a single flat color.

## Row-banded variants: how `theme.txt` assembly handles it

Since SNES needs the same `row0`/`row1`/`row2` matchrules and border assets
as Groovy Code's own root theme used through v18 (Groovy Code itself
dropped row-banding in v18 — see its own changelog — but SNES still needs
it, since its face-button colors ARE its identity), `scripts/
generate_variants.py` builds `theme.txt` from parts rather than one flat
template: a shared `HEAD_TEMPLATE` (metadata/colors/options/background
through the `functional` matchrule), an optional `MATCHRULES_ROWBANDED`
block spliced in only when a profile sets `"row_banded": True`, a shared
`TAIL_TEMPLATE` (the generic pressed/normal fallback, icon matchrules, and
the non-row asset blocks), an optional `ASSETS_ROWBANDED` block for the
row0/1/2 border asset configs, and a shared `ICON_ASSETS` block.
`build_theme_txt()` concatenates the right parts and formats the whole
thing once. A row-banded profile also needs a `row_faces` dict
(`{0: color, 1: color, 2: color}`) and generates six extra
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

Geometry/material — the organic-shape knobs (see "Geometry" above) that
make each one an actual unique silhouette rather than a recolor, plus each
variant's own motif glyph:

| Variant | radius_frac | wobble | margin_frac | rim_frac | gap | face gradient | motif | character |
|---|---|---|---|---|---|---|---|---|
| IBM Model M | 0.16 | 0.06 | 0.15 | 0.030 | 1.05 | 0.10 → 0.76 | switch-cross | boxy, thick bezel, low wobble (precision-molded PBT) |
| Macintosh Plus | 0.42 | 0.07 | 0.05 | 0.012 | 1.1 | 0.08 → 0.90 | CRT | rounded, thin bezel, nearly flat |
| Commodore 64 | 0.26 | 0.10 | 0.09 | 0.020 | 1.15 | 0.16 → 0.80 | IC chip | baseline chunky sculpted retro key |
| Amber terminal | 0.10 | 0.04 | 0.05 | 0.014 | 1.3 | 0.04 → 0.94 | cursor prompt | blocky, near-flat, wide grid spacing |
| Game Boy (DMG) | 0.30 | 0.09 | 0.14 | 0.020 | 1.2 | 0.12 → 0.80 | D-pad cross | chunky plastic, thick shell bezel |
| NES | 0.13 | 0.05 | 0.11 | 0.020 | 1.15 | 0.10 → 0.82 | button pair | rectangular, minimal rounding |
| SNES | 0.44 | 0.09 | 0.05 | 0.012 | 1.05 | 0.22 → 0.78 | diamond cluster (4-color) | roundest, thinnest bezel, glossiest |
| Game Boy Color | 0.34 | 0.10 | 0.13 | 0.020 | 1.15 | 0.14 → 0.80 | D-pad cross | rounder/softer than DMG, moderate bezel |

(Groovy Code itself, for comparison, uses `radius_frac=0.30, wobble=0.09,
margin_frac=0.09, rim_frac=0.018`, gap 1.15, gradient 0.14 → 0.82, and a
sunburst motif — see `scripts/keycap_render.py`'s defaults, which every
variant profile above overrides at least some of.)

## What's shared vs. generated per variant

Each `variants/<slug>/` directory is fully self-contained (a separate zip
import needs everything present, not references back to the repo root):

- **Generated per variant**: `theme.txt` (own `id`/`name`/`description`/
  `[colors]`/matchrules), border assets (`default`/`function`/`action`/
  `space`/`stickyon`, each with a `-press`/`-pressed` pair — plus
  `row0`/`row1`/`row2` pairs for SNES), and a gradient background PNG
  matching the variant's case tone, scattered with its own motif glyph.
- **Copied unchanged from the repo root**: `Icon-*.png` (icons are always
  force-recolored at runtime via canvas `source-in` compositing — see
  `CLAUDE.md` fact #3 — so the same alpha-shape PNGs work for every
  variant's `foreground_tint`), `FiraCode-Regular.ttf`, `FONT-
  ATTRIBUTION.txt`, `ICON-ATTRIBUTION.txt`, and `Button-morekey.png`/
  `Button-morekeysbox.png` (the long-press popup styling — still the
  original gold-ring look from Groovy Code v11, not restyled per variant
  or per the organic-shape pass; see "Open items" in
  `docs/GROOVY-CODE-THEME.md`, same low-priority reasoning applies here).

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
QWERTY across the color-only pass, the geometry pass, and again after the
v19 organic-shape rewrite — each render confirmed the eight read as
distinct shapes (boxy vs. rounded, thick-bezel vs. thin, tight vs. spaced,
low-wobble vs. high-wobble) side by side, not just distinct colors, and
that each variant's motif reads correctly on its `stickyon` key and
background. The amber terminal and SNES variants were additionally checked
on the `?123` Symbols layout (amber terminal for icon/hint legibility on a
uniform-black board, SNES to confirm row-banding survives onto a different
layout the same way Groovy Code's own pre-v18 row-banding did). Row/
hint-label spacing, rim/legend legibility, and icon recoloring all read
correctly on every variant after all three passes.

One real bug was caught and fixed during the v19 rewrite: the amber
terminal profile's `description` field originally contained a literal
`">_"` — unescaped double quotes inside a double-quoted TOML string. This
broke `theme.txt` parsing and made `preview-theme`'s import fail
repeatedly with a misleading generic error, initially mistaken for a
network/proxy issue before the malformed file was found by inspection.
Fixed by removing the quote characters from the description text. This is
the second time this exact bug class has hit this repo (previously with
Commodore 64's "blue screen" description) — worth grep-checking any new
profile's `description` string for embedded `"` before regenerating.

**None of the eight have been confirmed on a real device yet** — same
outstanding gap as Groovy Code itself.

## Adding another variant

1. Add a profile dict to `KEYBOARD_PROFILES` or `CONSOLE_PROFILES` (or a
   new category list, then include it in `PROFILES`) in
   `scripts/generate_variants.py`: `slug`, `name`, `theme_id`,
   `reference_note`, `description` (watch for embedded `"` — see the
   amber-terminal bug above), `well`, `face_default`, `rim`, `legend`,
   plus any of `face_function`/`face_action`/`face_space`/`face_stickyon`
   that should differ from `face_default`, and optional
   `bloom_action_color`/`bloom_action_alpha`/`bloom_stickyon_color`/
   `bloom_stickyon_alpha`. If the real hardware's identity is genuinely
   its color-coding (the SNES case), add `"row_banded": True` and a
   `row_faces` dict instead of forcing it flat.
2. **Also give it its own geometry and motif** — don't just default to
   Groovy Code's shape (that's the mistake this doc's "Geometry" section
   above exists to prevent from recurring). Pick `radius_frac`/`wobble`/
   `margin_frac`/`rim_frac`, `gap`, and `face_top_blend`/
   `face_bottom_scale` that reflect something real about the hardware
   (boxy vs. rounded, thick-cased vs. minimal, glossy vs. matte, precision-
   molded vs. hand-cut) — see the geometry table above for the range
   already in use and what reads as what. Either reuse an existing
   `motif_fn` from `scripts/keycap_render.py` if it fits, or write a new
   one (a small Pillow primitive glyph, same pattern as the existing eight)
   if the hardware calls for its own signature shape.
3. Run `python3 scripts/generate_variants.py` (this also recomputes that
   profile's `slicing`/`gap`/`roundedness` in its `theme.txt` — never hand-
   copy Groovy Code's or another variant's values).
4. Verify with `preview-theme` the same way as the others (see above) --
   specifically confirm the new variant reads as visually distinct from
   its nearest neighbor in the table, not just differently colored, and
   that its motif is legible on `stickyon` and the background.
5. The packaging workflow picks up the new `variants/<slug>/` directory
   automatically on the next push to `main` — no workflow changes needed.
