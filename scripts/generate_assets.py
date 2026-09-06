#!/usr/bin/env python3
"""Generate Groovy Code's Button-*.png keycap assets (Pillow + numpy).

v14: dark brushed-metal keycaps with a colored underglow, replacing the
v12/v13 solid-color-ring approach. Reference: a mockup the user shared of a
gaming-style keyboard -- charcoal keycaps with visible brushed texture,
color expressed as a soft glow bleeding from under each key rather than a
solid colored border, and one key shown dramatically lit (mapped onto our
`stickyon`/caps-lock state). Per the user's standing instruction, every
color used is still drawn from Groovy Code's own 7-color palette (the
"Warm-toned Groovy 70's" set, see docs/GROOVY-CODE-THEME.md) -- no colors
were borrowed from that reference image.

Per key: an outer body and inset "dish", both dark charcoal with a subtle
per-role tint and brushed-metal texture, a crisp rim highlight along the
dish's top edge, a tight contact shadow along its bottom edge, and a
soft colored glow pooling in the bottom portion of the dish (the role's
accent color -- gold=system, orange-red/orange/rust=row bands, orange=
action, brighter gold=stickyon). Documented in
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

import numpy as np
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
# Palette -- Groovy Code's own 7-color "Warm-toned Groovy 70's" set
# (theme.txt [colors] / docs/GROOVY-CODE-THEME.md). Every glow/tint below
# is one of these seven; nothing outside this palette is used.
# ---------------------------------------------------------------------------

GOLD = (225, 157, 37)  # #e19d25
ORANGE = (225, 122, 37)  # #e17a25
ORANGE_RED = (225, 78, 37)  # #e14e25
RUST_BRIGHT = (200, 90, 58)  # brightened #bd361e, see docs/GROOVY-CODE-THEME.md
CLAY = (179, 117, 69)  # #b37545
BROWN = (135, 71, 37)  # #874725
NEAR_BLACK = (66, 33, 24)  # #422118

# Dark charcoal keycap body, derived from the palette's own near-black
# (#422118) rather than a neutral gray, so the "dark" keys still read as
# part of this palette, not a generic gunmetal.
DARK_TOP = (46, 26, 17)
DARK_BOTTOM = (16, 8, 5)
DARK_TOP_PRESSED = (100, 54, 28)
DARK_BOTTOM_PRESSED = (64, 34, 17)

HIGHLIGHT = (245, 232, 208)  # crisp rim-highlight color (near on_background)
SHADOW = (0, 0, 0)


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
    scaling stays safe. Vectorized with numpy -- no per-pixel Python loop."""
    w, h = size
    t = (np.arange(h, dtype=np.float32) / max(h - 1, 1)) ** gamma
    top = np.array(top_color, dtype=np.float32)
    bottom = np.array(bottom_color, dtype=np.float32)
    rows = top[None, :] + (bottom - top)[None, :] * t[:, None]  # (h, 3)
    arr = np.repeat(rows[:, None, :], w, axis=1)  # (h, w, 3)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


# ---------------------------------------------------------------------------
# Brushed-metal texture: directional (streaky) noise + fine grain, built
# with numpy for speed and correctness (a pure-Python per-pixel version of
# this was tried first and had a silent near-zero-variance bug -- vectorize
# this kind of thing, don't hand-loop it).
# ---------------------------------------------------------------------------


def _box_blur_1d(arr, axis, k):
    """Fast box blur along one axis via an integral image (cumulative sum) --
    O(n) instead of O(n*k), and avoids reimplementing a slower manual
    convolution."""
    if k <= 0:
        return arr
    pad_width = [(0, 0), (0, 0)]
    pad_width[axis] = (k, k)
    a = np.pad(arr, pad_width, mode="edge")
    c = np.cumsum(a, axis=axis)
    zero_pad = [(0, 0), (0, 0)]
    zero_pad[axis] = (1, 0)
    c = np.pad(c, zero_pad, mode="constant")
    n = arr.shape[axis]
    idx_hi = [slice(None), slice(None)]
    idx_lo = [slice(None), slice(None)]
    idx_hi[axis] = slice(2 * k + 1, 2 * k + 1 + n)
    idx_lo[axis] = slice(0, n)
    window_sum = c[tuple(idx_hi)] - c[tuple(idx_lo)]
    return window_sum / (2 * k + 1)


