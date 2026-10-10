# RedNote Longform Editorial Renderer

A local workflow for turning a finished Chinese analytical article into reviewed RedNote/Xiaohongshu image cards without re-typesetting it by hand.

The article remains the intellectual product. Codex uses the repository's [`SKILL.md`](SKILL.md) to identify structure and propose page breaks; the renderer then applies one deterministic visual system and exports exact 1080×1440 PNG files.



## What works now

| Capability | Status |
| --- | --- |
| Finished UTF-8 TXT → auditable Markdown | Working |
| Codex-guided headings, emphasis, lists, frameworks, comparisons, and page breaks | Working through `SKILL.md` |
| Human approval of structure and four-part cover headline | Required workflow step |
| Cover plus complete body-card rendering from reviewed Markdown | Working |
| `section_intro`, `prose`, `bullet_list`, `numbered_framework`, `two_column`, `callout`, `cta`, and `references` | Working |
| Exact 1080×1440 output and overflow rejection | Working |
| Source-text reconciliation | Working when `--source-txt` is supplied |
| Manifest, zero-padded cards, and contact sheet | Working |
| Xiaohongshu publishing | Intentionally out of scope |

The intended workflow is:

```text
finished TXT article
        ↓
faithful rendered.md + conversion.json
        ↓
Codex applies semantic Markdown and proposes cover copy
        ↓
human reviews/approves structure and headline
        ↓
one deterministic renderer
        ↓
cover.png + card-NN.png + manifest.json + contact-sheet.png
```

The renderer does not contain a model call. Semantic judgment stays in the Codex skill; rendering stays repeatable and testable.

## Installation

From the repository root:

```sh
cd /Users/lynnwang/Documents/Coding_project/writting_editorial

python3 -m venv .venv
.venv/bin/python -m pip install \
  "Markdown==3.11" \
  "PyYAML==6.0.3" \
  "playwright==1.63.0"
.venv/bin/playwright install chromium
```

Python 3.11 or newer is recommended. Publishing dependencies such as `xhs`, `requests`, and `python-dotenv` are deliberately excluded.

## Use the workflow

### 1. Put the finished article in `inputs/`

Save it as UTF-8 text:

```text
inputs/my-article.txt
```

The article may contain ordinary paragraphs and explicit headings such as `一、为什么会这样`. Do not pre-format it for social media.

### 2. Ask Codex to prepare it

In this project, use a request such as:

> Use the repository's `SKILL.md` to turn `inputs/my-article.txt` into RedNote cards. Preserve every sentence and its order. Prepare the semantic Markdown and proposed cover headline, then stop for my approval before rendering.

Codex will use the skill to:

1. create a versioned run folder;
2. convert the TXT faithfully;
3. read the entire article;
4. add semantic Markdown and page markers;
5. propose the four-part cover headline;
6. show the page plan and uncertain classifications;
7. wait for approval.

The LLM work happens in Codex, not inside a Python CLI.

### 3. Faithful TXT conversion command

Codex normally runs this step, but it can also be run manually:

```sh
.venv/bin/python scripts/txt_to_md.py \
  inputs/my-article.txt \
  --title "文章标题" \
  --series-label "职场观察" \
  --slug my-article \
  --run-id draft-01
```

This creates:

```text
output/my-article/draft-01/
├── rendered.md
└── conversion.json
```

- `rendered.md` initially contains front matter and the unchanged article body.
- `conversion.json` records source/output hashes and mechanical normalization.
- Existing run directories are never overwritten.

Do not use `--infer-structure` in the normal Codex workflow. That older regex heuristic remains for compatibility, but the project skill is the authoritative semantic layer.

### 4. Review `rendered.md`

The reviewed file specifies semantic meaning with ordinary Markdown:

```md
---
title: "你以为这是体面，可能只是在默默把自己的功劳让出去"
series_label: "职场观察"
topic_label: "功劳与可见度"
cover_lead: "你以为这是"
cover_focus: "体面"
cover_bridge: "其实是在"
cover_emphasis: "把功劳让出去"
subtitle: "为什么越懂事，反而越容易被低估？"
source_file: "my-article.txt"
source_format: "txt"
conversion_mode: "semantic"
---

<!-- page: prose -->

# 一、真正危险的不是别人抢你的功劳

## 而是你从来没有把功劳留下来

普通正文保持为普通段落。

**这是一句需要视觉强调的话。**

<!-- page: bullet_list -->

# 系统能够读取的信号

- 谁在汇报；
- 谁的名字在材料里；
- 谁是项目 owner；
```

