"""Shared keycap rendering primitives (Pillow + numpy).

v19: organic "cookie"-shaped keys, replacing the v12-v18 rounded-rectangle
well+face+rim structure entirely, across every theme in this repo
(Groovy Code included). Prompted by a real published FUTO theme --
"Animal Keys" by TrashKittyQueen (`p.trashkittyqueen.petkeys`, downloaded
and inspected directly from https://keyboard.futo.tech/themes) -- whose
actual technique turned out to be: irregular, organic, hand-drawn-looking
key silhouettes (not clean rounded rects), a handful of accent keys with
a small motif baked into the art, and a decorative motif scattered
subtly across the background. This module reproduces that *technique*
procedurally (this repo's whole build approach is generative, not
hand-drawn assets) rather than copying Animal Keys' actual art or colors.

Every theme keeps its own well/face/rim colors and its own motif glyph
(see scripts/generate_assets.py and scripts/generate_variants.py) -- only
the organic-silhouette *mechanism* is shared here.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

KEY_SIZE = (160, 160)
SPACE_SIZE = (640, 160)

RIM_FRAC = 0.018  # rim thickness as a fraction of min(w,h), organic-shape equivalent of RIM_WIDTH
SLICING_OUTLINE = 3  # safety margin (px, at 160-scale) baked into the slicing fraction, same as pre-v19


def compute_slicing(radius_frac, size, outline=SLICING_OUTLINE):
    """The 9-patch stretch boundary for an organic border asset of the
    given canvas `size` at the given `radius_frac` (see organic_mask/
    render_organic_key) -- generalizes the fixed formula this theme's
    theme.txt comments used to derive by hand for a plain rounded rect
    (radius 26 on a 160x160 key -> (26+3)/160 = 0.18). Returns
    [x0, y0, x1, y1] fractions ready to drop into a `slicing = [...]`
    line. Every theme/asset with its own `radius_frac` must recompute
    its own slicing -- never reuse another asset's fixed values."""
    w, h = size
    radius_px = radius_frac * min(w, h)
    fx = (radius_px + outline) / w
    fy = (radius_px + outline) / h
    return [round(fx, 4), round(fy, 4), round(1 - fx, 4), round(1 - fy, 4)]


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def blend_white(color, t):
    return lerp(color, (255, 255, 255), t)


def scale(color, f):
    return tuple(round(c * f) for c in color)


def vertical_gradient(size, top_color, bottom_color):
    w, h = size
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        grad.putpixel((0, y), lerp(top_color, bottom_color, t))
    return grad.resize(size)


# ---------------------------------------------------------------------------
# Organic blob silhouette -- NOT a stretched ellipse (tried that first; it
# produces pointy ends on the wide 4:1 spacebar canvas, since an ellipse's
# curvature scales with aspect ratio). Checked directly against Animal
# Keys' own Button-space-dark.png, which is a rounded-rect body with
# irregular, slightly-bulgy CORNERS and flat straight edges between them
# -- not a full organic blob stretched end to end. This is also exactly
# what a 9-patch wants: straight stretchy edges, detail only in the
# corners. Implemented as a signed-distance-to-rounded-rect field (same
# shape as a normal rounded rectangle) whose effective corner radius is
# perturbed per-angle by a few random sine harmonics -- flat edges get a
# single per-edge perturbation (since the angle is constant along a flat
# edge), corners get the fully-varying organic wobble. Vectorized with
# numpy (not a per-pixel Python loop -- see docs/GROOVY-CODE-THEME.md's
# v14 entry for why that's a specific, remembered mistake in this repo).
# ---------------------------------------------------------------------------

