"""Procedural, per-variant icon rendering.

FUTO always force-recolors every icon at runtime (`drawTintedImage` in
`keyboard-theme-editor`'s `render.ts` uses canvas `source-in` compositing,
keyed on the theme's foreground color for that key state) -- only each
icon's ALPHA-CHANNEL SHAPE ever reaches the screen, never any RGB baked
into the PNG (see CLAUDE.md fact #3). Groovy Code and, before this
module existed, every classic-hardware variant all shared FUTO's own
official icon SVGs -- rasterized once, copied byte-identical into every
theme. That was a deliberate choice (matching FUTO's own iconography kept
these instantly recognizable, and fixed a real v10 regression where
hand-drawn icons had clobbered the official ones) but it also means the
8 variants were never actually "separate themes" for this one asset
class -- they all shipped the identical 10 files.

The user asked for every variant to have its own icons, no shared
assets. Since RGB is moot (see above), the only lever left for a
per-variant icon IDENTITY is silhouette: stroke weight, corner style
(sharp vs. round joins/caps), and an optional pixel-grid quantization for
the variants built around a pixel-art-era font. Every function below
draws the same real, recognizable glyph FUTO's own SVG depicts for that
role (a delete-key outline with an X, an up-arrow merged into a bar for
shift, a bent arrow for enter, etc.) -- this is a restyling of HOW each
icon is drawn, not a redesign of WHAT it communicates, so every variant's
keyboard stays legible by the same visual vocabulary a FUTO user already
knows.
"""

import io
import os
import re

from PIL import Image, ImageDraw

ICON_SIZE = (288, 288)

# vendor/tabler-icons/icons/outline -- real, MIT-licensed source SVGs used
# by render_svg_icon() below for the handful of icons sourced from a real
# brand mark or device glyph instead of drawn procedurally (see
# docs/VARIANTS.md's action_emoji entry). Path is relative to this file so
# it resolves regardless of the caller's own cwd.
TABLER_ICONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "vendor", "tabler-icons", "icons", "outline",
)


def _rgba(color, alpha):
    return tuple(color) + (alpha,)


def _stroke(draw, points, width, color, alpha, rounded, closed=False):
    """Draw a (optionally closed) polyline stroke. `rounded` gives round
    joints/caps (matching FUTO's own icons); otherwise joints are left
    sharp/butt, for a more technical, blocky look."""
    pts = list(points) + ([points[0]] if closed else [])
    fill = _rgba(color, alpha)
    if len(pts) > 1:
        draw.line(pts, fill=fill, width=max(1, width), joint="curve" if rounded else None)
    if rounded:
        r = width / 2
        for (x, y) in pts:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def _pixelate(img, grid):
    """Quantize to a coarse grid (area-averaged down, nearest-neighbor
    back up) for a blocky pixel-art look -- used by variants built around
    a pixel-grid-era font (DotGothic16, Press Start 2P, Sixtyfour, VT323,
    Pixelify Sans). `grid` is the number of blocks across the icon's
    shorter side; None/0 skips this entirely."""
    if not grid:
        return img
    w, h = img.size
    gw, gh = max(1, w // grid), max(1, h // grid)
    small = img.resize((gw, gh), Image.BOX)
    return small.resize((w, h), Image.NEAREST)


def render_icon(draw_fn, size=ICON_SIZE, color=(255, 255, 255), alpha=255,
                 stroke_frac=0.06, rounded=True, pixel_grid=None, **kwargs):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    sw = max(2, round(min(w, h) * stroke_frac))
    draw_fn(draw, w, h, sw, color, alpha, rounded, **kwargs)
    return _pixelate(img, pixel_grid)


def render_svg_icon(svg_filename, size=ICON_SIZE, stroke_frac=0.06, rounded=True,
                     pixel_grid=None, icons_dir=TABLER_ICONS_DIR):
    """Rasterize a real vendored SVG icon (Tabler Icons, MIT) into this
    theme's icon canvas, restyled with the same stroke-weight/joint/
    pixel-grid knobs the procedural glyphs above use -- so a real sourced
    icon still carries its own variant's silhouette identity instead of
    Tabler's fixed default stroke weight. Only works for outline-style
    SVGs built the way every icon in vendor/tabler-icons/icons/outline is:
    a 24x24 viewBox, `stroke="currentColor"`, `stroke-width="2"`. Only the
    resulting alpha shape ever reaches the screen (FUTO force-recolors
    every icon at render time, see CLAUDE.md fact #3), so no fill color
    handling is needed here.
    """
    import cairosvg

    w, h = size
    sw = max(2, round(min(w, h) * stroke_frac))
    # Tabler's outline SVGs use a 24-unit viewBox at stroke-width 2 --
    # convert the target pixel stroke width back into viewBox units so the
    # rasterized icon comes out at the same effective weight as this same
    # set's procedurally-drawn icons.
    viewbox_stroke = sw / (min(w, h) / 24)
    linecap = "round" if rounded else "butt"
    linejoin = "round" if rounded else "miter"

    with open(os.path.join(icons_dir, svg_filename)) as f:
        svg_text = f.read()
    svg_text = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{viewbox_stroke}"', svg_text)
    svg_text = re.sub(r'stroke-linecap="[^"]*"', f'stroke-linecap="{linecap}"', svg_text)
    svg_text = re.sub(r'stroke-linejoin="[^"]*"', f'stroke-linejoin="{linejoin}"', svg_text)

    png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"),
                                  output_width=w, output_height=h)
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    return _pixelate(img, pixel_grid)


