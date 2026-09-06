# Building a mechanical-keyboard-look theme

Notes for the next theme in this repo (or a variant of Groovy Code): making
FUTO Keyboard look like a real mechanical/desktop keyboard rather than a
generic soft-touch phone keyboard. Read `docs/THEME-FORMAT.md` first for
what fields exist; this is about which of those fields actually sell the
"mechanical keyboard" illusion, and which things a real mechanical keyboard
has that this format simply cannot do.

## What the format can't do — set expectations first

- **Row profile (Cherry/OEM sculpting) is not real 3D geometry here.** A
  real mechanical keyboard's rows are physically different heights/angles.
  FUTO themes only draw a flat PNG per key state — there's no per-row key
  *shape* or camera angle, only per-row *art*. You fake row-profile by
  varying the dish/bevel/shadow *painted into* each row's asset (see
  below), not by actually tilting anything.
- **Key geometry (size, row layout, gaps between rows) is controlled by the
  keyboard layout, not the theme.** `gap` (see `docs/THEME-FORMAT.md`) can
  shrink/grow how much of that fixed footprint your art fills, but you
  can't change which keys exist, their size ratios, or true row spacing.
- **One font for the whole theme** (`[options.font]`). Real mechanical
  keyboards often mix legend styles across rows/keycap sets — you can't do
  that here; pick one font that reads well at both letter and hint size.
- **No baked-in ambient occlusion between adjacent keys** — each key is
  rendered independently, so shadow one key casts onto its neighbor has to
  be faked by shrinking the key art via `gap` and letting a darker
  background/plate color show through the exposed margin, not by actually
  drawing a shadow that spans two keys' assets.

## What actually sells it

1. **Individual floating keycaps over a visible plate.** This is the single
   highest-leverage move. Set `gap` on your border assets to something
   *greater than the default `1`* on all four edges (shrinking the key art
   relative to its hit-box) and pair it with a background image that reads
   as a keyboard plate/PCB — brushed metal, matte black plastic, or a
   plate with switch cutouts — set via `[options.background]`. The
   exposed strip between keys becomes the "gap where you can see the
   plate," which is the single most recognizable visual signature of a
   mechanical keyboard vs. a phone keyboard's edge-to-edge key mat.
