#!/usr/bin/env python3
"""Generate the classic-keyboard variant themes under variants/<slug>/.

Each variant is a separate, self-contained FUTO Keyboard theme package
(its own theme.txt + Button-*.png + Icon-*.png + font + background +
attributions) using the same "brown well + bright inset face + rim"
structure as Groovy Code v17 (scripts/keycap_render.py), just recolored to
replicate a real classic keyboard's palette. FUTO's theme format has no
in-app palette-switching within one theme (confirmed: one theme.txt = one
fixed `[colors]`/asset set, see docs/THEME-FORMAT.md) -- so "alternative
color options" means separate installable packages, not a mode switch
inside Groovy Code itself.

Per the user's explicit choice, these are "mostly flat" like the real
keyboards they reference -- most keys are one uniform color, with only
the keyboards whose own hardware has a real accent (Commodore 64's
blue-gray function keys and reddish-brown RETURN key) or an unavoidable
UI need (the `stickyon`/caps-lock state, which has no on-key equivalent
on any of these real keyboards but has to read as "locked" in a
touchscreen theme) getting any color variation at all.

Run from the repo root: `python3 scripts/generate_variants.py`.
"""

import os
import shutil

from keycap_render import KEY_SIZE, KEY_RADIUS, SPACE_SIZE, SPACE_RADIUS, render_key, vertical_gradient, scale

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANTS_DIR = os.path.join(REPO_ROOT, "variants")

BACKGROUND_SIZE = (1080, 1080)

SHARED_FILES = [
    "Icon-backspace.png", "Icon-emoji.png", "Icon-shift-press.png", "Icon-shift.png",
    "Icon-enter.png", "Icon-globe.png", "Icon-mic.png", "Icon-tab.png",
    "Icon-arrow-left.png", "Icon-arrow-right.png",
    "FiraCode-Regular.ttf", "FONT-ATTRIBUTION.txt", "ICON-ATTRIBUTION.txt",
    "Button-morekey.png", "Button-morekeysbox.png",
]


def hexs(rgb):
    return "#%02x%02x%02x" % rgb


