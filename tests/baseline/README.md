# Untouched upstream baseline

This directory records the first successful local render of the vendored
`cnfjlhj/xhs-note-creator` example. No renderer, example content, template, or
theme was changed before this capture.

## Provenance

- Repository: <https://github.com/cnfjlhj/xhs-note-creator>
- Commit: `ac61b840cbe3b378effd46484c1d92f697372a0d`
- Snapshot date: 2026-10-09
- Vendored source: `vendor/xhs-note-creator/`
- Provenance note: `vendor/xhs-note-creator/UPSTREAM.md`

## Command

Run from the project root:

```sh
.venv/bin/python vendor/xhs-note-creator/scripts/render_xhs.py \
  vendor/xhs-note-creator/assets/example.md \
  -m auto-split \
  -o tests/baseline/upstream
```

The upstream program reported a 1080×1440 canvas and generated one cover plus
four body cards. The physical PNG files are actually 2160×2880 because the
documented Python renderer defaults to device scale factor 2.

## Environment

- macOS 14.1 (arm64)
- Python 3.14.4
- Playwright 1.63.0
- Chromium/Chrome for Testing 153.0.8010.12 (Playwright build v1243)
- Markdown 3.11
- PyYAML 6.0.3
- Direct Playwright dependencies: greenlet 3.5.6, pyee 13.0.1,
  typing_extensions 4.16.0

Publishing dependencies from the upstream `requirements.txt` were deliberately
not installed. In particular, `xhs`, `python-dotenv`, and `requests` are not
required for local rendering.

The renderer's computed font stack was `Noto Sans SC`, `Source Han Sans CN`,
`PingFang SC`, `Microsoft YaHei`, then `sans-serif`. At capture time Chromium
reported both `Noto Sans SC` and `PingFang SC` as available, but the stylesheet
still contains a Google Fonts import. That remote dependency must be removed
before claiming offline determinism.

## Artifacts

- `contact-sheet.png` — review sheet assembled from the raw outputs
- `upstream/cover.png` — untouched upstream cover
- `upstream/card_1.png` through `upstream/card_4.png` — untouched upstream body
  cards

All five raw images are 2160×2880 pixels.

| File | SHA-256 |
| --- | --- |
| `cover.png` | `93a2c746478dfa6f7f7bb9e647ac0b75f9f142b78977e7c24461763d0f942c5c` |
| `card_1.png` | `2e007d471961f6d386231c3903f9c40fb413460de98d0c16ea53e0171abb5e92` |
| `card_2.png` | `dd169928184c546811088cf12efcc12569f7b1a3e781383f897463bb2dfa679b` |
| `card_3.png` | `6272bd10a1d5875764852328c0c94aaff7cdc585e337b8977e3cc1d34fcc75f4` |
| `card_4.png` | `d8a2a2714e23c23e56fca8a2fb60ffb2d5b1ace4e94cea17d05a3240b97c518a` |

## Visual observations

- The example renders successfully and is readable.
- The cover is a generic gradient/emoji treatment rather than the supplied
  typography-led editorial reference.
- Card 1 ends with the orphan heading “新粗野主义风格 ⚡”.
- Card 2 starts that section's body and later starts “植物园风格”, so the page
  break does not preserve a coherent section unit.
- Card 3 begins with a blockquote carried over from the preceding section and
  then starts a new section.
- The layout is visually sparse and uses one generic content treatment rather
  than semantic layouts for frameworks, comparisons, callouts, and references.

These are baseline observations only. Nothing in this directory attempts to
fix them.