def make_brushed_texture(w, h, seed, angle_deg=15):
    """Returns an (h, w) float array of brightness-multiplier deviations,
    roughly in [-2, 2], mixing a heavily-horizontal-blurred "streak" noise
    (the brushed-metal grain direction) with a light fine-grain noise, then
    rotated a few degrees off-axis so the brush direction isn't perfectly
    aligned with the key edges."""
    rng = np.random.default_rng(seed)
    pad = int(max(w, h) * 0.6)
    W, H = w + 2 * pad, h + 2 * pad

    noise = rng.normal(0, 1, size=(H, W)).astype(np.float32)
    streak = _box_blur_1d(noise, axis=1, k=40)
    streak = _box_blur_1d(streak, axis=0, k=2)
    streak = (streak - streak.mean()) / (streak.std() + 1e-6)

    grain = rng.normal(0, 1, size=(H, W)).astype(np.float32)
    grain = _box_blur_1d(grain, axis=1, k=1)
    grain = (grain - grain.mean()) / (grain.std() + 1e-6)

    combined = streak * 0.6 + grain * 0.4
    img = Image.fromarray(np.clip(combined * 40 + 128, 0, 255).astype(np.uint8), mode="L")
    img = img.rotate(angle_deg, resample=Image.BICUBIC, expand=False)
    left = (W - w) // 2
    top = (H - h) // 2
    img = img.crop((left, top, left + w, top + h))
    return (np.asarray(img, dtype=np.float32) - 128) / 40.0


def apply_texture(img, texture, strength=0.05):
    """Multiplicative brightness shading -- a whole-image numpy op, not a
    per-pixel Python loop."""
    arr = np.asarray(img, dtype=np.float32)
    factor = 1.0 + np.clip(texture, -2, 2) * strength
    arr = arr * factor[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def draw_rim_and_shadow(base, inset_box, radius):
    """Crisp highlight line along the dish's top edge, tight shadow line
    along its bottom edge -- harder-edged than a soft ambient glow, per
    docs/MECHANICAL-KEYBOARD-GUIDE.md's PBT/ABS bevel note."""
    x0, y0, x1, y1 = inset_box
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


def draw_bottom_glow(base, inset_box, color, alpha=130, blur=9, height_frac=0.45):
    """Soft colored glow pooling in the bottom portion of the dish -- the
    "light bleeding from under the keycap" cue from the reference mockup,
    approximated within one key's own art since assets can't bleed light
    onto neighboring keys or the shared background layer."""
    x0, y0, x1, y1 = inset_box
    h = y1 - y0
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    glow_top = y1 - h * height_frac
    d.rounded_rectangle(
        [x0 + 4, glow_top, x1 - 4, y1 - 4],
        radius=max((x1 - x0) // 6, 6),
        fill=color + (alpha,),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


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
    tint,
    gamma,
    seed,
    glow_color=None,
    glow_alpha=130,
    glow_height=0.45,
    glow_blur=9,
    tint_amount=0.14,
    stabilizers=False,
    dish_dark_top=DARK_TOP,
    dish_dark_bottom=DARK_BOTTOM,
):
    """Dark brushed-charcoal keycap: outer body + inset dish, both tinted a
    little toward `tint` (the role's accent hue) and textured, with a
    colored glow pooling at the bottom of the dish. `glow_color=None` skips
    the glow entirely (not currently used, kept for a future fully-neutral
    key if wanted)."""
    w, h = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))

    outer_mask = rounded_mask(size, radius)
    body_top = lerp(dish_dark_top, tint, tint_amount * 1.3)
    body_bottom = lerp(dish_dark_bottom, tint, tint_amount * 0.7)
    body = dish_gradient(size, blend_white(body_top, 0.10), body_bottom, 1.0)
    body = apply_texture(body, make_brushed_texture(w, h, seed))
    canvas.paste(body, (0, 0), outer_mask)

    inset = radius + OUTLINE
    inset_box = (inset, inset, w - inset, h - inset)
    inner_radius = max(radius - OUTLINE, 4)
    dish_size = (inset_box[2] - inset_box[0], inset_box[3] - inset_box[1])

    dish_mask = Image.new("L", size, 0)
    dish_mask.paste(rounded_mask(dish_size, inner_radius), (inset_box[0], inset_box[1]))
    grad = dish_gradient(dish_size, dish_dark_top, dish_dark_bottom, gamma)
    grad = apply_texture(grad, make_brushed_texture(dish_size[0], dish_size[1], seed + 1))
    dish_layer = Image.new("RGB", size, (0, 0, 0))
    dish_layer.paste(grad, (inset_box[0], inset_box[1]))
    canvas.paste(dish_layer, (0, 0), dish_mask)

    if glow_color is not None:
        draw_bottom_glow(
            canvas, inset_box, glow_color, alpha=glow_alpha, blur=glow_blur, height_frac=glow_height
        )

    draw_rim_and_shadow(canvas, inset_box, radius)
    if stabilizers:
        draw_stabilizer_dimples(canvas, inset_box)

    return canvas