THEME_TEMPLATE = """\
# -------------------------------------------------------------------
#                  FUTO Keyboard Theme Configuration
#                        Format version: 1.0
# {name} — a classic-keyboard color variant of Groovy Code, replicating
# {reference_note}, set in FiraCode.
# -------------------------------------------------------------------

name = "{name}"
author = "Shelbee"
id = "{theme_id}"
version = 1
description = "{description}"

[options]
auto_borders = true
center_hints = false
roundedness = 0.6
scale_text = 1.0
scale_hints = 0.85
weight_text = 500
weight_hints = 400

[colors]
primary = "{primary}"
on_primary = "{on_primary}"
primary_container = "{well_hex}"
on_primary_container = "{legend_hex}"
inverse_primary = "{rim_hex}"

secondary = "{secondary}"
on_secondary = "{on_secondary}"
secondary_container = "{well_hex}"
on_secondary_container = "{legend_hex}"

tertiary = "{rim_hex}"
on_tertiary = "{legend_hex}"
tertiary_container = "{well_hex}"
on_tertiary_container = "{legend_hex}"

background = "{bg_hex}"
on_background = "{legend_hex}"

surface = "{bg_hex}"
on_surface = "{legend_hex}"
surface_variant = "{well_hex}"
on_surface_variant = "{legend_hex}"
surface_tint = "{primary}"
inverse_surface = "{legend_hex}"
inverse_on_surface = "{bg_hex}"

error = "#bd361e"
on_error = "#f5e6c8"
error_container = "#422118"
on_error_container = "#f0c9a0"

outline = "{rim_hex}99"
outline_variant = "{rim_hex}66"
scrim = "#000000"

surface_bright = "{well_hex}"
surface_dim = "{bg_hex}"
surface_container = "{bg_hex}"
surface_container_high = "{well_hex}"
surface_container_highest = "{well_hex}"
surface_container_low = "{bg_hex}"
surface_container_lowest = "{bg_hex}"

keyboard_surface = "{bg_hex}"
keyboard_surface_dim = "{bg_hex}"
keyboard_container = "{well_hex}"
keyboard_container_variant = "{well_hex}"
on_keyboard_container = "{legend_hex}"
keyboard_press = "{well_hex}"
keyboard_container_pressed = "{rim_hex}44"
on_keyboard_container_pressed = "{legend_hex}00"

[options.font]
font = "FiraCode-Regular.ttf"

[options.background]
image = "{background_file}"
opacity = 1
action_bar_opacity = 0.3
cropping = [0.0, 0.0, 1.0, 1.0]

# -------------------------------------------------------------------
# Matchrules — order-dependent, first match wins. No row-banding in
# this variant (flat, per the real keyboard it replicates).
# -------------------------------------------------------------------

[[matchrules.border]]
selector = "morekeysbox"
asset = "Button-morekeysbox.png"

[[matchrules.border]]
selector = "morekey"
asset = "Button-morekey.png"

[[matchrules.border]]
selector = "action pressed"
asset = "Button-action-press.png"

[[matchrules.border]]
selector = "action"
asset = "Button-action.png"

[[matchrules.border]]
selector = "spacebar pressed"
asset = "Button-space-press.png"

[[matchrules.border]]
selector = "spacebar"
asset = "Button-space.png"

[[matchrules.border]]
selector = "stickyon pressed"
asset = "Button-stickyon-press.png"

[[matchrules.border]]
selector = "stickyon"
asset = "Button-stickyon.png"

[[matchrules.border]]
selector = "functional pressed"
asset = "Button-function-pressed.png"

[[matchrules.border]]
selector = "functional popup"
asset = "Button-function-pressed.png"

[[matchrules.border]]
selector = "functional"
asset = "Button-function.png"

[[matchrules.border]]
selector = "normal popup"
asset = "Button-default-press.png"

[[matchrules.border]]
selector = "pressed"
asset = "Button-default-press.png"

[[matchrules.border]]
selector = "normal"
asset = "Button-default.png"

[[matchrules.icon]]
selector = "icon delete_key"
asset = "Icon-backspace.png"

[[matchrules.icon]]
selector = "icon action_emoji"
asset = "Icon-emoji.png"

[[matchrules.icon]]
selector = "icon shift_key_shifted"
asset = "Icon-shift-press.png"

[[matchrules.icon]]
selector = "icon shift_key"
asset = "Icon-shift.png"

[[matchrules.icon]]
selector = "icon enter_key"
asset = "Icon-enter.png"

[[matchrules.icon]]
selector = "icon action_switch_language"
asset = "Icon-globe.png"

[[matchrules.icon]]
selector = "icon mic_fill"
asset = "Icon-mic.png"

[[matchrules.icon]]
selector = "icon tab_key"
asset = "Icon-tab.png"

[[matchrules.icon]]
selector = "icon action_left"
asset = "Icon-arrow-left.png"

[[matchrules.icon]]
selector = "icon action_right"
asset = "Icon-arrow-right.png"

# -------------------------------------------------------------------
# Asset configs — one entry per image used above. Slicing fractions
# match scripts/keycap_render.py's shared KEY_SIZE/KEY_RADIUS geometry
# (see docs/THEME-FORMAT.md "Computing slicing values").
# -------------------------------------------------------------------

[[asset.border]]
name = "Button-morekeysbox.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.05, 0.28, 0.95, 0.72]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-morekey.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0, 0, 1, 1]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-default.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-default-press.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-function.png"
background_tint = "#ffffff"
foreground_tint = "{function_legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-function-pressed.png"
background_tint = "#ffffff"
foreground_tint = "{function_legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-space.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.052, 0.206, 0.948, 0.794]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-space-press.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.052, 0.206, 0.948, 0.794]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-action.png"
background_tint = "#ffffff"
foreground_tint = "{action_legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-action-press.png"
background_tint = "#ffffff"
foreground_tint = "{action_legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-stickyon.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.border]]
name = "Button-stickyon-press.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.18, 0.18, 0.82, 0.82]
gap = [1.15, 1.15, 1.15, 1.15]
target_density = 640

[[asset.icon]]
name = "Icon-backspace.png"
target_density = 640

[[asset.icon]]
name = "Icon-emoji.png"
target_density = 640

[[asset.icon]]
name = "Icon-shift-press.png"
target_density = 640

[[asset.icon]]
name = "Icon-shift.png"
target_density = 640

[[asset.icon]]
name = "Icon-enter.png"
target_density = 640

[[asset.icon]]
name = "Icon-globe.png"
target_density = 640

[[asset.icon]]
name = "Icon-mic.png"
target_density = 640

[[asset.icon]]
name = "Icon-tab.png"
target_density = 640

[[asset.icon]]
name = "Icon-arrow-left.png"
target_density = 640

[[asset.icon]]
name = "Icon-arrow-right.png"
target_density = 640
"""