2. **Row-varying dish depth, not just row-varying color.** Groovy Code
   already proved the *multiplicative* darkening technique for the dish
   (72%→40% of base color, scaled by row/key brightness — see
   `docs/GROOVY-CODE-THEME.md`'s "Keycap dish contrast" bug). For a
   mechanical look, additionally vary the dish's *vertical offset* and rim
   highlight *position* per row to suggest the angled sculpt: top rows'
   dish/highlight sits lower in the key (as if you're looking down into a
   keycap angled away from you), bottom rows' sits higher. Even a few
   pixels of asymmetry per row reads as "these rows are sculpted
   differently" without needing true 3D.
3. **A harder, more saturated rim highlight + a tighter, darker cast
   shadow than Groovy Code's.** Real PBT/ABS keycaps have a crisp glossy
   highlight along one edge (usually top) from the injection-molded bevel,
   and a small hard-edged contact shadow at the base where the keycap meets
   the switch housing — sharper than a soft ambient shadow. Push rim
   highlight alpha higher and shadow blur radius lower than you would for a
   "soft" theme like Groovy Code.
4. **Legend authenticity.** Monospace/technical fonts (FiraCode, JetBrains
   Mono, a DIN-style geometric sans) read as "keycap legend" far more than
   a rounded UI font. If you want a shine-through/backlit-legend look,
   remember `foreground_tint` only sets label *color* — it can't add a
   glow, since the label is drawn fresh at render time on top of your
   border art. The closest approximation is a bright, slightly desaturated
   `foreground_tint` plus a dark key face, which reads as "lit from behind"
   even without an actual glow.
5. **A believable case bezel.** Use `[options.background].cropping` to
   crop your plate/case art tightly (Pet Keys crops to `[0.06, 0.06, 0.9,
   0.9]` rather than bleeding to the edges) so the visible background reads
   as a bounded case surface behind the keys, not an infinite tiled
   texture. A subtle screw-hole or brand-badge detail in the background
   image (well outside the key-covered area) sells "this is a keyboard
   case" cheaply.
6. **Spacebar stabilizer hint.** Real spacebars show two small stabilizer
   stems/wire dimples near the 1/4 and 3/4 width marks. A very subtle
   pair of vertical grooves at those x-positions in the spacebar art (not
   on letter keys) is a cheap, recognizable detail that a phone keyboard
   would never have.
7. **Per-switch-color banding, if you want a colorful board.** Real
   mechanical builds often color-code modifier/home/accent keys by switch
   or keycap set (e.g. novelty accent keys in a different colorway from the
   base set). This repo's row-banding approach in Groovy Code
   (`normal row 0/1/2`) generalizes directly: pick 2–4 accent colors and
   assign them via `row`/`rowmod`/`label` matchrules the same way, rather
   than inventing a new mechanism.
8. **Scattered novelty keycaps, if you want variety without a rule per
   key.** A real custom-keycap set often has a handful of novelty/artisan
   caps scattered around rather than uniform rows. `keyboard.futo.tech`'s
   Christmas 2025 theme does exactly this by combining `rowmod` and
   `colmod` in one selector (`normal rowmod 1 2 colmod 3 5`, see
   `docs/THEME-FORMAT.md`) to place its "bitten cookie" variant at a
   repeating-but-sparse set of positions instead of every key. The same
   technique works for scattering a distinct "novelty keycap" art variant
   (different legend style, an accent color, a printed icon) across a
   mechanical theme without hand-listing every affected key.
9. **A cleaner long-press popup.** If you want the popup accent keys to
   read as one smooth surface rather than a row of separately-outlined
   chips (closer to how a real keyboard has no equivalent UI at all),
   map `morekey` to a fully transparent asset (`slicing = [0, 0, 1, 1]`,
   otherwise blank) the way Christmas 2025 does, and let `morekeysbox`
   alone define the popup's outline.

## Suggested build approach

Reuse Groovy Code's generation approach (Python + Pillow, not hand-drawn
pixels — see `docs/GROOVY-CODE-THEME.md`'s "Build workflow") with these
parameter changes:

- Increase `gap` from `1` to something like `1.4–1.8` on all border assets
  so keys visually separate from each other.
- Author a plate/background PNG (brushed metal, PCB, or matte case texture)
  instead of a flat/soft gradient background, and crop it in from the
  edges via `cropping`.
- Generate dish/highlight with a **per-row vertical offset parameter**, not
  just per-row color, in whatever script replaces the missing generation
  script.
- Keep the same discipline this repo already follows: `background_tint =
  "#ffffff"` on every border asset so hand-painted shading survives
  (see `docs/THEME-FORMAT.md`), `padding = [0,0,0,0]` on any key with a
  letter/hint (previously-shipped bug, see `docs/GROOVY-CODE-THEME.md`),
  and don't declare a visual change "done" without a real device
  screenshot — the dish-contrast and icon-regression bugs in this repo's
  history were both only catchable that way.

## Reference points

- `keyboard.futo.tech/themes` (checked while writing this doc, and again
  when all four published/gallery themes — Pet Keys, Christmas 2025,
  OpenDyslexic, plus our own Groovy Code — were downloaded and compared)
  currently has no mechanical/keycap-styled theme in the gallery — this
  would be original ground, not a copy of an existing FUTO theme.
- Pet Keys (`p.trashkittyqueen.petkeys`, see `docs/THEME-FORMAT.md`) is the
  best real-world example of per-key one-off art layered over rule-based
  fallbacks, which is exactly the technique you'd use for
  novelty/accent keycaps in a mechanical theme (specific keys get distinct
  "keycap set" art via `label`/exact `row N col M` selectors, everything
  else falls through to the base row-banded asset).
- Christmas 2025 (`art.zilluzion.xmas2025`) is the best real-world example
  of a **sculpted, non-rectangular** key silhouette (its keys are rounded
  gingerbread-cookie shapes with a literal bite taken out of some of them)
  combined with a painterly illustrated background — proof that this
  format's border assets don't have to be simple rounded rectangles at
  all, which matters if you want a keycap silhouette with a distinct
  physical edge profile rather than just a rounded square.
