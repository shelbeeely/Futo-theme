#!/usr/bin/env python3
"""Generate Groovy Code's Button-*.png keycap assets (Pillow only).

v18: matches the actual reference SVG exactly, correcting a divergence
v17 introduced. The reference ("Mechanical keyboard illustration in a
warm 70s palette") shows every single key -- every number, every letter
across all three rows, shift, backspace, ?123, comma, emoji, spacebar,
period -- rendered in the *same* solid orange (#e17a25) with a gold rim
and a dark brown (#422118) legend. The ONLY key that differs is Enter,
which is rust (#bd361e) with a cream arrow. There is no row-banding and
no separate "gold system key" color anywhere in the reference.

v17 misread this: it brought back row-banded per-row colors (orange-red/
orange/brightened-rust) and a gold face for functional keys, reasoning
that the user's chosen option text ("closer to the old v10-v13 look")
justified departing from the reference's literal uniform orange. Checked
directly against the actual SVG (rendered to PNG and compared side by
side with a `preview-theme` render), that departure was wrong -- the
user said the result looked nothing like the reference, which it didn't:
current live comparison in this repo's history showed row-banded
orange-red/orange/salmon keys and gold shift/backspace/?123/comma/emoji
keys, none of which the reference has anywhere. v18 fixes this by making
every non-action, non-stickyon key literally the same orange -- default,
functional, and spacebar all render identically now, matching the
reference's own repeated identical `<use href="#k">` pattern. Stickyon
(caps-lock) has no reference in the static SVG (it only shows the idle
state) so it keeps the pre-existing interpretive gold treatment -- gold
is now free for this exclusive use since it's no longer spent on
functional keys.

The actual rendering (`render_key` and its geometry constants) lives in
scripts/keycap_render.py, shared with the classic-hardware variant themes
in variants/ (see scripts/generate_variants.py) -- this file just
supplies Groovy Code's own palette and per-asset role mapping.

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
# of these seven; nothing outside this palette is used.
# ---------------------------------------------------------------------------

GOLD = (225, 157, 37)  # #e19d25
ORANGE = (225, 122, 37)  # #e17a25 -- every key on the board except action/stickyon
RUST = (189, 54, 30)  # #bd361e -- the action/enter key, matching the reference exactly
BROWN = (135, 71, 37)  # #874725 -- the outer "well" body color for every key

FLAT_KEYS = ["Button-default", "Button-space", "Button-function"]
PRESSED_SUFFIX = {"Button-default": "-press", "Button-space": "-press", "Button-function": "-pressed"}


def main():
    for name in FLAT_KEYS:
        size = SPACE_SIZE if name == "Button-space" else KEY_SIZE
        radius = SPACE_RADIUS if name == "Button-space" else KEY_RADIUS
        stabilizers = name == "Button-space"

        normal = render_key(size, radius, ORANGE, BROWN, GOLD, stabilizers=stabilizers)
        normal.save(f"{name}.png")

        pressed = render_key(size, radius, ORANGE, BROWN, GOLD, pressed=True, stabilizers=stabilizers)
        pressed.save(f"{name}{PRESSED_SUFFIX[name]}.png")
        print(f"wrote {name}.png / {name}{PRESSED_SUFFIX[name]}.png")

    # Action (enter): rust face, matching the reference's rust-red enter
    # key against everything else's orange -- plus a modest bloom so it
    # still reads as the primary accent key at rest.
    action = render_key(KEY_SIZE, KEY_RADIUS, RUST, BROWN, GOLD, bloom_alpha=90, bloom_pad=7)
    action.save("Button-action.png")

    action_press = render_key(KEY_SIZE, KEY_RADIUS, RUST, BROWN, GOLD, pressed=True)
    action_press.save("Button-action-press.png")
    print("wrote Button-action.png / Button-action-press.png")

    # stickyon (caps-lock engaged): the reference has no locked state to
    # match, so this stays an interpretive choice -- brightest gold face
    # plus the biggest bloom, unmistakably "on." Gold is exclusive to this
    # key now that functional keys are back to plain orange.
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
