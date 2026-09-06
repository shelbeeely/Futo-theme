# Groovy Code — this repo's theme

"Groovy Code" is a warm-toned 70's palette (gold/orange/rust/brown) with an
orange accent, set in FiraCode. Currently at **v17**. The repo root *is* the
theme package — `theme.txt` plus PNG assets plus the font, ready to zip and
sideload into FUTO Keyboard's theme importer. See `docs/THEME-FORMAT.md` for
what every field in `theme.txt` means in general; this doc is about the
choices specific to this theme.

## Design system

- **Palette:** gold `#e19d25`, orange `#e17a25`, orange-red `#e14e25`, rust
  `#bd361e`, clay `#b37545`, brown `#874725`, near-black `#422118`-derived —
  pulled from a "Warm-toned Groovy 70's" reference palette image. This
  remains the only source of color anywhere in the rendering, including
  the v17 redesign below — only the *structure* (well + inset face + gold
  rim) came from an external reference, never its colors.
- **Keycap structure, v17 — brown outer "well" + bright inset face + thin
  gold rim, on every key.** Replaces v15/v16's dark-charcoal-single-surface
  look entirely. See the v17 entry below for why and what.
- **Row-banded letter keys:** top row = orange-red, home row = orange,
  bottom row = brightened rust — mirrors the source palette's stacked
  swatch order, implemented with `normal row 0`/`row 1`/`row 2` matchrules
  (see `theme.txt`). As of v17 this is a solid, clearly visible inset-face
  color per row again (not the v15/v16 near-imperceptible tint) — see the
  v17 entry below. Confirmed via `preview-theme` on the `?123` Symbols and
  Numpad layouts too, not just QWERTY — nothing layout-specific was needed.
- **Gold inset face** = "system key" signal (shift, backspace, 123, gear,
  comma/period) — i.e. the `functional` matchrules. As of v17 this is a
  solid, clearly visible gold face again, reversing v15/v16's
  near-imperceptible tint — this directly answers the "Open items"
  question those versions had flagged (restore the cue vs. match the dark
  reference exactly): the user's v17 direction settled it in favor of
  restoring it.
- **Brightest gold face + a soft bloom** (`stickyon` asset) = caps-lock
  engaged — brighter than every other key's face and the only key with a
  colored bloom bleeding past its rim, deliberately, so the locked state is
  unmistakable at a glance. Confirmed as the real caps-lock-locked visual
  state, not just an icon change — see `docs/THEME-FORMAT.md`'s `stickyon`
  entry.
- **True rust face + a modest bloom** = the `action` (enter) key —
  distinct from every other key's orange/gold, matching the v17 reference
  SVG's rust-red enter key exactly.
- **v12 mechanical-keyboard pass:** `gap` raised from `1` to `1.5` on every
  border asset (uniformly, so spacing stays even) to expose more
  background between keys — the single highest-leverage move in the
  mechanical guide. The dish/rim-highlight/shadow rendering was redone
  with a crisper, less-blurred highlight and a per-row gamma curve on the
  dish gradient (steeper on `row 0`, gentler on `row 2`) as a row-profile
  cue, and the spacebar got two subtle stabilizer-stem dimples.
- **v13 dish-squeeze fix:** the v12 keycap dish looked fine on every asset
  PNG viewed in isolation but rendered as a thin vertical sliver once
  actually imported and rendered as a real (non-square) key — see the bug
  entry below. Fixed by raising `target_density` from `480` to `640` on
  every border and icon asset (kept in sync, as before) — a pure
  `theme.txt` edit, no art regeneration needed.
- **v14 redesign — dark brushed-charcoal keycaps with an underglow,
  replacing the v12/v13 solid-color-ring look entirely.** Prompted by a
  reference mockup the user shared (a gaming-style keyboard: charcoal
  keycaps with visible brushed-metal texture, color expressed as a glow
  bleeding from under each key rather than filling the whole border, one
  key shown dramatically lit). The old `stickyon` "deliberately flat, no
  dish" design (see earlier versions of this doc) was replaced by that same
  reference: `stickyon` now gets a real dish like every other key, just
  with a much bigger/brighter glow — a "lit dish" reads as more clearly
  "on" than a flat color block, and matches the mockup's single glowing
  key directly. Per the user's standing instruction, every glow/tint color
  is still one of Groovy Code's own seven palette colors — nothing from the
  reference image's teal/purple/blue was borrowed; only the *technique*
  (dark cap + colored glow instead of solid ring) came from it. Technical
  notes: brushed-metal texture is directional (mostly-horizontal-blurred)
  noise built with numpy for speed/correctness — a pure-Python per-pixel
  version was tried first and had a silent near-zero-variance bug, worth
  remembering if you're tempted to hand-loop pixel-level image ops again.
  See `scripts/generate_assets.py` for the full technique
  (`make_brushed_texture`, `draw_bottom_glow`).