def organic_mask(size, seed, radius_frac=0.30, wobble=0.09, harmonics=(2, 3, 5), supersample=3):
    w, h = size
    ss = supersample
    W, H = w * ss, h * ss
    R = min(W, H) * radius_frac

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = np.maximum(np.maximum(R - xx, xx - (W - R)), 0)
    dy = np.maximum(np.maximum(R - yy, yy - (H - R)), 0)
    dist = np.sqrt(dx ** 2 + dy ** 2)
    theta = np.arctan2(dy, dx)

    rng = np.random.default_rng(seed)
    wob = np.ones_like(theta)
    for k in harmonics:
        amp = wobble * rng.uniform(0.4, 1.0) / len(harmonics)
        phase = rng.uniform(0, 2 * np.pi)
        wob = wob + amp * np.sin(k * theta + phase)
    wob = np.clip(wob, 0.35, None)

    mask = (dist <= R * wob).astype(np.float32) * 255
    img = Image.fromarray(mask.astype(np.uint8), mode="L")
    return img.resize((w, h), Image.LANCZOS)


def render_organic_key(
    size,
    seed,
    face_color,
    well_color,
    rim_color,
    pressed=False,
    radius_frac=0.30,
    wobble=0.09,
    harmonics=(2, 3, 5),
    margin_frac=0.09,
    stabilizers=False,
    bloom_alpha=0,
    bloom_pad_frac=0.05,
    bloom_color=None,
    well_top_blend=0.10,
    well_bottom_scale=0.72,
    face_top_blend=0.14,
    face_bottom_scale=0.82,
    pressed_face_scale=0.80,
    rim_top_blend=0.15,
    rim_pressed_scale=0.75,
    rim_frac=RIM_FRAC,
    motif_fn=None,
    motif_color=None,
    motif_alpha=150,
    motif_scale_frac=0.15,
    motif_pos=(0.5, 0.36),
    motif_kwargs=None,
):
    """Well + inset face + rim, all organically-shaped nested blobs sharing
    the same `seed` (so the face/rim nest self-similarly inside the well,
    rather than three unrelated random shapes) at shrinking `radius_frac`.
    Every geometry/material knob defaults close to Groovy Code's own v18
    values so behavior stays predictable across callers; `radius_frac`/
    `wobble`/`margin_frac` are what give each theme its own silhouette
    character (see scripts/generate_variants.py profiles). `motif_fn`, if
    given, draws a small themed glyph (signature `(draw, cx, cy, r, color,
    alpha)`) centered on the face -- used sparingly, on `stickyon` and one
    or two accent keys, not on every key."""
    w, h = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    outer_mask = organic_mask(size, seed, radius_frac, wobble, harmonics)

    well_top = blend_white(well_color, well_top_blend) if not pressed else well_color
    well_bottom = scale(well_color, well_bottom_scale)
    well = vertical_gradient(size, well_top, well_bottom)
    canvas.paste(well, (0, 0), outer_mask)

    face_radius_frac = radius_frac - margin_frac
    rim_radius_frac = face_radius_frac + rim_frac
    face_mask = organic_mask(size, seed, face_radius_frac, wobble, harmonics)
    rim_mask = organic_mask(size, seed, rim_radius_frac, wobble, harmonics)

    face = scale(face_color, pressed_face_scale) if pressed else face_color

    if bloom_alpha and not pressed:
        glow_color = bloom_color if bloom_color is not None else face_color
        bloom_mask = organic_mask(size, seed, rim_radius_frac + bloom_pad_frac, wobble, harmonics)
        bloom_layer = Image.new("RGBA", size, (0, 0, 0, 0))
        bloom_layer.paste(Image.new("RGB", size, glow_color), (0, 0), bloom_mask)
        alpha_arr = (np.asarray(bloom_mask, dtype=np.float32) * (bloom_alpha / 255.0)).astype(np.uint8)
        bloom_layer.putalpha(Image.fromarray(alpha_arr, mode="L"))
        bloom_layer = bloom_layer.filter(ImageFilter.GaussianBlur(max(w, h) * 0.025))
        canvas.alpha_composite(bloom_layer)

    rim_draw_color = blend_white(rim_color, rim_top_blend) if not pressed else scale(rim_color, rim_pressed_scale)
    rim_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    rim_layer.paste(Image.new("RGB", size, rim_draw_color), (0, 0), rim_mask)
    canvas.alpha_composite(rim_layer)

    face_top = blend_white(face, face_top_blend)
    face_bottom = scale(face, face_bottom_scale)
    face_grad = vertical_gradient(size, face_top, face_bottom)
    face_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    face_layer.paste(face_grad, (0, 0), face_mask)
    canvas.alpha_composite(face_layer)

    if motif_fn is not None:
        motif_layer = Image.new("RGBA", size, (0, 0, 0, 0))
        d = ImageDraw.Draw(motif_layer)
        mc = motif_color if motif_color is not None else rim_color
        mx, my = w * motif_pos[0], h * motif_pos[1]
        motif_fn(d, mx, my, min(w, h) * motif_scale_frac, mc, motif_alpha, **(motif_kwargs or {}))
        motif_layer.putalpha(
            Image.composite(motif_layer.getchannel("A"), Image.new("L", size, 0), face_mask)
        )
        canvas.alpha_composite(motif_layer)

    if stabilizers:
        dimples = Image.new("RGBA", size, (0, 0, 0, 0))
        dd = ImageDraw.Draw(dimples)
        for frac in (0.25, 0.75):
            cx = w * frac
            dd.ellipse(
                [cx - w * 0.02, h * 0.68, cx + w * 0.02, h * 0.82],
                fill=scale(face, 0.75) + (140,),
            )
        canvas.alpha_composite(dimples)

    canvas.putalpha(Image.composite(canvas.getchannel("A"), Image.new("L", size, 0), outer_mask))
    return canvas


