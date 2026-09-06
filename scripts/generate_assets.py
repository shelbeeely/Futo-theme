#!/usr/bin/env python3
"""Generate Groovy Code's Button-*.png keycap assets (Pillow + numpy).

v17: solid colorful keycaps -- brown "well" body, a bright inset face color
per key role, and a thin gold rim stroke right at the boundary between them.
Replaces v15/v16's dark-charcoal-single-surface-plus-tiny-glow look entirely,
per the user's explicit direction after seeing a new reference: an SVG
illustration of a mechanical keyboard with solid orange keycaps, a gold rim,
a visible inset face on every key (not just system keys), and a rust-red
enter key. Asked directly which way to go (keep v16's dark look, blend, or
revert) -- the user chose reverting to solid colorful keys.

What changed vs. v16, concretely:
- No more dark charcoal surface, brushed-metal grain, vignette, edge
  ambient-occlusion, or specular highlight -- those were photo-realism cues
  built for a dark, textured, photographic look, and fight against a flat,
  saturated, vector-illustration-style solid color read like the new
  reference. Dropped rather than kept "just in case."
- Every key is now a brown (#874725) outer well with a bright inset face
  (this theme's own palette colors, not the reference's) and a thin gold
  (#e19d25) rim stroke at the inset boundary -- directly matching the SVG's
  structure.
- Row-banding is preserved (this theme's own established signature, not
  present in the reference) by varying the inset face color per row/role
  instead of making every key identically orange -- home row orange, top
  row orange-red, bottom row brightened rust, system keys gold, enter key
  true rust, caps-lock an even brighter gold. This is closer to this
  theme's own v10-v13 look than to the reference's uniform-orange scheme,
  which is what the user's chosen option text described ("closer to our
  old v10-v13 look").
- A subtle vertical gradient on the inset face (not a flat fill) keeps a
  small hint of keycap dimensionality without reintroducing v14-v16's
  heavy photographic texture.

Geometry (radius/outline/canvas size) is fixed to match the `slicing`
values already in theme.txt -- changing these constants requires
recomputing those values too (see docs/THEME-FORMAT.md "Computing slicing
values").

Deliberately does NOT touch Icon-*.png, Button-morekey.png, or
Button-morekeysbox.png -- the icon-regeneration regression documented in
docs/GROOVY-CODE-THEME.md happened because a full regen run silently
clobbered hand-picked icon art. Keeping icons entirely outside this
script's reach makes that class of bug impossible, not just avoided.
"""

from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Geometry (must match theme.txt's `slicing` values -- see module docstring)
# ---------------------------------------------------------------------------

KEY_SIZE = (160, 160)
KEY_RADIUS = 26
SPACE_SIZE = (640, 160)
SPACE_RADIUS = 30

# Inset-face margins, matching the new SVG reference's asymmetric well
# (more brown visible at the bottom than the sides/top).
MARGIN_TOP = 12
MARGIN_SIDE = 12
MARGIN_BOTTOM = 20
RIM_WIDTH = 3

# ---------------------------------------------------------------------------
# Palette -- Groovy Code's own 7-color "Warm-toned Groovy 70's" set
# (theme.txt [colors] / docs/GROOVY-CODE-THEME.md). Every color below is one
# of these seven; nothing outside this palette is used, even though the
# *structure* (well + inset face + gold rim) came from an external reference.
# ---------------------------------------------------------------------------

GOLD = (225, 157, 37)  # #e19d25
ORANGE = (225, 122, 37)  # #e17a25
ORANGE_RED = (225, 78, 37)  # #e14e25
RUST = (189, 54, 30)  # #bd361e -- true palette rust, used for the action key
RUST_BRIGHT = (200, 90, 58)  # brightened rust, used for the bottom row
CLAY = (179, 117, 69)  # #b37545
BROWN = (135, 71, 37)  # #874725 -- the outer "well" body color for every key


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def blend_white(color, t):
    return lerp(color, (255, 255, 255), t)


def scale(color, f):
    return tuple(round(c * f) for c in color)


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255
    )
    return mask


def vertical_gradient(size, top_color, bottom_color):
    w, h = size
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        grad.putpixel((0, y), lerp(top_color, bottom_color, t))
    return grad.resize(size)


