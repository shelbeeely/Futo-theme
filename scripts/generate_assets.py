#!/usr/bin/env python3
"""Generate Groovy Code's Button-*.png keycap assets (Pillow).

Renders a mechanical-keycap silhouette per key: an outer colored "sidewall"
ring (the row/role border color) plus an inset "dish" with a top-to-bottom
brightness falloff, a crisp rim highlight along the dish's top edge, and a
tight contact shadow along its bottom edge. Same approach documented in
docs/MECHANICAL-KEYBOARD-GUIDE.md and docs/GROOVY-CODE-THEME.md.

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

from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# Geometry (must match theme.txt's `slicing` values -- see module docstring)
# ---------------------------------------------------------------------------

KEY_SIZE = (160, 160)
KEY_RADIUS = 26
SPACE_SIZE = (640, 160)
SPACE_RADIUS = 30
OUTLINE = 3  # ring thickness; inset = radius + outline

# ---------------------------------------------------------------------------
# Palette (from theme.txt [colors] / docs/GROOVY-CODE-THEME.md design system)
# ---------------------------------------------------------------------------

GOLD = (225, 157, 37)
ORANGE = (225, 122, 37)
ORANGE_RED = (225, 78, 37)
RUST_BRIGHT = (200, 90, 58)  # brightened rust, not raw palette rust
CLAY = (179, 117, 69)

# Fixed dark "keycap body" anchors for ring-style keys (default/functional/
# row-banded) -- the dish darkens toward black regardless of ring color.
DARK_TOP = (46, 26, 17)
DARK_BOTTOM = (16, 8, 5)
DARK_TOP_PRESSED = (100, 54, 28)
DARK_BOTTOM_PRESSED = (64, 34, 17)

HIGHLIGHT = (245, 232, 208)  # crisp rim-highlight color (near on_background)
SHADOW = (0, 0, 0)

STICKYON_FILL = tuple(round(c * 0.53) for c in GOLD)


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


def dish_gradient(size, top_color, bottom_color, gamma):
    """Vertical gradient; gamma < 1 biases bright longer (steep late drop,
    used for top-row keys), gamma > 1 biases the falloff earlier/gentler
    (used for bottom-row keys) -- the row-profile cue from the mechanical
    guide, done as a brightness curve rather than moved geometry so 9-patch
    scaling stays safe."""
    w, h = size
    grad = Image.new("RGB", size)
    px = grad.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        t = t ** gamma
        col = lerp(top_color, bottom_color, t)
        for x in range(w):
            px[x, y] = col
    return grad


def draw_rim_and_shadow(base, inset_box, radius):
    """Crisp highlight line along the dish's top edge, tight shadow line
    along its bottom edge -- harder-edged than a soft ambient glow, per
    docs/MECHANICAL-KEYBOARD-GUIDE.md's PBT/ABS bevel note."""
    x0, y0, x1, y1 = inset_box
    draw = ImageDraw.Draw(base, "RGBA")
    inner_margin = max(radius // 2, 6)

    highlight_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight_layer)
    hd.line(
        [(x0 + inner_margin, y0 + 2), (x1 - inner_margin, y0 + 2)],
        fill=HIGHLIGHT + (150,),
        width=2,
    )
    highlight_layer = highlight_layer.filter(ImageFilter.GaussianBlur(0.6))
    base.alpha_composite(highlight_layer)

    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sd.line(
        [(x0 + inner_margin, y1 - 2), (x1 - inner_margin, y1 - 2)],
        fill=SHADOW + (100,),
        width=3,
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(1.2))
    base.alpha_composite(shadow_layer)
    del draw


def draw_stabilizer_dimples(base, inset_box):
    """Subtle stabilizer-stem hints at the 1/4 and 3/4 width marks, near the
    dish's base -- a cheap, recognizable spacebar detail no phone keyboard
    would have."""
    x0, y0, x1, y1 = inset_box
    w = x1 - x0
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for frac in (0.25, 0.75):
        cx = x0 + w * frac
        d.rounded_rectangle(
            [cx - 4, y1 - 26, cx + 4, y1 - 8], radius=3, fill=SHADOW + (55,)
        )
    layer = layer.filter(ImageFilter.GaussianBlur(1.5))
    base.alpha_composite(layer)


