#!/usr/bin/env python3
"""Generate Groovy Code's Button-*.png keycap assets (Pillow + numpy).

v19: organic "cookie"-shaped keys, replacing v12-v18's rounded-rectangle
well+face+rim structure. Prompted by the user's explicit direction after
seeing a real published FUTO theme, "Animal Keys" by TrashKittyQueen
(downloaded from https://keyboard.futo.tech/themes and inspected
directly) -- its actual technique is irregular, organic key silhouettes
(not clean rounded rects) plus a small motif glyph on accent keys and
scattered subtly across the background. Asked directly how far to take
this (all 9 themes here, vs. just the 8 hardware variants, given Groovy
Code had JUST been fixed in v18 to match its own reference SVG's clean
rounded rects) -- the user chose all 9. So Groovy Code's key SILHOUETTE
moves away from that SVG's literal vector rounded-rect shape here; its
COLOR identity (uniform orange, rust enter key, gold caps-lock) is what
"matches the reference" going forward, unchanged from v18 and still the
right target -- see docs/GROOVY-CODE-THEME.md's v19 entry for the full
reasoning.

The organic silhouette (`render_organic_key`, `organic_mask`) and motif
glyphs live in scripts/keycap_render.py, shared with the classic-hardware
variant themes in variants/ (see scripts/generate_variants.py) -- this
file just supplies Groovy Code's own palette, motif choice (a small 70's
sunburst -- see `motif_sunburst`), and per-asset role mapping.

Deliberately does NOT touch Icon-*.png, Button-morekey.png, or
Button-morekeysbox.png -- the icon-regeneration regression documented in
docs/GROOVY-CODE-THEME.md happened because a full regen run silently
clobbered hand-picked icon art. Keeping icons entirely outside this
script's reach makes that class of bug impossible, not just avoided.
"""

from keycap_render import (
    KEY_SIZE, SPACE_SIZE, blend_white, motif_sunburst, render_organic_key,
    scatter_motifs, vertical_gradient, scale,
)

BACKGROUND_SIZE = (1080, 1080)

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
SEEDS = {"Button-default": 10, "Button-space": 70, "Button-function": 40}


def main():
    for name in FLAT_KEYS:
        size = SPACE_SIZE if name == "Button-space" else KEY_SIZE
        stabilizers = name == "Button-space"
        seed = SEEDS[name]

        normal = render_organic_key(size, seed, ORANGE, BROWN, GOLD, stabilizers=stabilizers)
        normal.save(f"{name}.png")

        pressed = render_organic_key(size, seed + 1000, ORANGE, BROWN, GOLD, pressed=True, stabilizers=stabilizers)
        pressed.save(f"{name}{PRESSED_SUFFIX[name]}.png")
        print(f"wrote {name}.png / {name}{PRESSED_SUFFIX[name]}.png")

    # Action (enter): rust face, matching the reference's rust-red enter
    # key against everything else's orange -- plus a modest bloom so it
    # still reads as the primary accent key at rest.
    action = render_organic_key(KEY_SIZE, 60, RUST, BROWN, GOLD, bloom_alpha=90, bloom_pad_frac=0.04)
    action.save("Button-action.png")

    action_press = render_organic_key(KEY_SIZE, 1060, RUST, BROWN, GOLD, pressed=True)
    action_press.save("Button-action-press.png")
    print("wrote Button-action.png / Button-action-press.png")

    # stickyon (caps-lock engaged): the reference has no locked state to
    # match, so this stays interpretive -- brightest gold face, the
    # biggest bloom, and a small brown sunburst motif (this theme's own
    # signature glyph, its "70's groovy" identity) baked right into the
    # face, unmistakably "on." Gold is exclusive to this key now that
    # functional keys are back to plain orange (since v18).
    stickyon = render_organic_key(
        KEY_SIZE, 80, blend_white(GOLD, 0.10), BROWN, GOLD,
        bloom_alpha=150, bloom_pad_frac=0.05,
        motif_fn=motif_sunburst, motif_color=BROWN, motif_alpha=130,
    )
    stickyon.save("Button-stickyon.png")

    stickyon_press = render_organic_key(
        KEY_SIZE, 1080, blend_white(GOLD, 0.10), BROWN, GOLD, pressed=True
    )
    stickyon_press.save("Button-stickyon-press.png")
    print("wrote Button-stickyon.png / Button-stickyon-press.png")

    # Background: a brown gradient plate scattered with small sunburst
    # motifs, matching the same technique now used for every classic-
    # hardware variant (see scripts/generate_variants.py's
    # build_background) -- replaces the old plain dark texture so Groovy
    # Code isn't the one theme in this repo without its own motif on the
    # background.
    bg_top = tuple(min(255, c + 20) for c in BROWN)
    bg_bottom = scale(BROWN, 0.55)
    background = vertical_gradient(BACKGROUND_SIZE, bg_top, bg_bottom).convert("RGBA")
    background.alpha_composite(
        scatter_motifs(BACKGROUND_SIZE, motif_sunburst, GOLD, count=20, seed=5, alpha=40, scale_frac=(0.018, 0.032))
    )
    background.convert("RGB").save("GroovyCode-background.png")
    print("wrote GroovyCode-background.png")


if __name__ == "__main__":
    main()