- **v16 — three procedural realism cues added, no new reference image
  this round.** The user asked to push the existing Pillow rendering
  toward photo-realism rather than sourcing an actual keycap image
  asset. Added in `render_key` (`scripts/generate_assets.py`):
  `apply_vignette` (numpy radial falloff, brighter up-and-left of center
  like a product photo lit from above, darker toward corners),
  `draw_edge_ao` (a thin blurred stroke just inside the rounded
  silhouette — the contact-shadow cue for where a keycap's flat top
  meets its side bevel, missing entirely before this), and
  `draw_specular` (a small tight bright ellipse, offset off-center,
  distinct from the broad gradient sheen v15 already had). All three are
  composited onto the full canvas rectangle (not clipped to the rounded
  mask individually) and clipped once at the very end of `render_key` —
  cheaper than re-clipping after every layer. Confirmed via
  `preview-theme` that glyph legibility isn't hurt by the highlight.
- **v15 redesign — the user said v14 "doesn't look like a mechanical
  keyboard," and a close-up photo of a real one they shared showed exactly
  why.** Three misses, in order of how much they mattered: (1) v14's glow
  filled roughly half the dish on *every single key* — the reference shows
  color as a small, tight, bright point of light right at the bottom edge,
  and only on a handful of keys (the number row, one demo key); most keys
  have no glow at all at rest. (2) v14 kept the v10-era "outer ring +
  inset dish + crisp highlight line" structure — the reference has no
  such split at all, just one continuous surface with a soft top-lit
  sheen. (3) v14's `gap = 1.5` was much wider than the thin seams in the
  reference. Fixed all three: `render_key` in `scripts/generate_assets.py`
  now renders a single gradient+texture surface with no dish/highlight
  objects, `draw_edge_light` replaces `draw_bottom_glow` with a small
  ellipse clipped tightly to the bottom edge (most keys pass
  `glow_color=None` and get no light at all), and `gap` dropped to `1.15`
  in `theme.txt`. Row-banding and the gold "system key" tint are now
  genuinely subtle (`tint_amount` down from ~0.14-0.30 to ~0.05-0.10) —
  intentional, to match the reference, but flagged in "Open items" below
  since it trades away a usability cue the theme used to have. As
  before, confirmed via `preview-theme`, not a real device yet.

