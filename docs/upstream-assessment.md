# Upstream assessment: `cnfjlhj/xhs-note-creator`

> Historical Phase 0 assessment. The approved extension path has since been
> implemented in `scripts/render_article.py`, `SKILL.md`, and
> `docs/semantic-markdown.md`. Keep this document as the baseline decision
> record rather than as current usage documentation.

## Decision

The selected upstream is reusable. Its core choices—Markdown input, HTML/CSS
composition, Playwright measurement, and Chromium screenshots—are sufficient
for this project. A new rendering engine is not justified.

The smallest credible path is to keep the pinned vendor snapshot unchanged and
create a narrow, attributed project-owned derivative of the primary Python
renderer. That derivative should retain the upstream Markdown-to-HTML and
Playwright screenshot pipeline while adding a project theme, explicit page-plan
input, exact-pixel capture, validation, and review artifacts. The semantic
planner remains the repository's Codex skill; it should not be embedded as a
model call inside the renderer.

This document is the Phase 0 review gate. No custom theme, semantic planner, or
publishing functionality has been implemented.

## Material inspected

- Project requirements: `AGENTS.md`, `PROJECT_CONTEXT.md`, and
  `REDNOTE_CODEX_PROJECT_BRIEF.md`
- All available screenshots under `references/screenshots/`, including the new
  typography cover reference
- The representative Chinese article at the repository root
- Upstream `README.md`, `README.en.md`, `SKILL.md`, `STYLES.md`, dependency
  declarations, Python and Node renderers, V2 renderers, HTML templates, base
  CSS, and theme CSS files
- Untouched upstream example render and its contact sheet

The repository currently has no `examples/` directory; the representative
article is `Example-articles-当一个比你有权利的人在占你的便宜，你到底能怎么办.txt`.

## Snapshot and licensing

- Upstream: <https://github.com/cnfjlhj/xhs-note-creator>
- Pinned commit: `ac61b840cbe3b378effd46484c1d92f697372a0d`
- Local path: `vendor/xhs-note-creator/`
- Retrieval: GitHub source archive, because the local Homebrew Git executable
  failed before network access with a libcurl symbol error

The snapshot does not contain a `LICENSE` file, although `package.json` declares
`MIT`. Before distributing a derivative, the upstream license text and copyright
notice must be obtained or clarified. The absence is a provenance risk, not a
reason to replace the renderer silently.

## Baseline result

The documented Python entrypoint rendered the untouched upstream example into
one cover and four cards. The command, environment, hashes, and observations are
recorded in `tests/baseline/README.md`; `tests/baseline/contact-sheet.png` is the
review artifact.

The command succeeds locally, proving the rendering path is viable. Its console
message describes 1080×1440 output, but every raw PNG is 2160×2880. The cause is
the Python renderer's default device scale factor of 2. This is a direct mismatch
with the project's requirement for exact 1080×1440 physical files.

## How the upstream works

The primary Python flow is:

1. Parse a simple YAML front matter block using a regular expression and
   `yaml.safe_load`.
2. Convert Markdown with Python-Markdown extensions `extra`, `codehilite`,
   `tables`, and `nl2br`.
3. Load a named CSS file from `assets/themes/`.
4. Build cover and card HTML inside `scripts/render_xhs.py`.
5. Use Playwright/Chromium to measure content and take screenshots.
6. Split either on explicit separators or, in `auto-split`, on blank-line
   paragraph groups whose measured height exceeds a fixed available-height
   estimate.

The active Python entrypoint does not use `assets/cover.html`, `assets/card.html`,
or `assets/styles.css` as authoritative templates. It assembles its own HTML and
background choices in code. This duplication explains why changing a nominal
template alone would not change the documented render path.

The Node implementation is not behaviorally equivalent: despite advertising
automatic pagination, it splits on separators. Its maximum-height behavior also
differs from Python. V2 introduces heuristic page estimates followed by browser
validation and uses DPR 1, but it is a separate, partially duplicated path and
still lacks the required semantic page model. V1 Python is therefore the best
proven base, with selected V2 measurement ideas adopted deliberately rather than
switching entrypoints wholesale.

## What can remain unchanged

- Python as the canonical local runtime for V1
- Markdown plus YAML front matter as the intermediate authoring format
- Python-Markdown conversion and its existing table/code/list support
- CSS-based visual styling and Chromium's browser layout engine
- Playwright measurement and screenshot capture
- The basic cover-plus-body output concept
- Explicit page separators as an optional escape hatch in an editable
  intermediate file
- The installed rendering dependency set: Markdown, PyYAML, Playwright, and
  Chromium only