# ---------------------------------------------------------------------------
# Icon glyphs -- signature (draw, w, h, stroke_width, color, alpha, rounded)
# ---------------------------------------------------------------------------

def icon_backspace(draw, w, h, sw, color, alpha, rounded):
    tip = (0.12 * w, 0.50 * h)
    body = [
        tip,
        (0.32 * w, 0.24 * h),
        (0.82 * w, 0.24 * h),
        (0.82 * w, 0.76 * h),
        (0.32 * w, 0.76 * h),
    ]
    _stroke(draw, body, sw, color, alpha, rounded, closed=True)
    _stroke(draw, [(0.46 * w, 0.37 * h), (0.66 * w, 0.63 * h)], sw, color, alpha, rounded)
    _stroke(draw, [(0.66 * w, 0.37 * h), (0.46 * w, 0.63 * h)], sw, color, alpha, rounded)


def _shift_points(w, h):
    return [
        (0.18 * w, 0.52 * h),
        (0.50 * w, 0.14 * h),
        (0.82 * w, 0.52 * h),
        (0.64 * w, 0.52 * h),
        (0.64 * w, 0.84 * h),
        (0.36 * w, 0.84 * h),
        (0.36 * w, 0.52 * h),
    ]


def icon_shift(draw, w, h, sw, color, alpha, rounded):
    _stroke(draw, _shift_points(w, h), sw, color, alpha, rounded, closed=True)


def icon_shift_press(draw, w, h, sw, color, alpha, rounded):
    draw.polygon(_shift_points(w, h), fill=_rgba(color, alpha))


def icon_enter(draw, w, h, sw, color, alpha, rounded):
    path = [(0.78 * w, 0.28 * h), (0.78 * w, 0.62 * h), (0.24 * w, 0.62 * h)]
    _stroke(draw, path, sw, color, alpha, rounded)
    left_end = path[-1]
    _stroke(draw, [(0.42 * w, 0.44 * h), left_end], sw, color, alpha, rounded)
    _stroke(draw, [(0.42 * w, 0.80 * h), left_end], sw, color, alpha, rounded)


def icon_globe(draw, w, h, sw, color, alpha, rounded):
    cx, cy = 0.5 * w, 0.5 * h
    r = 0.36 * min(w, h)
    fill = _rgba(color, alpha)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=sw)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=fill, width=sw)
    lens_w = r * 0.5
    draw.ellipse([cx - lens_w, cy - r, cx + lens_w, cy + r], outline=fill, width=sw)


def icon_mic(draw, w, h, sw, color, alpha, rounded):
    cx = 0.5 * w
    fill = _rgba(color, alpha)
    cap_r = 0.15 * min(w, h)
    cap_top, cap_bottom = 0.16 * h, 0.54 * h
    draw.rounded_rectangle([cx - cap_r, cap_top, cx + cap_r, cap_bottom], radius=cap_r, fill=fill)
    stand_r = cap_r * 1.55
    stand_cy = cap_bottom - cap_r * 0.25
    bbox = [cx - stand_r, stand_cy - stand_r * 0.7, cx + stand_r, stand_cy + stand_r * 1.1]
    draw.arc(bbox, start=0, end=180, fill=fill, width=sw)
    post_bottom = 0.82 * h
    draw.line([(cx, stand_cy + stand_r * 0.55), (cx, post_bottom)], fill=fill, width=sw)
    base_w = cap_r * 1.15
    draw.line([(cx - base_w, post_bottom), (cx + base_w, post_bottom)], fill=fill, width=sw)