# ---------------------------------------------------------------------------
# Variant profiles. Each face_* is an (R,G,B) tuple fed to render_key;
# each *_hex/legend value is the same color pre-formatted for theme.txt.
# "Mostly flat" per the user's choice: face_function/face_action/face_space
# default to face_default (no color difference at all) unless a profile
# overrides them -- only Commodore 64 (real hardware accent keys) and the
# stickyon/caps-lock state (no on-key equivalent on any of these real
# keyboards, but required for a legible "locked" cue) get real variation.
# ---------------------------------------------------------------------------

PROFILES = [
    {
        "slug": "ibm-model-m",
        "name": "IBM Model M",
        "theme_id": "com.shelbee.ibmmodelm",
        "reference_note": "the IBM Model M's monochrome putty-beige keycaps",
        "description": "Classic IBM Model M color variant: monochrome putty-beige keycaps in a warm gray well, no per-row or per-role color coding (the real keyboard has none) -- only caps-lock brightens and picks up a small amber LED-style glow. Set in FiraCode.",
        "well": (140, 132, 109),
        "face_default": (232, 224, 196),
        "face_stickyon": (245, 238, 214),
        "rim": (107, 100, 85),
        "legend": (43, 40, 32),
        "bloom_stickyon_color": (255, 153, 0),
        "bloom_stickyon_alpha": 150,
    },
    {
        "slug": "mac-plus",
        "name": "Macintosh Plus",
        "theme_id": "com.shelbee.macplus",
        "reference_note": "the Macintosh Plus's platinum keycaps",
        "description": "Classic Macintosh Plus color variant: monochrome warm platinum-gray keycaps, no per-row or per-role color coding (the real keyboard has none) -- only caps-lock brightens and picks up a soft System-blue glow, a small nod to the classic Mac UI highlight color rather than any real on-key indicator. Set in FiraCode.",
        "well": (139, 134, 128),
        "face_default": (212, 208, 200),
        "face_stickyon": (237, 234, 226),
        "rim": (112, 107, 98),
        "legend": (42, 40, 35),
        "bloom_stickyon_color": (91, 127, 166),
        "bloom_stickyon_alpha": 130,
    },
    {
        "slug": "commodore-64",
        "name": "Commodore 64",
        "theme_id": "com.shelbee.commodore64",
        "reference_note": "the Commodore 64's beige keycaps with its blue-gray function row and reddish-brown RETURN key",
        "description": "Classic Commodore 64 color variant: warm beige keycaps in a brown well, blue-gray function/system keys, a reddish-brown RETURN key, and a bright blue-screen glow on caps-lock. Set in FiraCode.",
        "well": (110, 87, 56),
        "face_default": (214, 190, 148),
        "face_function": (124, 138, 156),
        "face_action": (139, 68, 50),
        "face_stickyon": (155, 169, 188),
        "rim": (74, 59, 38),
        "legend": (32, 22, 13),
        "bloom_stickyon_color": (65, 105, 225),
        "bloom_stickyon_alpha": 160,
    },
    {
        "slug": "amber-terminal",
        "name": "Amber Terminal",
        "theme_id": "com.shelbee.amberterminal",
        "reference_note": "a VT100-style amber phosphor terminal's monochrome black keys with amber trim",
        "description": "Amber phosphor terminal color variant: uniform near-black keycaps, no per-row or per-role face color at all -- the only color is a thin amber rim and amber legends on every key, with the enter key and caps-lock picking up a soft amber glow like a lit terminal cursor block. Set in FiraCode.",
        "well": (10, 10, 10),
        "face_default": (22, 22, 22),
        "rim": (255, 176, 0),
        "legend": (255, 176, 0),
        "bloom_action_color": (255, 176, 0),
        "bloom_action_alpha": 90,
        "bloom_stickyon_color": (255, 176, 0),
        "bloom_stickyon_alpha": 210,
    },
]


