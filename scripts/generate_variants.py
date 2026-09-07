#!/usr/bin/env python3
"""Generate the classic-hardware variant themes under variants/<slug>/.

Each variant is a separate, self-contained FUTO Keyboard theme package
(its own theme.txt + Button-*.png + Icon-*.png + font + background +
attributions) using the same organic "cookie"-shaped well+face+rim
structure as Groovy Code v19 (scripts/keycap_render.py), recolored and
reshaped to replicate a real device's palette and physical character, plus
its own small motif glyph. FUTO's theme format has no in-app palette-
switching within one theme (confirmed: one theme.txt = one fixed
`[colors]`/asset set, see docs/THEME-FORMAT.md) -- so "alternative color
options" means separate installable packages, not a mode switch inside
Groovy Code itself.

v19 note: every variant here was already organically-shaped-and-motif'd in
this pass (there was no earlier rounded-rect version of these 8 to
preserve compatibility with) -- this whole file was rewritten alongside
keycap_render.py's organic primitives, prompted by the user's explicit
direction to take the whole "classic-hardware variant" project in this
direction after seeing Animal Keys (TrashKittyQueen,
p.trashkittyqueen.petkeys, downloaded from
https://keyboard.futo.tech/themes and inspected directly -- see
docs/VARIANTS.md for what its actual technique turned out to be).

Per the user's explicit choice for the first (keyboard) batch, color
stays "mostly flat" like the real hardware -- most keys are one uniform
color, with only the devices whose own hardware has a real accent
(Commodore 64's blue-gray function keys and reddish-brown RETURN key) or
an unavoidable UI need (the `stickyon`/caps-lock state, which has no
on-key equivalent on any of these real keyboards but has to read as
"locked" in a touchscreen theme) getting any color variation at all. SNES
is the one exception that opts INTO row-banding, since its four-color
face-button scheme IS its identity (see its profile below).

8BitDo research (per the user's explicit request, confirmed via web
search): 8BitDo's real "Retro Mechanical Keyboard" product line has
exactly four color editions -- N (NES), Fami (Famicom), M, and C64
(Commodore 64) -- confirming a real, currently-sold C64-themed mechanical
keyboard exists and validating this repo's own Commodore 64 variant as
matching a real product category, not just an invented idea. "M Edition"
is a separate colorway from either of our Game Boy or SNES references
(8BitDo's own naming, not Nintendo's), so it didn't inform any specific
palette change here -- noted for completeness rather than acted on.

Run from the repo root: `python3 scripts/generate_variants.py`.
"""

import os
import shutil

from keycap_render import (
    KEY_SIZE, SPACE_SIZE,
    render_organic_key, vertical_gradient, scale, compute_slicing, scatter_motifs,
    motif_switch_cross, motif_crt, motif_chip, motif_cursor,
    motif_dpad, motif_button_pair, motif_diamond_cluster,
)

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


# ---------------------------------------------------------------------------
# theme.txt is assembled from parts rather than one flat template, so that
# row-banded variants (currently just SNES) can splice in the row0/1/2
# matchrules + asset blocks that Groovy Code's own root theme.txt uses,
# while flat variants skip them entirely. All parts share one kwargs dict
# and get formatted together at the end (see build_theme_txt()).
# ---------------------------------------------------------------------------

HEAD_TEMPLATE = """\
# -------------------------------------------------------------------
#                  FUTO Keyboard Theme Configuration
#                        Format version: 1.0
# {name} — a color-and-shape variant of Groovy Code, replicating
# {reference_note}, set in FiraCode.
# -------------------------------------------------------------------

name = "{name}"
author = "Shelbee"
id = "{theme_id}"
version = 4
description = "{description}"

[options]
auto_borders = true
center_hints = false
roundedness = {roundedness}
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
# Matchrules — order-dependent, first match wins.
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
"""