Publishing code and dependencies can remain vendored for provenance but must
not be invoked, installed, imported by the project entrypoint, or exposed as a
V1 workflow.

## Requirement comparison

| Requirement | Upstream status | Minimum response |
| --- | --- | --- |
| Reuse an existing renderer | Meets | Preserve pinned snapshot; derive narrowly |
| Local deterministic render | Partial | Remove runtime network assets; pin versions and font stack |
| Exact 1080×1440 PNGs | Fails in documented Python path | Capture at DPR 1 and validate physical dimensions |
| Finished `.md` input | Partial | Retain Markdown input; add project metadata/schema |
| Finished `.txt` input | Missing | Project skill converts faithfully to `rendered.md` |
| Preserve sentences and order | Unverified | Add source/render reconciliation and transformation log |
| Semantic page types | Missing | Add explicit page-plan schema and minimal block markers |
| Semantic pagination | Fails | Plan by blocks; measure; split prose at paragraph then sentence boundaries |
| No orphan headings or split list items | Fails | Treat headings/list items/short arguments as indivisible groups |
| Editable intermediate | Partial | Save `rendered.md` and page plan per run |
| Versioned output folder | Missing | Project-owned orchestration creates immutable run directories |
| Manifest and review artifacts | Missing | Emit `manifest.json` and contact sheet |
| Typography-led editorial theme | Missing | Add one `editorial-blue` theme and cover treatment |
| Cover confirmation workflow | Missing | Implement in the Codex skill, not renderer code |
| Offline after install | Fails | Remove Google Fonts import and all remote runtime assets |
| No publishing | Renderer can be used alone, repo also ships publisher | Exclude publisher from project workflow and dependencies |

## Observed gaps and risks

### Exact output and overflow

The primary renderer's DPR 2 default creates double-resolution physical files.
In separator and automatic modes it also allows the screenshot height to grow
to `max(configured height, measured content height)`. An oversized block can
therefore produce a taller card instead of a valid 3:4 card. The hardcoded
`height - 220` pagination allowance is not derived from the actual selected
theme's header, footer, or padding.

### Hardcoded structure

Cover/card markup, decorative backgrounds, metadata placement, theme names, and
some size policy live in Python rather than in authoritative templates. The
existing HTML files are not a clean extension seam for the primary entrypoint.
The project should make one path authoritative instead of editing several
nominally equivalent implementations.

### Silent content transformation

The cover title and subtitle are sliced to 15 characters. This is silent data
loss and conflicts with the requirement that a proposed two-line headline be
shown for confirmation. The project must fail validation or ask for a revised
cover split rather than truncate.

### Paragraph-only pagination

Automatic splitting groups content around blank lines, measures each group, and
appends it while the estimated page height fits. It does not understand heading
attachment, list item integrity, numbered frameworks, paired comparisons,
callouts, references, or CTAs. It does not split an oversized prose paragraph at
sentence boundaries. The untouched baseline visibly produces an orphan heading
and continuation fragments on later cards.

### Fonts and reproducibility

The active CSS imports Google Fonts. The local run happened to report suitable
Chinese fonts as available, but output can vary by machine or network state.
Offline acceptance requires a local/system font policy with documented fallback
and a render test performed with network access disabled.

### Missing audit and review layer

Upstream emits PNGs only. It does not save a normalized intermediate, page plan,
manifest, transformation record, source-text reconciliation, contact sheet, or
dimension/overflow report. It also uses non-zero-padded card names.

### Multiple drifting renderers

Python, Node, Python V2, and Node V2 are separate implementations with differing
pagination and size behavior. Maintaining parity across all four would add work
without user value. V1 should explicitly support one canonical Python path.

## Minimum modification seams

Keep `vendor/xhs-note-creator/` immutable. In the implementation session:

1. Copy the pinned primary Python renderer to `scripts/render_xhs.py` with an
   attribution header and a concise list of intentional divergences. A local
   derivative is preferable to monkey-patching because the relevant HTML,
   backgrounds, truncation, scale factor, and pagination policy are hardcoded.
2. Make project-owned templates under `assets/` authoritative for the derivative
   renderer. Avoid duplicating the same markup in both templates and Python.
3. Add only `assets/themes/editorial-blue.css` for V1. Do not port or redesign
   the full upstream theme catalog.
4. Accept a validated page plan as renderer input. Keep semantic classification,
   user confirmation, and `.txt` normalization in the project-local `SKILL.md`
   workflow.
5. Add small project-owned validation/contact-sheet helpers. They should inspect
   output, not become another renderer.
6. Keep `vendor/xhs-note-creator/scripts/publish_xhs.py` out of every command,
   dependency list, and acceptance test.

