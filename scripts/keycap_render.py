"""Shared keycap rendering primitives (Pillow only, no numpy).

Extracted from generate_assets.py's v17 "well + inset face + gold rim"
render_key so the same rendering code can be reused across Groovy Code
itself and the classic-keyboard variant themes in variants/ (see
scripts/generate_variants.py) -- same structure, different colors, rather
than duplicating the function per theme.

Geometry (KEY_SIZE/KEY_RADIUS/SPACE_SIZE/SPACE_RADIUS/margins) is shared
across every theme that uses this module: it must match the `slicing`
values in each theme's theme.txt (see docs/THEME-FORMAT.md "Computing
slicing values"). Colors are NOT shared -- every caller passes its own
face/well/rim/legend colors.
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
):
    """Brown-well-style structure: outer well body + bright inset face +
    thin rim stroke at the boundary. `rim_color`/`well_color` are explicit
    per caller -- this is shared across differently-colored themes, so
    there's no sane universal default. `bloom_color` defaults to
    `face_color` when omitted (matches Groovy Code v17's original
    behavior, where the bloom is just the face color bleeding past the
    rim); pass it explicitly when the glow should differ from the face
    itself (e.g. an amber glow on an otherwise near-black face)."""
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
        rim_draw_color = blend_white(rim_color, 0.15) if not pressed else scale(rim_color, 0.75)
        rd.rounded_rectangle(
            [ix0, iy0, ix1 - 1, iy1 - 1],
            radius=inset_radius,
            outline=rim_draw_color + (255,),
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