The Markdown determines meaning:

- `#` — major heading;
- `##` — secondary heading;
- `**text**` — emphasis;
- `- item` — bullet list;
- `1. item` — numbered framework;
- `> text` — quotation or callout;
- `<!-- page: TYPE -->` — page boundary and layout;
- `<!-- column -->` — a column boundary inside a `two_column` page.

The CSS theme—not the Markdown—determines the red rules, typography, spacing, numbering style, and callout colors. The full contract and examples are in [`docs/semantic-markdown.md`](docs/semantic-markdown.md).

### 5. Approve the cover and structure

The cover requires four explicit parts:

| Field | Example | Visual role |
| --- | --- | --- |
| `cover_lead` | `你以为这是` | Black setup |
| `cover_focus` | `体面` | Oversized black focal phrase |
| `cover_bridge` | `其实是在` | Black transition |
| `cover_emphasis` | `把功劳让出去` | Brick-red consequence |

Confirm these together with the proposed page types and headings. The cover may compress the title, but it must not strengthen or change the article's claim.

### 6. Render the approved article

After approval, run:

```sh
.venv/bin/python scripts/render_article.py \
  output/my-article/draft-01/rendered.md \
  --source-txt inputs/my-article.txt
```

By default, the artifacts are written beside `rendered.md`:

```text
output/my-article/draft-01/
├── rendered.md
├── conversion.json
├── cover.png
├── card-01.png
├── card-02.png
├── card-03.png
├── ...
├── manifest.json
└── contact-sheet.png
```

Use `--output-dir PATH` to place the render artifacts in another new run folder.

The renderer:

- uses the approved reference-matched HTML/CSS templates;
- uses only local/system fonts and assets at runtime;
- captures every card at DPR 1;
- validates exact 1080×1440 physical dimensions;
- rejects cover collisions and body/footer overflow;
- refuses to replace existing render artifacts;
- checks the reviewed article against the original TXT;
- writes page types, hashes, dimensions, and structural assignments to `manifest.json`;
- creates a contact sheet for review.

If one page overflows, no partial artifacts are installed. Move the page boundary at a paragraph or sentence boundary, keep semantic units intact, and rerun.

## Supported page types

| Type | Use it for |
| --- | --- |
| `section_intro` | A major section opening with a short setup |
| `prose` | Default analytical prose |
| `bullet_list` | Genuinely parallel items |
| `numbered_framework` | Explicit stages, steps, or numbered reasoning |
| `two_column` | Two directly comparable concepts |
| `callout` | A thesis sentence or important reframing |
| `cta` | Optional, separately approved publication chrome |
| `references` | References supplied by the source |

Readability wins over a fixed page count. Eight to fifteen cards is a rough expectation, not a limit.

## Use an existing Markdown article

TXT conversion is optional if the article already exists as Markdown. Add:

1. the required YAML cover fields;
2. a supported `<!-- page: TYPE -->` marker before every body card;
3. exactly two `<!-- column -->` markers on a `two_column` page.

Then run `scripts/render_article.py`. If there is no original TXT, omit `--source-txt`; the manifest will record that reconciliation was not requested.

## Validation and tests

Run the unit tests:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m unittest \
  tests.test_render_article \
  tests.test_render_cover \
  tests.test_txt_to_md \
  -v
```

Run the end-to-end fixture, which exercises every supported page type:

```sh
.venv/bin/python scripts/render_article.py \
  tests/article-render/sample.md \
  --source-txt tests/article-render/sample.txt \
  --output-dir /tmp/rednote-proof
