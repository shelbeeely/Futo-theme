# Futo-theme

**Groovy Code** — a custom [FUTO Keyboard](https://keyboard.futo.tech/) (Android)
theme: a warm-toned 70's palette (gold/orange/rust/brown) with an orange
accent, set in FiraCode. The repo root is the theme package itself —
`theme.txt` plus PNG assets plus the font, ready to zip and sideload into the
FUTO Keyboard app's theme importer.

## Getting the importable zip

Every push to `main` that touches theme files runs
[`.github/workflows/package-theme.yml`](.github/workflows/package-theme.yml),
which zips up just the theme package (leaving out `docs/`, `scripts/`, and
this repo's own dev docs) and publishes it two ways:

- **Releases** (recommended) — a permanent link at this repo's Releases
  page, tagged `vN` to match `theme.txt`'s `version`. Download the `.zip`
  from there and import it in FUTO Keyboard's theme importer.
- **Actions artifact** — attached to the workflow run itself, if you'd
  rather grab a specific commit's build without waiting for a release.

You can also trigger a build on demand from the Actions tab
("Package theme" → "Run workflow") without pushing a new commit.

## Docs

- [`docs/THEME-FORMAT.md`](docs/THEME-FORMAT.md) — reference for the FUTO
  `theme.txt` format itself (verified from the
  [`keyboard-theme-editor`](https://github.com/futo-org/keyboard-theme-editor)
  source), applicable to any FUTO theme, not just this one.
- [`docs/GROOVY-CODE-THEME.md`](docs/GROOVY-CODE-THEME.md) — this theme's
  design system, build workflow, fixed-bug history, and open items.
- [`docs/MECHANICAL-KEYBOARD-GUIDE.md`](docs/MECHANICAL-KEYBOARD-GUIDE.md) —
  notes on pushing a theme further toward a mechanical/desktop-keyboard
  look within what the format supports.

See also `CLAUDE.md` for the working notes an AI assistant should read
before continuing work on this repo.

## Previewing changes without a device

`.claude/skills/preview-theme/` renders a real preview of the theme using
FUTO's own [`keyboard-theme-editor`](https://github.com/futo-org/keyboard-theme-editor)
rendering code, run locally and driven headlessly — so a visual change to
`theme.txt` or the generated assets can be checked before ever needing to
sideload onto an Android device. See its `SKILL.md` for usage.
