#!/usr/bin/env python3
"""Generate Groovy Code's Button-*.png keycap assets (Pillow + numpy).

v15: single-surface brushed-charcoal keycaps with a small, tight point of
edge light on accent keys only -- replacing v14's separate ring+dish
structure and big glow-pooling-in-the-dish look, which the user said didn't
read as a real mechanical keyboard. Reference: a close-up photo of an
actual backlit mechanical keyboard the user shared. What that photo
actually shows, that v14 missed:

- No visible bezel-ring-around-a-sunken-dish at all -- each keycap is ONE
  continuous surface with a subtle top-lit sheen (lighter near the top,
  darker toward the bottom), not two visually separate regions.
- The colored light is a SMALL, TIGHT, BRIGHT point right at the bottom
  edge of the key -- not a wash filling half the key's face.
- Most keys have NO glow at all in their resting state. Only a handful
  (the number row in the reference, mapped here onto system/action/
  stickyon keys) show any color; plain letter keys are just dark.
- Gaps between keys are much thinner than v14's.

Per the user's standing instruction, every color used is still drawn from
Groovy Code's own 7-color palette -- only the *technique* (single dark
surface + a small bright edge-light on a few keys) came from the
reference, not its colors.

Geometry (radius/outline/canvas size) is fixed to match the `slicing`
values already in theme.txt -- changing these constants requires
recomputing those values too (see docs/THEME-FORMAT.md "Computing slicing
values"). Note: v15 no longer uses an inset "dish" region, but `slicing`
still governs the 9-patch stretch boundary for the whole key, so the
constants below still matter.

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
OUTLINE = 3

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

# Dark charcoal keycap surface, derived from the palette's own near-black
# (#422118) rather than a neutral gray, so the "dark" keys still read as
# part of this palette, not a generic gunmetal. TOP is the subtle top-lit
# sheen, BOTTOM is where the surface reads darkest.
SURF_TOP = (52, 30, 20)
SURF_BOTTOM = (14, 7, 4)
SURF_TOP_PRESSED = (110, 60, 32)
SURF_BOTTOM_PRESSED = (58, 30, 15)

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


def vertical_gradient(size, top_color, bottom_color, gamma):
    """Vertical gradient, vectorized with numpy -- no per-pixel Python loop.
    gamma < 1 biases bright longer near the top (steeper late drop), gamma
    > 1 falls off earlier/gentler -- used as the per-row profile cue."""
    w, h = size
    t = (np.arange(h, dtype=np.float32) / max(h - 1, 1)) ** gamma
    top = np.array(top_color, dtype=np.float32)
    bottom = np.array(bottom_color, dtype=np.float32)
    rows = top[None, :] + (bottom - top)[None, :] * t[:, None]
    arr = np.repeat(rows[:, None, :], w, axis=1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


# ---------------------------------------------------------------------------
# Brushed-metal texture: directional (streaky) noise + fine grain, built
# with numpy for speed and correctness (a pure-Python per-pixel version of
# this was tried first and had a silent near-zero-variance bug -- vectorize
# this kind of thing, don't hand-loop it).
# ---------------------------------------------------------------------------


def _box_blur_1d(arr, axis, k):
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
    roughly in [-2, 2]: a heavily-horizontal-blurred "streak" noise (the
    brushed-metal grain direction) mixed with light fine grain, rotated a
    few degrees off-axis."""
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


