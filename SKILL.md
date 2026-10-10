---
name: rednote-article-cards
description: Convert a finished Chinese TXT or Markdown article into reviewed, reference-styled RedNote image cards in this repository. Use for article structure, cover-copy approval, semantic pagination, rendering, or revising a generated card set; do not use for article rewriting or publishing.
---

# RedNote article cards

Treat the supplied article as substantively approved. Preserve every source sentence and its order. Your work is semantic classification, page planning, cover-copy compression, and deterministic rendering—not rewriting, summarizing, or making the prose more “viral.”

Read `PROJECT_CONTEXT.md`, `REDNOTE_CODEX_PROJECT_BRIEF.md`, and `docs/semantic-markdown.md` before preparing an article. Inspect the active reference screenshots when making visual judgments.

## Workflow

1. Put or locate the finished UTF-8 `.txt` source. For TXT input, run `scripts/txt_to_md.py` without `--infer-structure` to create a versioned, faithful `rendered.md` and `conversion.json`.
2. Read the entire article. Add semantic Markdown without changing its words or order:
   - preserve explicit headings;
   - use ordinary Markdown for headings, bold emphasis, quotations, and lists;
   - insert one supported `<!-- page: TYPE -->` marker for every body card;
   - use `<!-- column -->` only for a genuine two-sided comparison;
   - keep uncertain passages as prose instead of inventing a stronger structure.
3. Propose the cover's `cover_lead`, `cover_focus`, `cover_bridge`, and `cover_emphasis`. Keep the article's epistemic strength. Add the proposed values to front matter only after showing them to the user.
4. Before rendering, show the user a compact review summary: cover copy, page count, page types/headings, and every uncertain classification. Pause for approval when the cover or structure has not already been approved.
5. After approval, run the single renderer with source reconciliation:

   ```sh
   .venv/bin/python scripts/render_article.py \
     output/<slug>/<run-id>/rendered.md \
     --source-txt inputs/<article>.txt
   ```

6. If the renderer reports overflow, adjust page markers at paragraph or sentence boundaries. Do not shrink body type below the theme defaults and do not rewrite or drop text to make a page fit. Keep headings with related body, list items intact, and short numbered arguments intact.
7. Present `contact-sheet.png`, the output directory, and any manifest warnings. Do not publish or automate upload.

## Semantic decisions

- Use `section_intro` for a major section opening with a short setup, not ordinary continuation prose.
- Use `prose` by default.
- Use `bullet_list` only for genuinely parallel items.
- Use `numbered_framework` for explicit sequential or numbered reasoning.
- Use `two_column` only when the two sides are directly comparable.
- Use `callout` sparingly for a thesis or important reframing.
- Treat `cta` as optional publication chrome, separate from article content.
- Use `references` only for references supplied by the source; never invent citations.

Aim for readable cards rather than a fixed count. Eight to fifteen cards is an expectation for typical long articles, not a constraint.

## Output and revision rules

- Use `output/<article-slug>/<run-id>/` and never overwrite a prior reviewed run.
- Keep `rendered.md` editable and make page-boundary corrections there.
- The renderer must produce `cover.png`, zero-padded `card-NN.png` files, `manifest.json`, and `contact-sheet.png`.
- Pass `--source-txt` for final renders. A failed reconciliation means the Markdown changed, dropped, duplicated, or reordered source text; resolve the mismatch rather than bypassing validation.
- Do not call the vendored publisher or install publishing dependencies.