- **v17 — reverted to solid colorful keys, replacing v15/v16's dark
  charcoal look entirely.** Prompted by a new reference: an SVG
  illustration of a mechanical keyboard with solid orange keycaps, a gold
  rim, a visible inset face on *every* key (not just system keys), and a
  rust-red enter key — a fundamentally different direction from v15/v16's
  dark-surface-plus-tiny-glow look. Rather than guess a fourth time on a
  subjective visual target (this repo's own stated lesson, see the v14/v15
  history above), the user was asked directly: keep v16's dark look, blend
  (dark keys with a visible rim/inset), or go back to solid colorful keys.
  **They chose reverting to solid colorful keys.** Implemented in
  `scripts/generate_assets.py`'s rewritten `render_key`: every key is now a
  brown (`#874725`) outer "well" body with a bright inset face offset in
  from the edges (asymmetric margins — less at the sides/top, more at the
  bottom, matching the reference) and a thin gold (`#e19d25`) rim stroke
  right at that boundary. Row-banding was brought back as a *solid* color
  per row (not the reference's uniform orange) since it's this theme's own
  established signature and closer to the old v10–v13 look, which is what
  the user's chosen option explicitly referenced. The action/enter key
  uses true rust (`#bd361e`, distinct from the row2 asset's *brightened*
  rust) to match the reference's rust-red enter key exactly, and
  `stickyon` keeps the brightest gold face plus the biggest bloom, per the
  existing "gold = locked" convention. Every v14–v16 photo-realism
  technique — brushed-metal texture, vignette, edge ambient-occlusion, the
  small specular highlight — was **dropped, not kept alongside the new
  structure**: those were built for a dark, textured, photographic read,
  and fight against a flat, saturated, vector-style solid-color look like
  the new reference. This wasn't explicitly asked for by the user's answer
  (which was about color/structure, not the realism techniques
  specifically), so flag it if the intent was to layer realism cues onto
  the new solid-color faces rather than drop them — a judgment call, not a
  certainty. A subtle vertical gradient on the inset face (~15% lighter at
  top, ~18% darker at bottom) was kept for a small hint of keycap
  dimensionality without reintroducing the heavy texture. Confirmed via
  `preview-theme` on QWERTY, Symbols, and Numpad — row-banding, the gold
  rim, and the rust enter key all read correctly on all three. Not yet
  confirmed on a real device.

## Build workflow

Assets are generated with Python + Pillow (PIL), not hand-authored, via
`scripts/generate_assets.py` (`pip install pillow`) — run
`python3 scripts/generate_assets.py` from the repo root to regenerate all
16 non-icon `Button-*.png` border assets in place. Palette and geometry
constants live at the top of the script; the geometry constants
(radius/outline/canvas size) must match `theme.txt`'s `slicing` values (see
`docs/THEME-FORMAT.md`'s "Computing slicing values") if you change them.
As of v17 the script no longer needs numpy — the v14–v16 brushed-texture/
vignette/specular/edge-AO machinery was dropped along with the dark
charcoal look it served (see the v17 changelog entry below); rendering is
back to plain Pillow gradients and rounded-rect compositing. It
deliberately never touches `Icon-*.png`, `Button-morekey.png`, or
`Button-morekeysbox.png` — see the icon-regression bug below for why that
boundary is load-bearing, not incidental.

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
- **Dish squeezed to a sliver on real (non-square) keys (fixed v13):** the
  v12 border assets' `slicing` fractions (0.18 uniform) were computed
  assuming a square 160×160 key. A real rendered key measured out to
  roughly a 0.72 width:height ratio (noticeably taller than wide), and
  since a 9-patch's fixed margin is an *absolute on-screen size* regardless
  of the key's actual shape, that same margin ate a much bigger fraction of
  the narrower width than the taller height — the dish read as a thin
  vertical column instead of a proper keycap face. Invisible from any
  single asset PNG (which only shows the asset at its own square native
  resolution); only visible once actually imported and rendered as a real
  key — caught using the `preview-theme` skill (`.claude/skills/
  preview-theme/`), not a real device. See `docs/THEME-FORMAT.md`'s "The
  9-patch margin is a fixed on-screen size" for the full mechanism and the
  general fix.
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
format, (b) as of v13, rendering the theme for real with the
`preview-theme` skill (`.claude/skills/preview-theme/`) — which runs
`keyboard-theme-editor`'s actual rendering code locally via a headless
browser, not a real device — and (c) testing on a real device and
comparing a screenshot. (b) is what caught the v13 dish-squeeze bug that
(a) alone had missed for two versions; (c) is still the only way to check
real screen color/gamma, actual pressed/sticky-state interaction, and
`morekeysbox`/`morekey` (the editor's own preview stubs long-press to
always-false). **Don't declare a visual fix correct on the strength of (a)
alone if (b) is available, and don't call it fully confirmed without (c)
eventually happening.**

## Open items / not yet done

- **Whether to layer the v14–v16 photo-realism techniques back onto the
  v17 solid-color faces is an open judgment call, not something the user
  explicitly decided.** v17 dropped brushed texture/vignette/specular/edge
  ambient-occlusion entirely because they fought against a flat, saturated
  look — but the user's chosen option was about color/structure
  ("solid colorful keys"), not explicitly about the realism techniques.
  If a future round wants some photo-realism back (e.g. just a subtle
  texture on the inset face, keeping the flat gold rim crisp), that's a
  reasonable middle ground worth asking about rather than assuming either
  way.
- ~15 other confirmed real icon IDs are unused (settings, numpad, undo,
  chevron_right, previous_key, etc. — full list in
  `docs/THEME-FORMAT.md`) — only the ones with a clear coding-relevant use
  case (tab, cursor arrows, globe, mic) have been wired up so far.
- `morekeysbox`/`morekey` (long-press accent popup) styling was added but
  never confirmed on a real device — the editor's own JS preview stubs
  these to always-false, so it can only be verified in the real Android
  app. They also weren't restyled for the v17 look (still the old
  gold-ring style from v11) since they can't be previewed to check the
  result — low priority, since they're only visible during a long-press.
- v11 through v17 have all been checked with the `preview-theme` skill's
  real render but **none of them have been screenshotted/confirmed on a
  real device yet** — that's the immediate next verification step. Real
  screen color/gamma and actual touch/pressed-state interaction still
  can't be checked any other way.
- The background (`GroovyCode-background.png`) is still the original plain
  dark texture, untouched through v17 — a first attempt at a brushed-plate
  background (pure Pillow, no numpy) had a near-zero-variance bug and was
  abandoned when the v14 mockup redirected effort toward the keycaps
  instead. Revisit only if the plain background still looks flat next to
  the now much more colorful keycaps once seen on a real device.