# Only spliced in for row_banded profiles (currently just SNES) -- must sit
# after functional and before the generic pressed/normal fallback, same
# ordering rule as Groovy Code's own root theme.txt.
MATCHRULES_ROWBANDED = """
[[matchrules.border]]
selector = "normal row 0 pressed"
asset = "Button-row0-press.png"

[[matchrules.border]]
selector = "normal row 0"
asset = "Button-row0.png"

[[matchrules.border]]
selector = "normal row 1 pressed"
asset = "Button-row1-press.png"

[[matchrules.border]]
selector = "normal row 1"
asset = "Button-row1.png"

[[matchrules.border]]
selector = "normal row 2 pressed"
asset = "Button-row2-press.png"

[[matchrules.border]]
selector = "normal row 2"
asset = "Button-row2.png"
"""

TAIL_TEMPLATE = """
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
# Asset configs — one entry per image used above. {{key_slicing}}/
# {{space_slicing}} are computed per profile from its own organic
# radius_frac via keycap_render.compute_slicing() (see
# docs/THEME-FORMAT.md "Computing slicing values") -- NOT Groovy Code's
# own values, since each variant draws its own corner shape.
# -------------------------------------------------------------------

[[asset.border]]
name = "Button-morekeysbox.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0.05, 0.28, 0.95, 0.72]
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-morekey.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = [0, 0, 1, 1]
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-default.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-default-press.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-function.png"
background_tint = "#ffffff"
foreground_tint = "{function_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-function-pressed.png"
background_tint = "#ffffff"
foreground_tint = "{function_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-space.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = {space_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-space-press.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = {space_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-action.png"
background_tint = "#ffffff"
foreground_tint = "{action_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-action-press.png"
background_tint = "#ffffff"
foreground_tint = "{action_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-stickyon.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-stickyon-press.png"
background_tint = "#ffffff"
foreground_tint = "{legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640
"""

# Only spliced in for row_banded profiles -- asset blocks for the row0/1/2
# border art the MATCHRULES_ROWBANDED rules above reference.
ASSETS_ROWBANDED = """
[[asset.border]]
name = "Button-row0.png"
background_tint = "#ffffff"
foreground_tint = "{row0_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-row0-press.png"
background_tint = "#ffffff"
foreground_tint = "{row0_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-row1.png"
background_tint = "#ffffff"
foreground_tint = "{row1_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-row1-press.png"
background_tint = "#ffffff"
foreground_tint = "{row1_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-row2.png"
background_tint = "#ffffff"
foreground_tint = "{row2_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640

[[asset.border]]
name = "Button-row2-press.png"
background_tint = "#ffffff"
foreground_tint = "{row2_legend_hex}"
padding = [0, 0, 0, 0]
slicing = {key_slicing}
gap = {gap_list}
target_density = 640
"""