# ---------------------------------------------------------------------------
# Motif glyphs -- small, simple line-art badges, one per theme, used (a)
# baked into a theme's stickyon/accent key art via render_organic_key's
# motif_fn, and (b) scattered across the background via scatter_motifs.
# Each theme picks ONE of these to be its own visual signature, the same
# role Animal Keys' paw print plays for itself. Signature is always
# `(draw, cx, cy, r, color, alpha)` so they're interchangeable.
# ---------------------------------------------------------------------------

def motif_sunburst(draw, cx, cy, r, color, alpha):
    """Groovy Code -- a small 70's sun, radiating short rays from a disc."""
    draw.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4], fill=color + (alpha,))
    width = max(1, round(r * 0.14))
    for i in range(8):
        ang = i * (2 * np.pi / 8)
        x0, y0 = cx + np.cos(ang) * r * 0.52, cy + np.sin(ang) * r * 0.52
        x1, y1 = cx + np.cos(ang) * r, cy + np.sin(ang) * r
        draw.line([x0, y0, x1, y1], fill=color + (alpha,), width=width)


def motif_switch_cross(draw, cx, cy, r, color, alpha):
    """IBM Model M -- a stylized keyswitch stem (square + cross), the
    buckling-spring mechanism's own iconography."""
    width = max(1, round(r * 0.16))
    draw.rounded_rectangle(
        [cx - r, cy - r, cx + r, cy + r], radius=r * 0.2, outline=color + (alpha,), width=width
    )
    draw.line([cx - r * 0.55, cy, cx + r * 0.55, cy], fill=color + (alpha,), width=width)
    draw.line([cx, cy - r * 0.55, cx, cy + r * 0.55], fill=color + (alpha,), width=width)


def motif_crt(draw, cx, cy, r, color, alpha):
    """Macintosh Plus -- a tiny CRT monitor silhouette on a stand."""
    width = max(1, round(r * 0.14))
    draw.rounded_rectangle(
        [cx - r, cy - r * 0.7, cx + r, cy + r * 0.5],
        radius=r * 0.22, outline=color + (alpha,), width=width,
    )
    draw.rectangle([cx - r * 0.3, cy + r * 0.5, cx + r * 0.3, cy + r * 0.68], fill=color + (alpha,))