This is an extension-sized fork of one file and its visual assets, not a new
engine or broad upstream refactor.

## Phase 1 checklist: deterministic reference-matched rendering

- [ ] Establish `scripts/render_xhs.py` as the single supported derivative,
      documenting upstream commit and local divergences.
- [ ] Make project cover/card templates authoritative and remove silent
      15-character truncation.
- [ ] Implement the unified warm-white, near-black, brick-red visual system,
      reserving muted blue for occasional callouts.
- [ ] Match the latest supplied typography cover's hierarchy: series label,
      topic label, confirmed black lead/focal/bridge lines, confirmed red
      emphasis line, subtitle block, and restrained rules.
- [ ] Omit issue number and illustration unless explicitly supplied.
- [ ] Give body cards readable minimum type/line-height and page-number-only
      footers.
- [ ] Keep author CTA outside article content and insert it only when configured.
- [ ] Capture at DPR 1 and fail if any PNG is not exactly 1080×1440.
- [ ] Remove Google Fonts and other remote runtime resources; document the local
      Chinese font stack.
- [ ] Fail on overflow/clipping rather than increasing card height.
- [ ] Add zero-padded body-card filenames, contact-sheet generation, and a
      machine-readable validation report.
- [ ] Verify the same intermediate/theme produces identical hashes on repeated
      runs in the supported environment.
- [ ] Run once with network access disabled.
- [ ] Compare the cover against `cover-editorial-reference.png` and bodies
      against `IMG_8834.JPG` through `IMG_8848.JPG`, plus `IMG_8861.JPG`.

## Phase 2 checklist: project-local semantic workflow

- [ ] Add repository-owned `SKILL.md` following the skill-creator conventions,
      with narrow trigger language and progressive disclosure.
- [ ] Accept a finished `.txt` or `.md` article and optional supplied cover asset.
- [ ] Collect missing publication metadata and propose a two-part cover headline
      for user confirmation before rendering.
- [ ] Preserve explicit headings and lists; pause only on genuinely ambiguous
      semantic classifications.
- [ ] Emit editable `rendered.md` plus an explicit page plan containing only:
      `cover`, `section_intro`, `prose`, `bullet_list`, `numbered_framework`,
      `two_column`, `callout`, `cta`, and `references`.
- [ ] Use two columns only for genuinely paired comparisons.
- [ ] Never invent references; relocate an intact supplied bibliography only
      when logged.
- [ ] Keep source sentences and order intact; allow only classification,
      paragraph/sentence pagination, faithful list formatting, and logged
      bibliography relocation.
- [ ] Prevent orphan headings, split bullets, split short numbered arguments,
      clipped text, and undersized type.
- [ ] Split oversized prose first at paragraph boundaries and then at Chinese
      sentence boundaries, without rewriting.
- [ ] Create `output/<article-slug>/<run-id>/` without overwriting earlier runs.
- [ ] Emit `cover.png`, zero-padded body cards, `rendered.md`, page plan,
      `manifest.json`, and `contact-sheet.png`.
- [ ] Log every structural transformation, relocated block, heading split, and
      optional publication-chrome insertion.
- [ ] Reconcile normalized source/rendered text so each source sentence appears
      once and in order, except an explicitly logged bibliography relocation.
- [ ] Exercise long prose, lists, comparisons, numbered frameworks, CTA, and
      supplied references using real Chinese analytical articles.

## Explicit assumptions and requirement mismatches

- `PROJECT_CONTEXT.md` is present, so the earlier execution blocker is resolved.
- The latest `cover-editorial-reference.png` is the primary V1 cover reference.
  Its black/brick-red high-contrast direction supersedes the earlier muted-blue
  cover exploration.
- Readability takes priority over card count; 8–15 cards is an expectation, not
  a cap or target enforced by shrinking type.
- The series and topic labels are configurable metadata; the proof uses
  `职场观察 · 功劳与可见度` to match the latest reference.
- The body footer contains only the page number. Author CTA is optional,
  separately configured publication chrome.
- `IMG_8855.jpg` is not present in the current screenshot directory; the body
  comparison set is `IMG_8834.JPG`–`IMG_8848.JPG` plus `IMG_8861.JPG`.
- First supported runtime is the current local Codex/macOS environment.
  Cross-platform packaging is deferred unless it becomes effectively free.
- License clarification is required before public distribution of the derived
  renderer.

## Review gate

Phase 0 is complete when the baseline artifacts and this assessment are
accepted. Per the requested plan, implementation must stop here before creating
the custom theme, semantic planner, or repository-owned skill.
