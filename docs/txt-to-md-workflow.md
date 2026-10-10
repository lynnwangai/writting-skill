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

The command stops after faithful conversion. `SKILL.md` is the authoritative
semantic layer: Codex reads the whole article, classifies its structure, and
performs a restrained editorial-emphasis pass using exact source wording. The
emphasis pass selects the central thesis, key distinctions or reversals,
section-level conclusions, and final synthesis; it does not apply bolding by a
fixed quota. When the source ends with an author self-introduction or sign-off,
the semantic pass preserves its wording and emits `<!-- author-signoff -->`
followed by a `>` blockquote immediately before references.

For a Markdown-only request, Codex returns the semantic `rendered.md` for human
review at that point. For a card request, it continues with page markers,
proposes the cover split and color roles, runs the non-rendering `--preflight`
density check, and returns that exact review draft. Final PNG rendering waits
for explicit approval of the cover, emphasis, color, and pagination in that file.

Before preflight, run `scripts/paginate_article.py` on the semantically reviewed
Markdown. It replaces provisional page markers using real browser measurements,
sentence-safe prose splitting, protected semantic atoms, and deterministic tail
balancing. Manual boundary shuffling is a fallback only when the command reports
a specific protected atom that cannot satisfy both fit and density constraints.

The review draft must place content as one continuous flow. Preflight requires
every body page except the final one to fill at least 75% of its available
content height. When moving one adjacent boundary is not enough, rebalance page
boundaries across the full article. `section_intro`, CTA, and non-final reference
pages are not density exceptions.

If the reviewed `title` or cover copy differs from the source file's first-line
title, preserve the original line in front matter as `source_title`. Do not edit
the source snapshot to make reconciliation pass.

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
