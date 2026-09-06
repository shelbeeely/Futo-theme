#!/usr/bin/env python3
"""Generate Groovy Code's Button-*.png keycap assets (Pillow only).

v17: solid colorful keycaps -- brown "well" body, a bright inset face color
per key role, and a thin gold rim stroke right at the boundary between them.
Replaces v15/v16's dark-charcoal-single-surface-plus-tiny-glow look entirely,
per the user's explicit direction after seeing a new reference: an SVG
illustration of a mechanical keyboard with solid orange keycaps, a gold rim,
a visible inset face on every key (not just system keys), and a rust-red
enter key. Asked directly which way to go (keep v16's dark look, blend, or
revert) -- the user chose reverting to solid colorful keys.

The actual rendering (`render_key` and its geometry constants) now lives in
scripts/keycap_render.py, shared with the classic-keyboard variant themes in
variants/ (see scripts/generate_variants.py) -- this file just supplies
Groovy Code's own palette and per-asset role mapping.

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

from keycap_render import KEY_SIZE, KEY_RADIUS, SPACE_SIZE, SPACE_RADIUS, blend_white, render_key

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
        normal = render_key(KEY_SIZE, KEY_RADIUS, face, BROWN, GOLD)
        normal.save(f"{name}.png")

        pressed = render_key(KEY_SIZE, KEY_RADIUS, face, BROWN, GOLD, pressed=True)
        pressed.save(f"{name}{PRESSED_SUFFIX[name]}.png")
        print(f"wrote {name}.png / {name}{PRESSED_SUFFIX[name]}.png")

    # Action (enter): true rust face, matching the reference's rust-red
    # enter key against everything else's orange/gold -- plus a modest
    # bloom so it still reads as the primary accent key at rest.
    action = render_key(KEY_SIZE, KEY_RADIUS, RUST, BROWN, GOLD, bloom_alpha=90, bloom_pad=7)
    action.save("Button-action.png")

    action_press = render_key(KEY_SIZE, KEY_RADIUS, RUST, BROWN, GOLD, pressed=True)
    action_press.save("Button-action-press.png")
    print("wrote Button-action.png / Button-action-press.png")

    # Spacebar: plain clay face, no bloom, with stabilizer-stem dimples.
    space = render_key(SPACE_SIZE, SPACE_RADIUS, CLAY, BROWN, GOLD, stabilizers=True)
    space.save("Button-space.png")

    space_press = render_key(
        SPACE_SIZE, SPACE_RADIUS, CLAY, BROWN, GOLD, pressed=True, stabilizers=True
    )
    space_press.save("Button-space-press.png")
    print("wrote Button-space.png / Button-space-press.png")

    # stickyon (caps-lock engaged): the brightest, most bloomed gold face on
    # the board -- unmistakably "on," continuing the "gold = locked" cue.
    stickyon = render_key(
        KEY_SIZE, KEY_RADIUS, blend_white(GOLD, 0.10), BROWN, GOLD,
        bloom_alpha=150, bloom_pad=9,
    )
    stickyon.save("Button-stickyon.png")

    stickyon_press = render_key(
        KEY_SIZE, KEY_RADIUS, blend_white(GOLD, 0.10), BROWN, GOLD, pressed=True
    )
    stickyon_press.save("Button-stickyon-press.png")
    print("wrote Button-stickyon.png / Button-stickyon-press.png")


if __name__ == "__main__":
    main()