ICON_ASSETS = """
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


def build_theme_txt(row_banded, **kwargs):
    parts = [HEAD_TEMPLATE]
    if row_banded:
        parts.append(MATCHRULES_ROWBANDED)
    parts.append(TAIL_TEMPLATE)
    if row_banded:
        parts.append(ASSETS_ROWBANDED)
    parts.append(ICON_ASSETS)
    return "".join(parts).format(**kwargs)


# ---------------------------------------------------------------------------
# Classic-keyboard profiles (first batch). "Mostly flat" per the user's
# choice: face_function/face_action/face_space default to face_default (no
# color difference at all) unless a profile overrides them -- only
# Commodore 64 (real hardware accent keys) and the stickyon/caps-lock
# state (no on-key equivalent on any of these real keyboards, but required
# for a legible "locked" cue) get real color variation. Each also gets its
# own organic radius_frac/wobble/margin_frac/rim_frac (silhouette
# character) and a motif glyph baked into stickyon + scattered on the
# background (see scripts/keycap_render.py's motif_* functions).
# ---------------------------------------------------------------------------

KEYBOARD_PROFILES = [
    {
        "slug": "ibm-model-m",
        "name": "IBM Model M",
        "theme_id": "com.shelbee.ibmmodelm",
        "reference_note": "the IBM Model M's putty-beige PBT keycaps (Pantone 452C, closest sourced reference) sitting in the keyboard's actual dark charcoal/near-black case -- corrected after a generated reference photo showed the case is NOT a darker shade of the same beige, as this repo had rendered it",
        # NOTE ON CONFIDENCE: unlike Commodore 64 (RAL 1019, well-documented)
        # and Macintosh Plus (Pantone 453C, sourced to Apple's own
        # designer), no search turned up a color spec confirmed specific
        # to the Model M's keycaps. Pantone 452C (hex ~#b0aa7e) remains
        # the best available reference for the beige. The CASE color,
        # however, is unambiguous from any real photo of a Model M
        # (including a generated reference image checked directly): dark
        # charcoal/near-black plastic, not beige at all. This repo's
        # `well` (the visible bezel/recess around each key) had wrongly
        # used a darker shade of the SAME beige family, which reads as a
        # dull monochrome keyboard -- the real thing's defining visual
        # trait is the high-contrast dark case against light keycaps.
        # Fixed by making `well` (and therefore the background, which
        # derives from `well`) actually dark, and `rim` a subtle mid-gray
        # bevel rather than another beige tone.
        "description": "Classic IBM Model M variant: putty-beige PBT keycaps (Pantone 452C) sitting in the keyboard's real dark charcoal case -- corrected from an earlier version that wrongly rendered the case as a darker beige instead of the high-contrast dark plastic real Model M units actually have. Sharp-cornered and thick-bezeled like real buckling-spring PBT caps, with a small switch-stem motif scattered on the background and marking caps-lock. No per-row or per-role color coding (the real keyboard has none) -- only caps-lock brightens and picks up a small amber LED-style glow. Set in FiraCode.",
        # Sharp, boxy, thick-bezeled -- heavy mechanical PBT caps, not
        # glossy plastic. Low wobble: a precision-molded keycap, not a
        # hand-thrown ceramic one.
        "radius_frac": 0.16, "wobble": 0.06, "margin_frac": 0.15, "rim_frac": 0.030,
        "gap": 1.05,
        "face_top_blend": 0.10, "face_bottom_scale": 0.76,
        "well": (32, 32, 35),
        "face_default": (176, 170, 126),
        "face_stickyon": (202, 197, 158),
        "rim": (68, 66, 62),
        "legend": (43, 40, 32),
        "bloom_stickyon_color": (255, 153, 0),
        "bloom_stickyon_alpha": 150,
        "motif_fn": motif_switch_cross,
    },
    {
        "slug": "mac-plus",
        "name": "Macintosh Plus",
        "theme_id": "com.shelbee.macplus",
        "reference_note": "the original Macintosh's actual \"Apple Beige\" (Pantone 453C) case/keyboard color -- not the cooler gray \"Platinum\" this repo originally guessed (a later Apple color the Plus didn't ship in) -- with the keys' real dark switch-plate gaps, not another shade of beige",
        # CORRECTED (round 1): the earlier version of this profile used a
        # cool gray ("Platinum"), Apple's *later* case color introduced
        # with the Macintosh SE/II circa 1987. The Mac Plus (1986)
        # continued the warmer beige of the 128k/512k Macs -- Apple's own
        # designer confirmed the reference color was Pantone 453C
        # (hex ~#bfbb98), widely documented as "Apple Beige."
        # CORRECTED (round 2): a generated reference photo of a real
        # M0110A keyboard showed narrow dark gaps between the low-profile
        # keycaps (the switch plate/mechanism beneath, visible where caps
        # don't fully meet) -- the same finding as IBM Model M. `well`
        # (and the background, which derives from it) had wrongly used a
        # darker shade of the same beige; fixed to actually be dark. The
        # thin `margin_frac`/`rim_frac` already in place happen to be
        # correct for how little of that dark gap actually shows on this
        # keyboard's tightly-packed keys -- only the color was wrong.
        "description": "Classic Macintosh Plus variant: Apple Beige keycaps (Pantone 453C, the real original Mac case color) with the real dark switch-plate showing in the narrow gaps between keys, rounded and thin-bezeled like real low-profile Apple caps, with a small CRT-monitor motif scattered on the background and marking caps-lock. No per-row or per-role color coding (the real keyboard has none) -- only caps-lock brightens and picks up a soft System-blue glow, a small nod to the classic Mac UI highlight color rather than any real on-key indicator. Set in FiraCode.",
        # Low-profile, rounded, minimal: a thin bezel (keys nearly fill
        # the housing) and a nearly-flat face -- smooth and pillowy, not
        # deeply sculpted.
        "radius_frac": 0.42, "wobble": 0.07, "margin_frac": 0.05, "rim_frac": 0.012,
        "gap": 1.1,
        "face_top_blend": 0.08, "face_bottom_scale": 0.90,
        "well": (26, 25, 24),
        "face_default": (191, 187, 152),
        "face_stickyon": (219, 216, 190),
        "rim": (72, 68, 62),
        "legend": (42, 40, 30),
        "bloom_stickyon_color": (91, 127, 166),
        "bloom_stickyon_alpha": 130,
        "motif_fn": motif_crt,
    },
    {
        "slug": "commodore-64",
        "name": "Commodore 64",
        "theme_id": "com.shelbee.commodore64",
        "reference_note": "the Commodore 64 breadbin's real RAL 1019 (\"Grey beige\") case color, with its brown/tan (\"Mustard\") function row and reddish-brown RETURN key",
        # CORRECTED: face_default/well were an invented warm beige/brown
        # that was never checked against a real source. RAL 1019
        # ("Grey beige", hex ~#a48f7a) is the widely-documented real
        # Commodore 64 breadbin color (confirmed across multiple
        # restoration/color-matching sources, e.g. dfarq.homeip.net and
        # Lemon64 threads) -- noticeably grayer and more muted than the
        # cream-beige this repo guessed. well is a darker shade of the
        # same RAL 1019 family rather than an unrelated brown, since the
        # real C64 case is one uniform injection-molded color, not two.
        "description": "Classic Commodore 64 variant: RAL 1019 Grey Beige keycaps (the real, documented breadbin case color) in a darker shade of the same beige, chunky and moderately rounded like real sculpted home-computer caps, with a small IC-chip motif scattered on the background. Brown/tan function-key row (Commodore's own real part color, nicknamed Mustard), a reddish-brown RETURN key, and a bright blue-screen glow on caps-lock. Set in FiraCode.",
        # Chunky sculpted home-computer keys -- moderate rounding, a
        # visible bezel, a fairly pronounced dish. Kept close to a
        # generic "retro computer key" baseline since this is the
        # reference point the other geometries deliberately depart from.
        "radius_frac": 0.26, "wobble": 0.10, "margin_frac": 0.09, "rim_frac": 0.020,
        "gap": 1.15,
        "face_top_blend": 0.16, "face_bottom_scale": 0.80,
        "well": (107, 93, 79),
        "face_default": (164, 143, 122),
        # Real C64 units shipped with either brown/tan ("Mustard",
        # Commodore's own part name) or plain gray F-keys, per lemon64.com
        # forum threads from owners -- never the blue-gray this repo
        # originally invented without checking. Asked the user which real
        # variant to match; they chose brown/tan. (No precise hex found
        # for "Mustard" itself; this is a reasoned tan approximation.)
        "face_function": (154, 118, 62),
        "face_action": (139, 68, 50),
        "face_stickyon": (155, 169, 188),
        "rim": (74, 64, 55),
        "legend": (32, 22, 13),
        "bloom_stickyon_color": (65, 105, 225),
        "bloom_stickyon_alpha": 160,
        "motif_fn": motif_chip,
    },
    {
        "slug": "amber-terminal",
        "name": "Amber Terminal",
        "theme_id": "com.shelbee.amberterminal",
        "reference_note": "a VT100-style terminal's real beige-putty keyboard, with a distinct dark brown/gray function-key row (confirmed via a generated reference photo) and the amber phosphor screen glow carried as its accent color",
        "description": "Amber phosphor terminal variant: beige-putty keycaps -- matching the real VT100-era terminal keyboard's actual color, not the black slab this repo originally guessed -- with a distinct dark taupe function-key row (a real feature of these keyboards, confirmed against a reference photo, not invented), blocky and barely rounded like a flat function-key slab, with a small cursor-prompt motif scattered on the background and marking caps-lock. The amber accent (rim, legends, and the enter/caps-lock glow) is carried over from the CRT's own phosphor color, evoking a lit terminal cursor block. Set in FiraCode.",
        # Blocky and nearly flat -- a terminal function key is a slab
        # behind a wireframe outline, not a sculpted physical cap. Sharp
        # corners, a thin bright rim (the only real detailing), a wider
        # gap for a grid/schematic feel instead of tightly-packed keys.
        "radius_frac": 0.10, "wobble": 0.04, "margin_frac": 0.05, "rim_frac": 0.014,
        "gap": 1.3,
        # A touch more dish depth than the original near-black version --
        # a real beige keycap actually shows its sculpting, where a near-
        # black key could get away with almost none.
        "face_top_blend": 0.08, "face_bottom_scale": 0.88,
        # CONFIDENCE NOTE: no text source gave a precise VT100 case/keycap
        # color spec (unlike C64's RAL 1019 or Mac Plus's Pantone 453C).
        # DEC terminal keyboards of this era are generally recalled as
        # beige/putty plastic, the same "computer beige" family as most
        # 1970s-80s hardware -- this is an informed approximation within
        # that family, not a sourced match. A generated reference photo of
        # a real VT100-style keyboard confirmed this AND surfaced a real
        # feature this repo had missed entirely: the top function-key row
        # is a distinct dark brown/gray, not beige like the rest -- the
        # same "one row gets its own color" pattern the C64 already has.
        # Added `face_function` for that; everything else stays beige.
        "well": (180, 174, 156),
        "face_default": (206, 200, 180),
        "face_function": (72, 66, 58),
        "rim": (255, 176, 0),
        "legend": (140, 74, 0),
        "bloom_action_color": (255, 176, 0),
        "bloom_action_alpha": 90,
        "bloom_stickyon_color": (255, 176, 0),
        "bloom_stickyon_alpha": 210,
        "motif_fn": motif_cursor,
    },
]

# ---------------------------------------------------------------------------
# Classic-console profiles (second batch). Same "match the real hardware"
# principle: Game Boy (DMG), NES, and Game Boy Color are genuinely
# monochrome-button hardware (a colored case at most) so they stay flat,
# each with one small colored accent nodding to a real detail that has no
# on-key equivalent (DMG's red power LED, NES's red logotype, GBC's green
# power LED). SNES was originally the one exception, row-banded to carry
# a four-color Y/X/A/B scheme -- but that scheme turned out to be the
# Japanese/European Super Famicom's colors, not the real North American
# SNES controller's (which has only two button colors, purple + lavender,
# no rainbow). Corrected to match the real NA hardware and folded back
# into this flat-with-an-accent-key family; see its own profile below for
# the full correction note.
#
# CONFIDENCE NOTE for this whole batch: unlike Commodore 64 (RAL 1019) and
# Macintosh Plus (Pantone 453C), no search turned up a precise sourced hex
# for the Game Boy (DMG), NES, or Game Boy Color's actual shell/button
# colors -- these three remain informed approximations from general
# recollection/community consensus, not confirmed against a real spec.
# ---------------------------------------------------------------------------

CONSOLE_PROFILES = [
    {
        "slug": "gameboy-dmg",
        "name": "Game Boy",
        "theme_id": "com.shelbee.gameboydmg",
        "reference_note": "the original Game Boy (DMG)'s putty-gray shell and dark gray buttons (approximated -- no sourced hex found)",
        "description": "Classic Game Boy (DMG) variant: dark gray buttons in a putty-gray shell, chunky and thick-bezeled like real molded plastic buttons, with a small D-pad-cross motif scattered on the background and marking caps-lock. No per-row or per-role color coding (the real hardware has none) -- only caps-lock brightens and picks up the console's own red power-LED glow. Set in FiraCode.",
        # Chunky molded plastic buttons sitting in a thick shell bezel --
        # the DMG's brick-like housing is the most visible "well" of any
        # variant here.
        "radius_frac": 0.30, "wobble": 0.09, "margin_frac": 0.14, "rim_frac": 0.020,
        "gap": 1.2,
        "face_top_blend": 0.12, "face_bottom_scale": 0.80,
        "well": (196, 190, 164),
        "face_default": (58, 58, 56),
        "face_stickyon": (75, 75, 72),
        "rim": (90, 88, 78),
        "legend": (230, 224, 200),
        "bloom_stickyon_color": (210, 30, 30),
        "bloom_stickyon_alpha": 170,
        "motif_fn": motif_dpad,
    },
    {
        "slug": "nes",
        "name": "NES",
        "theme_id": "com.shelbee.nes",
        "reference_note": "the Nintendo Entertainment System controller's light gray shell and near-black D-pad/buttons (approximated -- no sourced hex found)",
        "description": "Classic NES variant: near-black D-pad and buttons in a light gray shell, minimally rounded like the real controller's famously rectangular buttons, with a small twin-button motif scattered on the background. No per-row or per-role color coding (the real controller has none) -- only the action key and caps-lock pick up a soft red glow, a nod to the console's red logotype rather than any real on-button indicator. Set in FiraCode.",
        # The NES controller's buttons are famously rectangular, not
        # round -- minimal corner rounding here, a moderate bezel.
        "radius_frac": 0.13, "wobble": 0.05, "margin_frac": 0.11, "rim_frac": 0.020,
        "gap": 1.15,
        "face_top_blend": 0.10, "face_bottom_scale": 0.82,
        "well": (184, 184, 178),
        "face_default": (43, 43, 43),
        "rim": (140, 140, 134),
        "legend": (224, 224, 218),
        "bloom_action_color": (224, 32, 32),
        "bloom_action_alpha": 80,
        "bloom_stickyon_color": (224, 32, 32),
        "bloom_stickyon_alpha": 180,
        "motif_fn": motif_button_pair,
    },
    {
        "slug": "snes",
        "name": "SNES",
        "theme_id": "com.shelbee.snes",
        "reference_note": "the real North American SNES controller (SNS-005)'s warm gray-lavender body and its actual purple A/B + lavender X/Y buttons",
        # CORRECTED: this variant originally used the green/blue/yellow/red
        # Y/X/A/B scheme, which is the Japanese/European Super Famicom's
        # colors, not the North American SNES's -- confirmed via research
        # (a real mistake this repo made and hadn't checked). The real NA
        # SNS-005 controller has only two button colors: purple (A/B,
        # convex) and lavender (X/Y, concave), on a warm gray-lavender
        # body -- no per-row rainbow at all. Hex approximations below are
        # community-sourced (color-hex.com's "US Super Nintendo SNES Color
        # Palette"), not an official Nintendo spec, but far closer to the
        # real hardware than the invented rainbow was. Dropped
        # "row_banded" entirely as a result -- two button colors don't
        # map onto three letter-rows, so this is now flat-with-an-accent-
        # key like the other console variants, not a special case.
        "description": "Classic SNES variant, corrected to match the real North American controller (SNS-005): a warm gray-lavender body, lavender-purple keys (matching the concave X/Y buttons), and a darker purple action/enter key (matching the convex A/B buttons) -- not the green/blue/yellow/red rainbow, which is actually the Japanese/European Super Famicom's color scheme, not the NA SNES's. Rounded and glossy like the real concave buttons, with a small two-tone diamond motif scattered on the background. Set in FiraCode.",
        # Rounded, glossy, concave buttons sitting almost flush in the
        # housing -- the roundest radius and thinnest bezel of any
        # variant, plus a brighter top-blend for a glossier sheen than
        # the plastic-matte look everything else here goes for.
        "radius_frac": 0.44, "wobble": 0.09, "margin_frac": 0.05, "rim_frac": 0.012,
        "gap": 1.05,
        "face_top_blend": 0.22, "face_bottom_scale": 0.78,
        "well": (206, 201, 204),
        "face_default": (167, 164, 224),
        "face_action": (81, 70, 137),
        "face_stickyon": (225, 222, 240),
        "rim": (144, 138, 153),
        "legend": (28, 26, 36),
        "bloom_stickyon_color": (81, 70, 137),
        "bloom_stickyon_alpha": 140,
        "motif_fn": motif_diamond_cluster,
        "motif_kwargs": {"colors": [(81, 70, 137), (167, 164, 224), (81, 70, 137), (167, 164, 224)]},
    },
    {
        "slug": "gameboy-color",
        "name": "Game Boy Color",
        "theme_id": "com.shelbee.gameboycolor",
        "reference_note": "the Game Boy Color's grape-purple shell and dark violet buttons (approximated -- no sourced hex found; \"Grape\" was also a specific real GBC colorway name, not just a generic description, worth double-checking against a reference photo before calling this confirmed)",
        "description": "Classic Game Boy Color variant: dark violet-gray buttons in a deep grape-purple shell, more rounded and softer-bezeled than the original DMG (matching its real, more ergonomic redesign), with a small D-pad-cross motif scattered on the background. No per-row or per-role color coding (the real hardware has none) -- only caps-lock brightens and picks up the console's own green power-LED glow (versus the original Game Boy's red one). Set in FiraCode.",
        # More rounded and curved than the boxy original DMG (the GBC's
        # shell is a noticeably softer, more ergonomic redesign) but not
        # as thick-bezeled -- a middle ground between DMG and SNES.
        "radius_frac": 0.34, "wobble": 0.10, "margin_frac": 0.13, "rim_frac": 0.020,
        "gap": 1.15,
        "face_top_blend": 0.14, "face_bottom_scale": 0.80,
        "well": (74, 47, 94),
        "face_default": (58, 42, 74),
        "face_stickyon": (78, 58, 98),
        "rim": (138, 107, 168),
        "legend": (232, 221, 240),
        "bloom_stickyon_color": (40, 200, 90),
        "bloom_stickyon_alpha": 170,
        "motif_fn": motif_dpad,
    },
]

PROFILES = KEYBOARD_PROFILES + CONSOLE_PROFILES


def build_background(well, motif_fn, motif_color, motif_kwargs=None, seed=1):
    """A soft gradient plate scattered with the theme's own motif glyph,
    low-alpha -- the same role Animal Keys' paw-print wood background
    plays for itself."""
    top = tuple(min(255, c + 25) for c in well)
    bottom = scale(well, 0.6)
    bg = vertical_gradient(BACKGROUND_SIZE, top, bottom).convert("RGBA")
    if motif_fn is not None:
        layer = scatter_motifs(
            BACKGROUND_SIZE, motif_fn, motif_color, count=22, seed=seed,
            alpha=40, scale_frac=(0.018, 0.032), **(motif_kwargs or {}),
        )
        bg.alpha_composite(layer)
    return bg.convert("RGB")


def generate_variant(profile):
    slug = profile["slug"]
    out_dir = os.path.join(VARIANTS_DIR, slug)
    # Wipe and recreate rather than just os.makedirs(exist_ok=True) -- a
    # profile that drops row_banded (as SNES did, corrected to match real
    # NA hardware) would otherwise leave its old Button-row0/1/2*.png
    # orphaned in the directory, unreferenced by the new theme.txt but
    # still shipped in the package zip.
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir, exist_ok=True)

    well = profile["well"]
    rim = profile["rim"]
    legend = profile["legend"]
    face_default = profile["face_default"]
    face_function = profile.get("face_function", face_default)
    face_action = profile.get("face_action", face_default)
    face_space = profile.get("face_space", face_default)
    face_stickyon = profile.get("face_stickyon", face_default)
    row_banded = profile.get("row_banded", False)
    row_faces = profile.get("row_faces", {})

    action_bloom_color = profile.get("bloom_action_color")
    action_bloom_alpha = profile.get("bloom_action_alpha", 0)
    stickyon_bloom_color = profile.get("bloom_stickyon_color")
    stickyon_bloom_alpha = profile.get("bloom_stickyon_alpha", 0)

    motif_fn = profile.get("motif_fn")
    motif_kwargs = profile.get("motif_kwargs")

    # Geometry/material knobs -- shape, bezel thickness, rim weight, and
    # gradient contrast are what make each variant an actual distinct
    # theme (an organic silhouette + material finish of its own) rather
    # than Groovy Code's shape with new paint.
    radius_frac = profile.get("radius_frac", 0.30)
    wobble = profile.get("wobble", 0.09)
    geo = dict(
        margin_frac=profile.get("margin_frac", 0.09),
        rim_frac=profile.get("rim_frac", 0.018),
        well_top_blend=profile.get("well_top_blend", 0.10),
        well_bottom_scale=profile.get("well_bottom_scale", 0.72),
        face_top_blend=profile.get("face_top_blend", 0.14),
        face_bottom_scale=profile.get("face_bottom_scale", 0.82),
    )
    gap = profile.get("gap", 1.15)

    def rk(size, seed, face, **kw):
        return render_organic_key(size, seed, face, well, rim, radius_frac=radius_frac, wobble=wobble, **geo, **kw)

    def save(name, img):
        img.save(os.path.join(out_dir, name))

    save("Button-default.png", rk(KEY_SIZE, 10, face_default))
    save("Button-default-press.png", rk(KEY_SIZE, 1010, face_default, pressed=True))

    save("Button-function.png", rk(KEY_SIZE, 40, face_function))
    save("Button-function-pressed.png", rk(KEY_SIZE, 1040, face_function, pressed=True))

    save("Button-action.png", rk(
        KEY_SIZE, 60, face_action,
        bloom_alpha=action_bloom_alpha, bloom_color=action_bloom_color, bloom_pad_frac=0.04,
    ))
    save("Button-action-press.png", rk(KEY_SIZE, 1060, face_action, pressed=True))

    save("Button-space.png", rk(SPACE_SIZE, 70, face_space, stabilizers=True))
    save("Button-space-press.png", rk(SPACE_SIZE, 1070, face_space, pressed=True, stabilizers=True))

    save("Button-stickyon.png", rk(
        KEY_SIZE, 80, face_stickyon,
        bloom_alpha=stickyon_bloom_alpha, bloom_color=stickyon_bloom_color, bloom_pad_frac=0.05,
        motif_fn=motif_fn, motif_color=rim, motif_alpha=140, motif_kwargs=motif_kwargs,
    ))
    save("Button-stickyon-press.png", rk(KEY_SIZE, 1080, face_stickyon, pressed=True))

    row_legends = {}
    if row_banded:
        for row_idx, row_face in row_faces.items():
            save(f"Button-row{row_idx}.png", rk(KEY_SIZE, 100 + row_idx, row_face))
            save(f"Button-row{row_idx}-press.png", rk(KEY_SIZE, 1100 + row_idx, row_face, pressed=True))
            row_legends[f"row{row_idx}_legend_hex"] = hexs(profile.get(f"row{row_idx}_legend", legend))

    background_file = f"{slug}-background.png"
    build_background(well, motif_fn, rim, motif_kwargs, seed=5).save(os.path.join(out_dir, background_file))

    for fname in SHARED_FILES:
        shutil.copy(os.path.join(REPO_ROOT, fname), os.path.join(out_dir, fname))

    function_legend = profile.get("function_legend", legend)
    action_legend = profile.get("action_legend", legend)

    key_slicing = compute_slicing(radius_frac, KEY_SIZE)
    space_slicing = compute_slicing(radius_frac, SPACE_SIZE)
    roundedness = round(min(0.95, max(0.15, radius_frac * 2.1)), 2)

    theme_txt = build_theme_txt(
        row_banded,
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
        key_slicing=key_slicing,
        space_slicing=space_slicing,
        gap_list=[gap, gap, gap, gap],
        roundedness=roundedness,
        **row_legends,
    )
    with open(os.path.join(out_dir, "theme.txt"), "w") as f:
        f.write(theme_txt)

    print(f"wrote variants/{slug}/ ({len(os.listdir(out_dir))} files)")


def main():
    for profile in PROFILES:
        generate_variant(profile)


if __name__ == "__main__":
    main()