def render_key(
    size,
    radius,
    ring_color,
    dish_top,
    dish_bottom,
    gamma,
    filled=False,
    flat_fill=None,
    stabilizers=False,
):
    """filled=True -> ring color and dish share one hue family (action key).
    flat_fill -> stickyon: a single flat color, no dish/gradient/rim/shadow.
    """
    w, h = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))

    outer_mask = rounded_mask(size, radius)
    if flat_fill is not None:
        # stickyon: bright gold ring, flat darker-olive fill, no dish/rim/
        # shadow -- deliberately simple, see docstring below.
        body = Image.new("RGB", size, ring_color)
    else:
        # subtle top-lit sidewall gradient on the ring itself
        body = dish_gradient(size, blend_white(ring_color, 0.12), scale(ring_color, 0.85), 1.0)
    canvas.paste(body, (0, 0), outer_mask)

    inset = radius + OUTLINE
    inset_box = (inset, inset, w - inset, h - inset)
    inner_radius = max(radius - OUTLINE, 4)
    dish_size = (inset_box[2] - inset_box[0], inset_box[3] - inset_box[1])

    if flat_fill is not None:
        fill_mask = Image.new("L", size, 0)
        fill_mask.paste(rounded_mask(dish_size, inner_radius), (inset_box[0], inset_box[1]))
        fill_layer = Image.new("RGB", size, flat_fill)
        canvas.paste(fill_layer, (0, 0), fill_mask)
        return canvas

    dish_mask = Image.new("L", size, 0)
    dish_mask.paste(rounded_mask(dish_size, inner_radius), (inset_box[0], inset_box[1]))
    grad = dish_gradient(dish_size, dish_top, dish_bottom, gamma)
    dish_layer = Image.new("RGB", size, (0, 0, 0))
    dish_layer.paste(grad, (inset_box[0], inset_box[1]))
    canvas.paste(dish_layer, (0, 0), dish_mask)

    draw_rim_and_shadow(canvas, inset_box, radius)
    if stabilizers:
        draw_stabilizer_dimples(canvas, inset_box)

    return canvas


# ---------------------------------------------------------------------------
# Per-asset definitions: (filename, ring_color, dish_top, dish_bottom, gamma)
# gamma: <1 = top row (bright longer, steeper late falloff)
#         1 = home row / default baseline
#        >1 = bottom row (falls off earlier, gentler overall)
# ---------------------------------------------------------------------------

RING_KEYS = [
    ("Button-default", CLAY, DARK_TOP, DARK_BOTTOM, 1.0),
    ("Button-function", GOLD, DARK_TOP, DARK_BOTTOM, 1.0),
    ("Button-row0", ORANGE_RED, DARK_TOP, DARK_BOTTOM, 0.72),
    ("Button-row1", ORANGE, DARK_TOP, DARK_BOTTOM, 1.0),
    ("Button-row2", RUST_BRIGHT, DARK_TOP, DARK_BOTTOM, 1.35),
]

PRESSED_SUFFIX = {
    "Button-default": "-press",
    "Button-function": "-pressed",
    "Button-row0": "-press",
    "Button-row1": "-press",
    "Button-row2": "-press",
}


def main():
    for name, ring, dtop, dbot, gamma in RING_KEYS:
        normal = render_key(KEY_SIZE, KEY_RADIUS, ring, dtop, dbot, gamma)
        normal.save(f"{name}.png")

        pressed_ring = blend_white(ring, 0.3)
        pressed = render_key(
            KEY_SIZE, KEY_RADIUS, pressed_ring, DARK_TOP_PRESSED, DARK_BOTTOM_PRESSED, gamma
        )
        pressed.save(f"{name}{PRESSED_SUFFIX[name]}.png")
        print(f"wrote {name}.png / {name}{PRESSED_SUFFIX[name]}.png")

    # Action (enter) key: filled with the orange hue family, home-row-like
    # gamma, slightly wider top/bottom contrast for more pop on the primary
    # accent key.
    action_dish_top = scale(ORANGE, 0.70)
    action_dish_bottom = scale(ORANGE, 0.40)
    action = render_key(KEY_SIZE, KEY_RADIUS, ORANGE, action_dish_top, action_dish_bottom, 1.0)
    action.save("Button-action.png")

    action_press_ring = blend_white(ORANGE, 0.35)
    action_press_top = blend_white(ORANGE, 0.15)
    action_press_bottom = scale(ORANGE, 0.55)
    action_press = render_key(
        KEY_SIZE, KEY_RADIUS, action_press_ring, action_press_top, action_press_bottom, 1.0
    )
    action_press.save("Button-action-press.png")
    print("wrote Button-action.png / Button-action-press.png")

    # Spacebar: home-row-like gamma, plus stabilizer dimples.
    space = render_key(
        SPACE_SIZE, SPACE_RADIUS, CLAY, DARK_TOP, DARK_BOTTOM, 1.0, stabilizers=True
    )
    space.save("Button-space.png")

    space_press_ring = blend_white(CLAY, 0.3)
    space_press = render_key(
        SPACE_SIZE,
        SPACE_RADIUS,
        space_press_ring,
        DARK_TOP_PRESSED,
        DARK_BOTTOM_PRESSED,
        1.0,
        stabilizers=True,
    )
    space_press.save("Button-space-press.png")
    print("wrote Button-space.png / Button-space-press.png")

    # stickyon: deliberately flat, no dish -- see docs/GROOVY-CODE-THEME.md
    # ("Solid gold fill = caps-lock engaged"), an unambiguous locked-state
    # indicator, not a keycap dish.
    stickyon = render_key(KEY_SIZE, KEY_RADIUS, GOLD, None, None, 1.0, flat_fill=STICKYON_FILL)
    stickyon.save("Button-stickyon.png")

    stickyon_press_ring = blend_white(GOLD, 0.3)
    stickyon_press = render_key(
        KEY_SIZE, KEY_RADIUS, stickyon_press_ring, None, None, 1.0, flat_fill=STICKYON_FILL
    )
    stickyon_press.save("Button-stickyon-press.png")
    print("wrote Button-stickyon.png / Button-stickyon-press.png")


if __name__ == "__main__":
    main()