def build_background(well):
    top = tuple(min(255, c + 25) for c in well)
    bottom = scale(well, 0.6)
    return vertical_gradient(BACKGROUND_SIZE, top, bottom)


def generate_variant(profile):
    slug = profile["slug"]
    out_dir = os.path.join(VARIANTS_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)

    well = profile["well"]
    rim = profile["rim"]
    legend = profile["legend"]
    face_default = profile["face_default"]
    face_function = profile.get("face_function", face_default)
    face_action = profile.get("face_action", face_default)
    face_space = profile.get("face_space", face_default)
    face_stickyon = profile.get("face_stickyon", face_default)

    action_bloom_color = profile.get("bloom_action_color")
    action_bloom_alpha = profile.get("bloom_action_alpha", 0)
    stickyon_bloom_color = profile.get("bloom_stickyon_color")
    stickyon_bloom_alpha = profile.get("bloom_stickyon_alpha", 0)

    def save(name, img):
        img.save(os.path.join(out_dir, name))

    save("Button-default.png", render_key(KEY_SIZE, KEY_RADIUS, face_default, well, rim))
    save("Button-default-press.png", render_key(KEY_SIZE, KEY_RADIUS, face_default, well, rim, pressed=True))

    save("Button-function.png", render_key(KEY_SIZE, KEY_RADIUS, face_function, well, rim))
    save("Button-function-pressed.png", render_key(KEY_SIZE, KEY_RADIUS, face_function, well, rim, pressed=True))

    save("Button-action.png", render_key(
        KEY_SIZE, KEY_RADIUS, face_action, well, rim,
        bloom_alpha=action_bloom_alpha, bloom_color=action_bloom_color, bloom_pad=7,
    ))
    save("Button-action-press.png", render_key(KEY_SIZE, KEY_RADIUS, face_action, well, rim, pressed=True))

    save("Button-space.png", render_key(SPACE_SIZE, SPACE_RADIUS, face_space, well, rim, stabilizers=True))
    save("Button-space-press.png", render_key(
        SPACE_SIZE, SPACE_RADIUS, face_space, well, rim, pressed=True, stabilizers=True
    ))

    save("Button-stickyon.png", render_key(
        KEY_SIZE, KEY_RADIUS, face_stickyon, well, rim,
        bloom_alpha=stickyon_bloom_alpha, bloom_color=stickyon_bloom_color, bloom_pad=9,
    ))
    save("Button-stickyon-press.png", render_key(KEY_SIZE, KEY_RADIUS, face_stickyon, well, rim, pressed=True))

    background_file = f"{slug}-background.png"
    build_background(well).save(os.path.join(out_dir, background_file))

    for fname in SHARED_FILES:
        shutil.copy(os.path.join(REPO_ROOT, fname), os.path.join(out_dir, fname))

    function_legend = profile.get("function_legend", legend)
    action_legend = profile.get("action_legend", legend)

    theme_txt = THEME_TEMPLATE.format(
        name=profile["name"],
        reference_note=profile["reference_note"],
        theme_id=profile["theme_id"],
        description=profile["description"],
        background_file=background_file,
        well_hex=hexs(well),
        rim_hex=hexs(rim),
        legend_hex=hexs(legend),
        function_legend_hex=hexs(function_legend),
        action_legend_hex=hexs(action_legend),
        bg_hex=hexs(tuple(min(255, c + 25) for c in well)),
        primary=hexs(face_action),
        on_primary=hexs(legend),
        secondary=hexs(face_function),
        on_secondary=hexs(function_legend),
    )
    with open(os.path.join(out_dir, "theme.txt"), "w") as f:
        f.write(theme_txt)

    print(f"wrote variants/{slug}/ ({len(os.listdir(out_dir))} files)")


def main():
    for profile in PROFILES:
        generate_variant(profile)


if __name__ == "__main__":
    main()