```

Use a fresh output directory when rerunning because the renderer intentionally refuses to overwrite artifacts.

The unit tests cover semantic parsing, source reconciliation, changed-text rejection, raw-HTML escaping, two-column validation, faithful TXT conversion, overwrite protection, and required cover metadata. The end-to-end fixture additionally exercises Chromium, physical dimensions, overflow checks, manifests, and contact-sheet output.

## Repository layout

```text
.
├── AGENTS.md
├── PROJECT_CONTEXT.md
├── REDNOTE_CODEX_PROJECT_BRIEF.md
├── SKILL.md                         # Codex editorial and approval workflow
├── README.md
├── assets/
│   ├── templates/
│   │   ├── editorial-reference-cover.html
│   │   └── editorial-reference-card.html
│   └── themes/editorial-reference.css
├── docs/
│   ├── semantic-markdown.md         # Reviewed Markdown contract
│   ├── reference-template.md
│   ├── txt-to-md-workflow.md
│   └── upstream-assessment.md
├── inputs/                          # Put finished UTF-8 TXT articles here
├── output/                          # Versioned article runs
├── references/screenshots/          # User-supplied visual references
├── scripts/
│   ├── txt_to_md.py                 # Faithful import and audit
│   ├── render_article.py            # Canonical renderer
│   ├── render_cover.py              # Compatibility wrapper
│   ├── render_reference_proof.py    # Historical design fixture
│   └── render_theme_gallery.py      # Historical upstream comparison
├── tests/
│   ├── article-render/              # End-to-end semantic fixture
│   ├── baseline/                    # Untouched upstream baseline
│   ├── reference-proof/             # Earlier template proof
│   └── theme-gallery/               # Earlier theme comparison
└── vendor/xhs-note-creator/          # Pinned upstream snapshot
```

Only `txt_to_md.py`, `SKILL.md`, the semantic Markdown contract, `render_article.py`, and the active templates are part of the normal user workflow. The theme gallery, proof JSON renderer, old blue theme, and standalone cover CLI are retained only for history or compatibility.

## Design and content rules

The active visual reference is [`references/screenshots/cover-editorial-reference.png`](references/screenshots/cover-editorial-reference.png), supported by the body screenshots in the same folder.

- warm-white paper, near-black text, and brick-red primary accents;
- muted blue only for occasional callouts or approved CTA material;
- large phone-readable Chinese typography and generous whitespace;
- page-number-only body footers;
- two columns only for genuinely paired concepts;
- no cover illustration by default;
- no remote fonts or runtime assets.

The pipeline may add semantic markup and page boundaries. It must not summarize, reorder, invent references, strengthen a qualified claim, drop text, or transform the article into generic influencer copy.

When `--source-txt` is supplied, any changed, missing, duplicated, or reordered text stops rendering before output artifacts are written. The source's first nonblank line may be promoted to the exact matching `title` field.

## Upstream reuse and licensing

The rendering approach is derived from [`cnfjlhj/xhs-note-creator`](https://github.com/cnfjlhj/xhs-note-creator), vendored at commit `ac61b840cbe3b378effd46484c1d92f697372a0d`.

The snapshot remains unchanged under `vendor/xhs-note-creator/`. Project-specific scripts and templates live outside it. Baseline evidence and the reuse assessment are in [`tests/baseline/README.md`](tests/baseline/README.md) and [`docs/upstream-assessment.md`](docs/upstream-assessment.md).

The upstream snapshot does not contain a `LICENSE` file although `package.json` declares `MIT`. Obtain or clarify its license text and copyright notice before redistribution.

## Troubleshooting

### `source reconciliation failed`

The reviewed Markdown changed, omitted, duplicated, or reordered source text. Compare it with the original TXT. Only add Markdown syntax and page/column markers; do not rewrite the underlying words.

### `body content collides with the footer`

The page is too dense. Add a new page marker at the nearest paragraph boundary. If one paragraph alone is too large, split it at a sentence boundary. Do not reduce the global type size or remove content.

### `cover headline collides with the lower rule`

The approved cover copy is too tall for the reference composition. Faithfully redistribute or shorten the four-part cover copy and ask for approval again.

### `refusing to overwrite existing render artifacts`

The run has already been rendered. Preserve it and create a new versioned run, such as `draft-02`.

### `source TXT must be UTF-8 encoded`

Re-save the text file as UTF-8. UTF-8 with a BOM is accepted; GBK and other legacy encodings are not.

### Chromium is missing

```sh
.venv/bin/playwright install chromium
```

### Chromium fails with `EPERM`, `SIGTRAP`, or a launch error

Playwright needs permission to start its local browser process. Approve the scoped browser command in Codex or run the same renderer command in a normal local Terminal.

## Remaining improvements

The core reviewed TXT → cards workflow is implemented. Useful later improvements are:

- targeted regeneration of one approved page;
- richer reconciliation for intentionally relocated references or separately configured CTA text;
- optional supplied cover images;
- font packaging for stronger cross-machine reproducibility;
- more long-article regression fixtures.

These are quality and portability improvements; they are not additional application layers. A GUI, backend, database, embedded model API, publishing integration, analytics, and automated public posting remain out of scope.
