# Classic-hardware color variants

Eight alternate color options for this theme's keycap structure, each
replicating a real device's palette:

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

## Structure: shared rendering, per-variant palette

Every variant reuses Groovy Code v17's "brown well + bright inset face +
thin rim" keycap structure exactly — same geometry, same 9-patch slicing,
same margins — just recolored. The rendering code that makes that possible
lives in `scripts/keycap_render.py` (`render_key`, extracted from
`scripts/generate_assets.py` specifically so it could be reused here
without duplicating the function per variant). `scripts/generate_variants.py`
defines each variant as a small profile dict (well color, face color(s),
rim color, legend color, optional bloom color) and drives the shared
renderer + a `theme.txt` template (assembled from parts — see "Row-banded
variants" below) to produce a complete package per variant.

Run `python3 scripts/generate_variants.py` from the repo root to
(re)generate every `variants/<slug>/` directory from its profile.

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

| Variant | slug | Well | Face (default) | Rim | Notable departure |
|---|---|---|---|---|---|
| IBM Model M | `ibm-model-m` | `#8c846d` | `#e8e0c4` ivory | `#6b6455` | none — fully monochrome except `stickyon` |
| Macintosh Plus | `mac-plus` | `#8b8680` | `#d4d0c8` platinum | `#706b62` | none — fully monochrome except `stickyon` |
| Commodore 64 | `commodore-64` | `#6e5738` | `#d6be94` beige | `#4a3b26` | function keys `#7c8a9c` blue-gray, action (RETURN) `#8b4432` rust |
| Amber terminal | `amber-terminal` | `#0a0a0a` | `#161616` near-black | `#ffb000` amber | legend color is the rim color (amber-on-black everywhere) |
| Game Boy (DMG) | `gameboy-dmg` | `#c4bea4` putty | `#3a3a38` dark gray | `#5a584e` | none — fully monochrome except `stickyon` (red LED bloom) |
| NES | `nes` | `#b8b8b2` light gray | `#2b2b2b` near-black | `#8c8c86` | action key gets a soft red bloom (logotype nod), on top of `stickyon`'s |
| SNES | `snes` | `#57536b` lavender | `#8983a0` lavender | `#c8c4d8` | **row-banded**: row0 `#00954c` green, row1 `#0074bf` blue, row2 `#f5a800` yellow, action `#e60012` red |
| Game Boy Color | `gameboy-color` | `#4a2f5e` grape | `#3a2a4a` dark violet | `#8a6ba8` | none — fully monochrome except `stickyon` (green LED bloom) |

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
QWERTY; the amber terminal and SNES variants were additionally checked on
the `?123` Symbols layout (amber terminal for icon/hint legibility on a
uniform-black board, SNES to confirm row-banding survives onto a different
layout the same way Groovy Code's own row-banding does). Row/hint-label
spacing, rim/legend legibility, and icon recoloring all read correctly on
every variant. **None of the eight have been confirmed on a real device
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
2. Run `python3 scripts/generate_variants.py`.
3. Verify with `preview-theme` the same way as the others (see above).
4. The packaging workflow picks up the new `variants/<slug>/` directory
   automatically on the next push to `main` — no workflow changes needed.