def motif_chip(draw, cx, cy, r, color, alpha):
    """Commodore 64 -- a small IC chip, pin-lines on both sides."""
    width = max(1, round(r * 0.13))
    draw.rectangle([cx - r * 0.55, cy - r * 0.42, cx + r * 0.55, cy + r * 0.42], outline=color + (alpha,), width=width)
    for i in range(3):
        yy = cy - r * 0.28 + i * r * 0.28
        draw.line([cx - r * 0.8, yy, cx - r * 0.55, yy], fill=color + (alpha,), width=width)
        draw.line([cx + r * 0.55, yy, cx + r * 0.8, yy], fill=color + (alpha,), width=width)


def motif_cursor(draw, cx, cy, r, color, alpha):
    """Amber terminal -- a ">_" terminal prompt glyph."""
    width = max(1, round(r * 0.18))
    draw.line([cx - r * 0.7, cy - r * 0.5, cx - r * 0.1, cy], fill=color + (alpha,), width=width)
    draw.line([cx - r * 0.1, cy, cx - r * 0.7, cy + r * 0.5], fill=color + (alpha,), width=width)
    draw.rectangle([cx + r * 0.05, cy + r * 0.32, cx + r * 0.75, cy + r * 0.52], fill=color + (alpha,))


def motif_dpad(draw, cx, cy, r, color, alpha):
    """Game Boy / Game Boy Color -- a D-pad cross."""
    draw.rounded_rectangle([cx - r * 0.26, cy - r * 0.85, cx + r * 0.26, cy + r * 0.85], radius=r * 0.1, fill=color + (alpha,))
    draw.rounded_rectangle([cx - r * 0.85, cy - r * 0.26, cx + r * 0.85, cy + r * 0.26], radius=r * 0.1, fill=color + (alpha,))


def motif_button_pair(draw, cx, cy, r, color, alpha):
    """NES -- two small rectangular buttons, offset like A/B."""
    draw.rounded_rectangle(
        [cx - r * 0.75, cy + r * 0.05, cx - r * 0.05, cy + r * 0.55],
        radius=r * 0.18, fill=color + (alpha,),
    )
    draw.rounded_rectangle(
        [cx + r * 0.05, cy - r * 0.55, cx + r * 0.75, cy - r * 0.05],
        radius=r * 0.18, fill=color + (alpha,),
    )


def motif_diamond_cluster(draw, cx, cy, r, color, alpha, colors=None):
    """SNES -- four small dots in a diamond, echoing Y/X/A/B. Pass `colors`
    (a list of 4) to tint each dot its own face-button color instead of
    the uniform `color`."""
    pts = [(cx, cy - r * 0.75), (cx + r * 0.75, cy), (cx, cy + r * 0.75), (cx - r * 0.75, cy)]
    cols = colors if colors is not None else [color] * 4
    for (px, py), c in zip(pts, cols):
        draw.ellipse([px - r * 0.3, py - r * 0.3, px + r * 0.3, py + r * 0.3], fill=c + (alpha,))


def scatter_motifs(size, motif_fn, color, count, seed, alpha=45, scale_frac=(0.028, 0.05), margin_frac=0.06, **motif_kwargs):
    """Scatters `count` small, low-alpha copies of `motif_fn` across a
    canvas of `size` -- the background-texture equivalent of Animal Keys'
    paw-print wood background. Returns an RGBA layer to composite onto a
    background image."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = np.random.default_rng(seed)
    mx, my = w * margin_frac, h * margin_frac
    for _ in range(count):
        cx = rng.uniform(mx, w - mx)
        cy = rng.uniform(my, h - my)
        r = min(w, h) * rng.uniform(*scale_frac)
        motif_fn(d, cx, cy, r, color, alpha, **motif_kwargs)
    return layer