def icon_tab(draw, w, h, sw, color, alpha, rounded):
    y = 0.5 * h
    tip = (0.62 * w, y)
    _stroke(draw, [(0.14 * w, y), tip], sw, color, alpha, rounded)
    _stroke(draw, [(0.48 * w, y - 0.16 * h), tip], sw, color, alpha, rounded)
    _stroke(draw, [(0.48 * w, y + 0.16 * h), tip], sw, color, alpha, rounded)
    bar_x = 0.82 * w
    draw.line([(bar_x, y - 0.28 * h), (bar_x, y + 0.28 * h)], fill=_rgba(color, alpha), width=sw)


def icon_arrow(draw, w, h, sw, color, alpha, rounded, direction="left"):
    y = 0.5 * h
    if direction == "left":
        tail_x, tip_x, back_x = 0.82 * w, 0.18 * w, 0.42 * w
    else:
        tail_x, tip_x, back_x = 0.18 * w, 0.82 * w, 0.58 * w
    tip = (tip_x, y)
    _stroke(draw, [(tail_x, y), tip], sw, color, alpha, rounded)
    _stroke(draw, [(back_x, y - 0.20 * h), tip], sw, color, alpha, rounded)
    _stroke(draw, [(back_x, y + 0.20 * h), tip], sw, color, alpha, rounded)


def icon_arrow_left(draw, w, h, sw, color, alpha, rounded):
    icon_arrow(draw, w, h, sw, color, alpha, rounded, direction="left")


def icon_arrow_right(draw, w, h, sw, color, alpha, rounded):
    icon_arrow(draw, w, h, sw, color, alpha, rounded, direction="right")


def icon_emoji(draw, w, h, sw, color, alpha, rounded):
    cx, cy = 0.5 * w, 0.5 * h
    r = 0.36 * min(w, h)
    fill = _rgba(color, alpha)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=sw)
    eye_r = max(2, sw * 0.6)
    for ex in (cx - r * 0.38, cx + r * 0.38):
        ey = cy - r * 0.10
        draw.ellipse([ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r], fill=fill)
    mouth_w = r * 0.48
    mouth_y = cy + r * 0.14
    bbox = [cx - mouth_w, mouth_y - mouth_w * 0.7, cx + mouth_w, mouth_y + mouth_w * 0.95]
    draw.arc(bbox, start=20, end=160, fill=fill, width=sw)


# Filename -> drawing function, for the generator to iterate over.
ICON_FUNCS = {
    "Icon-backspace.png": icon_backspace,
    "Icon-shift.png": icon_shift,
    "Icon-shift-press.png": icon_shift_press,
    "Icon-enter.png": icon_enter,
    "Icon-globe.png": icon_globe,
    "Icon-mic.png": icon_mic,
    "Icon-tab.png": icon_tab,
    "Icon-arrow-left.png": icon_arrow_left,
    "Icon-arrow-right.png": icon_arrow_right,
    "Icon-emoji.png": icon_emoji,
}


def render_icon_set(out_dir, stroke_frac=0.06, rounded=True, pixel_grid=None, save=True,
                     emoji_icon_svg=None):
    """Render all 10 icon files with one style into `out_dir`. Returns a
    dict of filename -> PIL.Image for callers that want them in memory.

    `emoji_icon_svg`, if given, is a filename in `vendor/tabler-icons/icons/
    outline` (e.g. "brand-apple.svg") rasterized via render_svg_icon() in
    place of the usual procedural smiley for Icon-emoji.png -- used to give
    a variant a real hardware-appropriate action_emoji glyph instead of a
    generic emoji face (see docs/VARIANTS.md's action_emoji entry).
    """
    images = {}
    for name, fn in ICON_FUNCS.items():
        if name == "Icon-emoji.png" and emoji_icon_svg:
            img = render_svg_icon(emoji_icon_svg, stroke_frac=stroke_frac,
                                   rounded=rounded, pixel_grid=pixel_grid)
        else:
            img = render_icon(fn, stroke_frac=stroke_frac, rounded=rounded, pixel_grid=pixel_grid)
        images[name] = img
        if save:
            img.save(os.path.join(out_dir, name))
    return images