def apply_texture(img, texture, strength=0.045):
    arr = np.asarray(img, dtype=np.float32)
    factor = 1.0 + np.clip(texture, -2, 2) * strength
    arr = arr * factor[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def draw_edge_light(base, size, color, alpha, width_frac, height_frac, blur):
    """A small, tight, bright point of light right at the bottom edge of
    the key -- the actual cue from the reference photo, not a wash filling
    the key. Most keys skip this entirely (glow_color=None in render_key)."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lw = w * width_frac
    lh = h * height_frac
    cx = w / 2
    d.ellipse(
        [cx - lw / 2, h - lh - 2, cx + lw / 2, h + lh * 0.3],
        fill=color + (alpha,),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_stabilizer_dimples(base, size):
    """Subtle stabilizer-stem hints at the 1/4 and 3/4 width marks, near the
    key's base -- a cheap, recognizable spacebar detail no phone keyboard
    would have."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for frac in (0.25, 0.75):
        cx = w * frac
        d.rounded_rectangle(
            [cx - 4, h - 22, cx + 4, h - 6], radius=3, fill=SHADOW + (45,)
        )
    layer = layer.filter(ImageFilter.GaussianBlur(1.5))
    base.alpha_composite(layer)


def render_key(
    size,
    radius,
    gamma,
    seed,
    tint=None,
    tint_amount=0.0,
    glow_color=None,
    glow_alpha=0,
    glow_width=0.34,
    glow_height=0.14,
    glow_blur=7,
    stabilizers=False,
    surf_top=SURF_TOP,
    surf_bottom=SURF_BOTTOM,
):
    """One continuous brushed-charcoal surface per key -- no separate
    ring/dish regions, no crisp highlight line. Color, where present at
    all, is a small tight point of light at the bottom edge, not a wash."""
    w, h = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    mask = rounded_mask(size, radius)

    top = lerp(surf_top, tint, tint_amount) if tint else surf_top
    bottom = lerp(surf_bottom, tint, tint_amount * 0.5) if tint else surf_bottom
    body = vertical_gradient(size, top, bottom, gamma)
    body = apply_texture(body, make_brushed_texture(w, h, seed))
    canvas.paste(body, (0, 0), mask)

    if glow_color is not None:
        draw_edge_light(
            canvas, size, glow_color, glow_alpha, glow_width, glow_height, glow_blur
        )
        canvas.putalpha(Image.composite(canvas.getchannel("A"), Image.new("L", size, 0), mask))

    if stabilizers:
        draw_stabilizer_dimples(canvas, size)
        canvas.putalpha(Image.composite(canvas.getchannel("A"), Image.new("L", size, 0), mask))

    return canvas


# ---------------------------------------------------------------------------
# Per-asset definitions
# gamma: <1 = top row (bright longer, steeper late falloff)
#         1 = home row / default baseline
#        >1 = bottom row (falls off earlier, gentler overall)
# Plain letter/functional keys get NO glow at all, matching the reference
# photo (only a handful of keys show any color at rest) -- just a very
# faint per-row tint so the row-banding this theme is known for still
# exists, but nowhere near as loud as v12-v14.
# ---------------------------------------------------------------------------

RING_KEYS = [
    # name, tint, gamma, seed
    ("Button-default", CLAY, 1.0, 10),
    ("Button-function", GOLD, 1.0, 20),
    ("Button-row0", ORANGE_RED, 0.72, 30),
    ("Button-row1", ORANGE, 1.0, 40),
    ("Button-row2", RUST_BRIGHT, 1.35, 50),
]

PRESSED_SUFFIX = {
    "Button-default": "-press",
    "Button-function": "-pressed",
    "Button-row0": "-press",
    "Button-row1": "-press",
    "Button-row2": "-press",
}


def main():
    for name, tint, gamma, seed in RING_KEYS:
        normal = render_key(KEY_SIZE, KEY_RADIUS, gamma, seed, tint=tint, tint_amount=0.05)
        normal.save(f"{name}.png")

        pressed = render_key(
            KEY_SIZE, KEY_RADIUS, gamma, seed + 100,
            tint=tint, tint_amount=0.10,
            surf_top=SURF_TOP_PRESSED, surf_bottom=SURF_BOTTOM_PRESSED,
        )
        pressed.save(f"{name}{PRESSED_SUFFIX[name]}.png")
        print(f"wrote {name}.png / {name}{PRESSED_SUFFIX[name]}.png")

    # Action (enter): a small but brighter/bigger point of orange light than
    # the sparse accent keys below -- still the "primary" cue, just kept to
    # a tight spot instead of a wash.
    action = render_key(
        KEY_SIZE, KEY_RADIUS, 1.0, 60,
        tint=ORANGE, tint_amount=0.08,
        glow_color=ORANGE, glow_alpha=235, glow_width=0.55, glow_height=0.20, glow_blur=9,
    )
    action.save("Button-action.png")

    action_press = render_key(
        KEY_SIZE, KEY_RADIUS, 1.0, 160,
        tint=ORANGE, tint_amount=0.14,
        glow_color=ORANGE, glow_alpha=245, glow_width=0.65, glow_height=0.26, glow_blur=9,
        surf_top=SURF_TOP_PRESSED, surf_bottom=SURF_BOTTOM_PRESSED,
    )
    action_press.save("Button-action-press.png")
    print("wrote Button-action.png / Button-action-press.png")

    # Spacebar: plain, no glow (matches the reference's plain spacebar),
    # just texture and stabilizer dimples.
    space = render_key(SPACE_SIZE, SPACE_RADIUS, 1.0, 70, tint=CLAY, tint_amount=0.04, stabilizers=True)
    space.save("Button-space.png")

    space_press = render_key(
        SPACE_SIZE, SPACE_RADIUS, 1.0, 170,
        tint=CLAY, tint_amount=0.08,
        surf_top=SURF_TOP_PRESSED, surf_bottom=SURF_BOTTOM_PRESSED,
        stabilizers=True,
    )
    space_press.save("Button-space-press.png")
    print("wrote Button-space.png / Button-space-press.png")

    # stickyon (caps-lock engaged): the one dramatically-lit key from the
    # reference photo -- still a single dark brushed surface, but with a
    # big, bright gold point of light spreading across most of the lower
    # half, unmistakably "on."
    stickyon = render_key(
        KEY_SIZE, KEY_RADIUS, 1.0, 80,
        tint=GOLD, tint_amount=0.10,
        glow_color=GOLD, glow_alpha=250, glow_width=0.95, glow_height=0.55, glow_blur=13,
    )
    stickyon.save("Button-stickyon.png")

    stickyon_press = render_key(
        KEY_SIZE, KEY_RADIUS, 1.0, 180,
        tint=GOLD, tint_amount=0.14,
        glow_color=GOLD, glow_alpha=255, glow_width=1.0, glow_height=0.62, glow_blur=13,
        surf_top=SURF_TOP_PRESSED, surf_bottom=SURF_BOTTOM_PRESSED,
    )
    stickyon_press.save("Button-stickyon-press.png")
    print("wrote Button-stickyon.png / Button-stickyon-press.png")


if __name__ == "__main__":
    main()
