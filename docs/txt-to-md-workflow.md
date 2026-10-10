# TXT → Markdown workflow

Put finished UTF-8 `.txt` articles in `inputs/`. The converter creates a new,
versioned run directory and never overwrites an earlier run.

## Convert an article

From the project root:

```sh
.venv/bin/python scripts/txt_to_md.py inputs/my-article.txt \
  --title "文章标题" \
  --series-label "社会观察" \
  --footer-label "POWER & BEHAVIOR"
```

Optional cover metadata:

```sh
--subtitle "可选副标题"
```

The command prints the generated Markdown path. By default it writes:

```text
output/<article-slug>/<UTC-run-id>/
├── rendered.md
└── conversion.json
```

`rendered.md` contains renderer-compatible YAML front matter followed by the
article body. `conversion.json` records source/output hashes and every mechanical
transformation. By default the converter performs no semantic classification and
does not rewrite, summarize, reorder, or paginate the article.

The normal Codex workflow stops after faithful conversion. `SKILL.md` is the
authoritative semantic layer: Codex reads the whole article, adds semantic
Markdown and page markers, proposes the cover split, and waits for approval.

An older conservative regex pass remains available for compatibility:

```sh
.venv/bin/python scripts/txt_to_md.py inputs/my-article.txt \
  --title "文章标题" \
  --infer-structure
```

`--infer-structure` recognizes explicit Chinese numbered section headings, numbered
subsections, standalone quotations, selected parallel lists, and a small number
of high-confidence emphasis lines. It only adds Markdown punctuation; it does
not rewrite or reorder wording. Review these classifications before rendering.

Do not use it when Codex is applying `SKILL.md`; running both creates competing
semantic layers. The reviewed syntax is documented in `docs/semantic-markdown.md`.

## Reproducible path for tests

Pass a fixed run identifier when a stable path is useful:

```sh
.venv/bin/python scripts/txt_to_md.py inputs/my-article.txt \
  --title "文章标题" \
  --run-id manual-test
```

If that directory already exists, the command stops instead of replacing it.

## Render the approved article

After `rendered.md` contains the approved cover fields and one semantic page
marker per body card, run the canonical renderer:

```sh
.venv/bin/python scripts/render_article.py \
  output/<article-slug>/<run-id>/rendered.md \
  --source-txt inputs/my-article.txt
```

The renderer produces the cover, zero-padded body cards, manifest, and contact
sheet. It uses local/system fonts, refuses to overwrite prior render artifacts,
checks source-text preservation, detects overflow, and validates every card at
exactly 1080×1440.