# ---------------------------------------------------------------------------
# Per-asset definitions
# gamma: <1 = top row (bright longer, steeper late falloff)
#         1 = home row / default baseline
#        >1 = bottom row (falls off earlier, gentler overall)
# ---------------------------------------------------------------------------

RING_KEYS = [
    # name, tint, gamma, seed, glow_color, glow_alpha
    ("Button-default", CLAY, 1.0, 10, CLAY, 90),
    ("Button-function", GOLD, 1.0, 20, GOLD, 120),
    ("Button-row0", ORANGE_RED, 0.72, 30, ORANGE_RED, 130),
    ("Button-row1", ORANGE, 1.0, 40, ORANGE, 130),
    ("Button-row2", RUST_BRIGHT, 1.35, 50, RUST_BRIGHT, 130),
]

PRESSED_SUFFIX = {
    "Button-default": "-press",
    "Button-function": "-pressed",
    "Button-row0": "-press",
    "Button-row1": "-press",
    "Button-row2": "-press",
}


def main():
    for name, tint, gamma, seed, glow, glow_alpha in RING_KEYS:
        normal = render_key(KEY_SIZE, KEY_RADIUS, tint, gamma, seed, glow_color=glow, glow_alpha=glow_alpha)
        normal.save(f"{name}.png")

        pressed = render_key(
            KEY_SIZE,
            KEY_RADIUS,
            tint,
            gamma,
            seed + 100,
            glow_color=glow,
            glow_alpha=min(glow_alpha + 40, 220),
            glow_height=0.55,
            tint_amount=0.20,
            dish_dark_top=DARK_TOP_PRESSED,
            dish_dark_bottom=DARK_BOTTOM_PRESSED,
        )
        pressed.save(f"{name}{PRESSED_SUFFIX[name]}.png")
        print(f"wrote {name}.png / {name}{PRESSED_SUFFIX[name]}.png")

    # Action (enter) key: brighter, bigger orange glow than a normal key --
    # still the "primary" cue, now expressed as light rather than solid fill.
    action = render_key(
        KEY_SIZE, KEY_RADIUS, ORANGE, 1.0, 60,
        glow_color=ORANGE, glow_alpha=190, glow_height=0.75, glow_blur=11, tint_amount=0.22,
    )
    action.save("Button-action.png")

    action_press = render_key(
        KEY_SIZE, KEY_RADIUS, ORANGE, 1.0, 160,
        glow_color=ORANGE, glow_alpha=220, glow_height=0.85, glow_blur=11, tint_amount=0.28,
        dish_dark_top=DARK_TOP_PRESSED, dish_dark_bottom=DARK_BOTTOM_PRESSED,
    )
    action_press.save("Button-action-press.png")
    print("wrote Button-action.png / Button-action-press.png")

    # Spacebar: home-row-like gamma, subtle clay glow, plus stabilizer dimples.
    space = render_key(
        SPACE_SIZE, SPACE_RADIUS, CLAY, 1.0, 70,
        glow_color=CLAY, glow_alpha=90, stabilizers=True,
    )
    space.save("Button-space.png")

    space_press = render_key(
        SPACE_SIZE, SPACE_RADIUS, CLAY, 1.0, 170,
        glow_color=CLAY, glow_alpha=130, glow_height=0.55, tint_amount=0.20,
        dish_dark_top=DARK_TOP_PRESSED, dish_dark_bottom=DARK_BOTTOM_PRESSED,
        stabilizers=True,
    )
    space_press.save("Button-space-press.png")
    print("wrote Button-space.png / Button-space-press.png")

    # stickyon (caps-lock engaged): the dramatically-lit key from the
    # reference mockup -- same dark brushed keycap as everything else, but
    # a big, bright gold glow filling most of the dish, unmistakably "on"
    # rather than a flat solid fill. See docs/GROOVY-CODE-THEME.md for why
    # this replaced the older flat-fill design.
    stickyon = render_key(
        KEY_SIZE, KEY_RADIUS, GOLD, 1.0, 80,
        glow_color=GOLD, glow_alpha=225, glow_height=0.95, glow_blur=14, tint_amount=0.30,
    )
    stickyon.save("Button-stickyon.png")

    stickyon_press = render_key(
        KEY_SIZE, KEY_RADIUS, GOLD, 1.0, 180,
        glow_color=GOLD, glow_alpha=245, glow_height=1.0, glow_blur=14, tint_amount=0.34,
        dish_dark_top=DARK_TOP_PRESSED, dish_dark_bottom=DARK_BOTTOM_PRESSED,
    )
    stickyon_press.save("Button-stickyon-press.png")
    print("wrote Button-stickyon.png / Button-stickyon-press.png")


if __name__ == "__main__":
    main()
