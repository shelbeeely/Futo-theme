# Classic-keyboard color variants

Four alternate color options for this theme's keycap structure, each
replicating a real classic keyboard's palette: **IBM Model M**, **Macintosh
Plus**, **Commodore 64**, and an **amber phosphor terminal** (VT100-style).

## Why these are separate packages, not a setting inside Groovy Code

FUTO's theme format has no in-app palette switching within one theme — a
`theme.txt` is one fixed `[colors]` block plus one fixed set of border/icon
assets (confirmed from `keyboard-theme-editor` source, see
`docs/THEME-FORMAT.md`). There's no mechanism to ship several palettes in
one package and let the user pick between them at runtime. So "alternative
color options" means four more complete, independently-installable theme
packages under `variants/<slug>/`, each with its own `id`/`name`/`theme.txt`
— the user imports whichever one they want in FUTO Keyboard's theme picker,
same as Groovy Code itself.

## Structure: shared rendering, per-variant palette

Every variant reuses Groovy Code v17's "brown well + bright inset face +
thin rim" keycap structure exactly — same geometry, same 9-patch slicing,
same margins — just recolored. The rendering code that makes that possible
lives in `scripts/keycap_render.py` (`render_key`, extracted from
`scripts/generate_assets.py` specifically so it could be reused here
without duplicating the function four more times). `scripts/
generate_variants.py` defines each variant as a small profile dict (well
color, face color(s), rim color, legend color, optional bloom color) and
drives the shared renderer + a `theme.txt` template to produce a complete
package per variant.

Run `python3 scripts/generate_variants.py` from the repo root to
(re)generate all four `variants/<slug>/` directories from their profiles.

## "Mostly flat," per the real hardware — not row-banded like Groovy Code

Asked directly whether the variants should keep Groovy Code's row-banding
(three shades across the letter rows) or go flat like the keyboard they're
copying, the user chose **flat, matching the real keyboard**. Concretely:

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
  terminal cursor block). This is the closest of the four to "one uniform
  key color throughout."

## Per-variant profiles (`scripts/generate_variants.py`)

| Variant | slug | Well | Face (default) | Rim | Notable departure |
|---|---|---|---|---|---|
| IBM Model M | `ibm-model-m` | `#8c846d` | `#e8e0c4` ivory | `#6b6455` | none — fully monochrome except `stickyon` |
| Macintosh Plus | `mac-plus` | `#8b8680` | `#d4d0c8` platinum | `#706b62` | none — fully monochrome except `stickyon` |
| Commodore 64 | `commodore-64` | `#6e5738` | `#d6be94` beige | `#4a3b26` | function keys `#7c8a9c` blue-gray, action (RETURN) `#8b4432` rust |
| Amber terminal | `amber-terminal` | `#0a0a0a` | `#161616` near-black | `#ffb000` amber | legend color is the rim color (amber-on-black everywhere) |

## What's shared vs. generated per variant

Each `variants/<slug>/` directory is fully self-contained (a separate zip
import needs everything present, not references back to the repo root):

- **Generated per variant**: `theme.txt` (own `id`/`name`/`description`/
  `[colors]`/matchrules — no row-banding matchrules, since these are flat),
  10 `Button-*.png` border assets (`default`/`function`/`action`/`space`/
  `stickyon`, each with a `-press`/`-pressed` pair), and a simple gradient
  background PNG matching the variant's case tone.
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
hardcoded, so adding a fifth variant only requires adding it to `PROFILES`
in `scripts/generate_variants.py` and regenerating — no workflow edit
needed.

## Verification

All four variants were checked with the `preview-theme` skill (`.claude/
skills/preview-theme/scripts/build_zip.sh variants/<slug>` works directly,
since each variant directory already has a `theme.txt` at its root) on
QWERTY, and the amber terminal variant additionally on the `?123` Symbols
layout — row/hint-label spacing, rim/legend legibility, and icon
recoloring all read correctly. **None of the four have been confirmed on a
real device yet** — same outstanding gap as Groovy Code itself.

## Adding another variant

1. Add a profile dict to `PROFILES` in `scripts/generate_variants.py`:
   `slug`, `name`, `theme_id`, `reference_note`, `description`, `well`,
   `face_default`, `rim`, `legend`, plus any of `face_function`/
   `face_action`/`face_space`/`face_stickyon` that should differ from
   `face_default`, and optional `bloom_action_color`/`bloom_action_alpha`/
   `bloom_stickyon_color`/`bloom_stickyon_alpha`.
2. Run `python3 scripts/generate_variants.py`.
3. Verify with `preview-theme` the same way as the other four (see
   above).
4. The packaging workflow picks up the new `variants/<slug>/` directory
   automatically on the next push to `main` — no workflow changes needed.
