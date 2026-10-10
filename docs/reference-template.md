# Reference-matched editorial template

The active visual reference is `references/screenshots/cover-editorial-reference.png`
plus the body-card screenshots in the same directory. It supersedes the earlier
muted-blue typography cover direction.

## Visual system

- Exact 1080×1440 canvas at DPR 1
- Warm white paper and near-black Chinese type
- Brick-red primary accent for series metadata, cover emphasis, heading bars,
  underlines, numbered frameworks, and rules
- Muted blue reserved for occasional callouts
- Heavy, condensed-feeling cover hierarchy with explicit lead, focal word,
  bridge, and red-emphasis fields
- Configurable series/topic kicker and a subtitle block below the title rule
- Generous body margins, large line height, minimal decoration, and page-number
  footer
- Reusable prose, numbered-framework, and two-column comparison primitives
- Local/system fonts only; no remote runtime assets

## Active renderer

`scripts/render_article.py` is the canonical renderer. It reads the reviewed
semantic Markdown format in `docs/semantic-markdown.md` and uses the cover/card
templates and shared CSS below.

The older proof renderer remains only as design history. The end-to-end fixture
is `tests/article-render/sample.md`, with its review sheet at
`tests/article-render/contact-sheet.png`.

## Historical proof files

- Editable proof content: `tests/reference-proof/sample-pages.json`
- Cover template: `assets/templates/editorial-reference-cover.html`
- Body template: `assets/templates/editorial-reference-card.html`
- Shared theme: `assets/themes/editorial-reference.css`
- Proof renderer: `scripts/render_reference_proof.py`
- Review sheet: `tests/reference-proof/contact-sheet.png`

Re-render from the project root:

```sh
.venv/bin/python scripts/render_reference_proof.py
```

The proof renderer validates every card at exactly 1080×1440 and fails on canvas
overflow. It was the visual approval artifact used before the semantic Markdown
renderer was connected.
