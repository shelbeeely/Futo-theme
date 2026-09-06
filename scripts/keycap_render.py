"""Shared keycap rendering primitives (Pillow only, no numpy).

Extracted from generate_assets.py's v17 "well + inset face + rim"
render_key so the same rendering code can be reused across Groovy Code
itself and the classic-hardware variant themes in variants/ (see
scripts/generate_variants.py) -- same underlying structure (an outer well
body, an inset face, a rim stroke at the boundary), but every geometry
knob (corner radius, bezel/margin thickness, rim weight, gradient
contrast) is a parameter, not a constant -- so each variant can have its
own material character (a chunky slab-sided Model M vs. a thin-bezel
glossy SNES button) instead of being Groovy Code's shape with new paint.
Colors are likewise never shared -- every caller passes its own
face/well/rim/legend colors.

KEY_SIZE/SPACE_SIZE (the canvas resolution assets are drawn at) ARE
shared -- they're just an internal art resolution, not anything the real
key's on-screen shape depends on. `radius`, by contrast, changes both the
drawn silhouette AND the `slicing` fraction a theme.txt needs (see
`compute_slicing` below and docs/THEME-FORMAT.md "Computing slicing
values") -- every caller using a non-default radius must recompute its
own slicing values, not reuse Groovy Code's 0.18/0.82.
"""

from PIL import Image, ImageDraw, ImageFilter

KEY_SIZE = (160, 160)
KEY_RADIUS = 26
SPACE_SIZE = (640, 160)
SPACE_RADIUS = 30

MARGIN_TOP = 12
MARGIN_SIDE = 12
MARGIN_BOTTOM = 20
RIM_WIDTH = 3

SLICING_OUTLINE = 3  # matches the safety margin baked into Groovy Code's own 0.18/0.052/0.206 values


def compute_slicing(radius, size, outline=SLICING_OUTLINE):
    """The 9-patch stretch boundary for a border asset of the given
    canvas `size` and corner `radius` -- generalizes the fixed formula
    Groovy Code's own theme.txt comments derive by hand (radius 26 on a
    160x160 key -> (26+3)/160 = 0.18). Returns [x0, y0, x1, y1] fractions
    ready to drop straight into a `slicing = [...]` line."""
    w, h = size
    fx = (radius + outline) / w
    fy = (radius + outline) / h
    return [round(fx, 4), round(fy, 4), round(1 - fx, 4), round(1 - fy, 4)]


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
    well_color,
    rim_color,
    pressed=False,
    gold_rim=True,
    stabilizers=False,
    bloom_alpha=0,
    bloom_pad=6,
    bloom_color=None,
    margin_top=MARGIN_TOP,
    margin_side=MARGIN_SIDE,
    margin_bottom=MARGIN_BOTTOM,
    rim_width=RIM_WIDTH,
    well_top_blend=0.10,
    well_bottom_scale=0.72,
    face_top_blend=0.14,
    face_bottom_scale=0.82,
    pressed_face_scale=0.80,
    rim_top_blend=0.15,
    rim_pressed_scale=0.75,
):
    """Well + inset face + rim -- the one structure every theme in this
    repo shares -- but every geometry/material knob defaults to Groovy
    Code v17's own original hardcoded values, so its calls (which pass
    none of these) render byte-identically. Variant themes override
    `margin_*`/`rim_width` for bezel thickness and `radius` for corner
    shape (material silhouette), and the `*_blend`/`*_scale` gradient
    knobs for how deep/flat/glossy the surface reads (material finish).
    `rim_color`/`well_color` are explicit per caller -- this is shared
    across differently-colored themes, so there's no sane universal
    default. `bloom_color` defaults to `face_color` when omitted (matches
    Groovy Code v17's original behavior, where the bloom is just the face
    color bleeding past the rim); pass it explicitly when the glow should
    differ from the face itself (e.g. an amber glow on an otherwise
    near-black face)."""
    w, h = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    outer_mask = rounded_mask(size, radius)

    well_top = blend_white(well_color, well_top_blend) if not pressed else well_color
    well_bottom = scale(well_color, well_bottom_scale)
    well = vertical_gradient(size, well_top, well_bottom)
    canvas.paste(well, (0, 0), outer_mask)

    ix0, iy0 = margin_side, margin_top
    ix1, iy1 = w - margin_side, h - margin_bottom
    inset_size = (ix1 - ix0, iy1 - iy0)
    inset_radius = max(radius - margin_side, 6)

    face = scale(face_color, pressed_face_scale) if pressed else face_color

    if bloom_alpha and not pressed:
        glow_color = bloom_color if bloom_color is not None else face_color
        bloom = Image.new("RGBA", size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(bloom)
        bd.rounded_rectangle(
            [ix0 - bloom_pad, iy0 - bloom_pad, ix1 - 1 + bloom_pad, iy1 - 1 + bloom_pad],
            radius=inset_radius + bloom_pad,
            fill=glow_color + (bloom_alpha,),
        )
        bloom = bloom.filter(ImageFilter.GaussianBlur(bloom_pad * 0.8))
        canvas.alpha_composite(bloom)

    face_top = blend_white(face, face_top_blend)
    face_bottom = scale(face, face_bottom_scale)
    face_grad = vertical_gradient(inset_size, face_top, face_bottom)
    face_mask = rounded_mask(inset_size, inset_radius)
    face_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    face_layer.paste(face_grad, (ix0, iy0), face_mask)
    canvas.alpha_composite(face_layer)

    if gold_rim:
        rim = Image.new("RGBA", size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rim)
        rim_draw_color = blend_white(rim_color, rim_top_blend) if not pressed else scale(rim_color, rim_pressed_scale)
        rd.rounded_rectangle(
            [ix0, iy0, ix1 - 1, iy1 - 1],
            radius=inset_radius,
            outline=rim_draw_color + (255,),
            width=rim_width,
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