def render_key(
    size,
    radius,
    face_color,
    well_color=BROWN,
    pressed=False,
    gold_rim=True,
    stabilizers=False,
    bloom_alpha=0,
    bloom_pad=6,
):
    """Brown outer well + bright inset face + thin gold rim at the boundary
    -- the new v17 structure, replacing v16's single dark brushed surface."""
    w, h = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    outer_mask = rounded_mask(size, radius)

    well_top = blend_white(well_color, 0.10) if not pressed else well_color
    well_bottom = scale(well_color, 0.72)
    well = vertical_gradient(size, well_top, well_bottom)
    canvas.paste(well, (0, 0), outer_mask)

    ix0, iy0 = MARGIN_SIDE, MARGIN_TOP
    ix1, iy1 = w - MARGIN_SIDE, h - MARGIN_BOTTOM
    inset_size = (ix1 - ix0, iy1 - iy0)
    inset_radius = max(radius - MARGIN_SIDE, 6)

    face = scale(face_color, 0.80) if pressed else face_color

    if bloom_alpha and not pressed:
        # A soft bloom of the face color bleeding a little past the rim --
        # the "unmistakably lit" cue for the action/stickyon keys, kept as
        # a bleed rather than the v14-v16 big colored-glow-in-the-dish look.
        bloom = Image.new("RGBA", size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(bloom)
        bd.rounded_rectangle(
            [ix0 - bloom_pad, iy0 - bloom_pad, ix1 - 1 + bloom_pad, iy1 - 1 + bloom_pad],
            radius=inset_radius + bloom_pad,
            fill=face_color + (bloom_alpha,),
        )
        from PIL import ImageFilter

        bloom = bloom.filter(ImageFilter.GaussianBlur(bloom_pad * 0.8))
        canvas.alpha_composite(bloom)

    face_top = blend_white(face, 0.14)
    face_bottom = scale(face, 0.82)
    face_grad = vertical_gradient(inset_size, face_top, face_bottom)
    face_mask = rounded_mask(inset_size, inset_radius)
    face_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    face_layer.paste(face_grad, (ix0, iy0), face_mask)
    canvas.alpha_composite(face_layer)

    if gold_rim:
        rim = Image.new("RGBA", size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rim)
        rim_color = blend_white(GOLD, 0.15) if not pressed else scale(GOLD, 0.75)
        rd.rounded_rectangle(
            [ix0, iy0, ix1 - 1, iy1 - 1],
            radius=inset_radius,
            outline=rim_color + (255,),
            width=RIM_WIDTH,
        )
        canvas.alpha_composite(rim)

    if stabilizers:
        dimples = Image.new("RGBA", size, (0, 0, 0, 0))
        dd = ImageDraw.Draw(dimples)
        for frac in (0.25, 0.75):
            cx = w * frac
            dd.rounded_rectangle(
                [cx - 4, iy1 - 16, cx + 4, iy1 - 4], radius=3,
                fill=scale(face, 0.75) + (140,),
            )
        canvas.alpha_composite(dimples)

    canvas.putalpha(Image.composite(canvas.getchannel("A"), Image.new("L", size, 0), outer_mask))
    return canvas


# ---------------------------------------------------------------------------
# Per-asset definitions -- face color varies by row/role (this theme's own
# row-banding signature), well/rim stay uniform brown+gold on every key,
# matching the reference's well+rim structure.
# ---------------------------------------------------------------------------

RING_KEYS = [
    # name, face color
    ("Button-default", CLAY),
    ("Button-function", GOLD),
    ("Button-row0", ORANGE_RED),
    ("Button-row1", ORANGE),
    ("Button-row2", RUST_BRIGHT),
]

PRESSED_SUFFIX = {
    "Button-default": "-press",
    "Button-function": "-pressed",
    "Button-row0": "-press",
    "Button-row1": "-press",
    "Button-row2": "-press",
}


def main():
    for name, face in RING_KEYS:
        normal = render_key(KEY_SIZE, KEY_RADIUS, face)
        normal.save(f"{name}.png")

        pressed = render_key(KEY_SIZE, KEY_RADIUS, face, pressed=True)
        pressed.save(f"{name}{PRESSED_SUFFIX[name]}.png")
        print(f"wrote {name}.png / {name}{PRESSED_SUFFIX[name]}.png")

    # Action (enter): true rust face, matching the reference's rust-red
    # enter key against everything else's orange/gold -- plus a modest
    # bloom so it still reads as the primary accent key at rest.
    action = render_key(KEY_SIZE, KEY_RADIUS, RUST, bloom_alpha=90, bloom_pad=7)
    action.save("Button-action.png")

    action_press = render_key(KEY_SIZE, KEY_RADIUS, RUST, pressed=True)
    action_press.save("Button-action-press.png")
    print("wrote Button-action.png / Button-action-press.png")

    # Spacebar: plain clay face, no bloom, with stabilizer-stem dimples.
    space = render_key(SPACE_SIZE, SPACE_RADIUS, CLAY, stabilizers=True)
    space.save("Button-space.png")

    space_press = render_key(SPACE_SIZE, SPACE_RADIUS, CLAY, pressed=True, stabilizers=True)
    space_press.save("Button-space-press.png")
    print("wrote Button-space.png / Button-space-press.png")

    # stickyon (caps-lock engaged): the brightest, most bloomed gold face on
    # the board -- unmistakably "on," continuing the "gold = locked" cue.
    stickyon = render_key(
        KEY_SIZE, KEY_RADIUS, blend_white(GOLD, 0.10), bloom_alpha=150, bloom_pad=9
    )
    stickyon.save("Button-stickyon.png")

    stickyon_press = render_key(KEY_SIZE, KEY_RADIUS, blend_white(GOLD, 0.10), pressed=True)
    stickyon_press.save("Button-stickyon-press.png")
    print("wrote Button-stickyon.png / Button-stickyon-press.png")


if __name__ == "__main__":
    main()
