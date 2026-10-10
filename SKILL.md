---
name: rednote-article-cards
description: Convert a finished Chinese TXT or Markdown article into semantically structured Markdown and, when requested, reviewed reference-styled RedNote image cards in this repository. Use for TXT-to-Markdown conversion, article structure, editorial emphasis, cover-copy approval, semantic pagination, rendering, or revising a generated card set; do not use for article rewriting or publishing.
---

# RedNote article cards

Treat the supplied article as substantively approved. Preserve every source sentence and its order. Your work is semantic classification, page planning, cover-copy compression, and deterministic rendering—not rewriting, summarizing, or making the prose more “viral.”

Read `PROJECT_CONTEXT.md`, `REDNOTE_CODEX_PROJECT_BRIEF.md`, and `docs/semantic-markdown.md` before preparing an article. Inspect the active reference screenshots when making visual judgments.

## Workflow

1. Put or locate the finished UTF-8 `.txt` source. For TXT input, run `scripts/txt_to_md.py` without `--infer-structure` to create a versioned, faithful `rendered.md` and `conversion.json`.
2. Read the entire article. Add semantic Markdown without changing its words or order:
   - preserve explicit headings;
   - classify genuine headings, quotations, lists, and numbered frameworks;
   - complete the editorial emphasis pass in `docs/semantic-markdown.md`: wrap exact source wording in `**...**` for the central thesis, key distinctions or reversals, section conclusions, and final synthesis;
   - use `*...*` for a red accent and `***...***` for bold red only when that additional visual priority is intentional;
   - keep emphasis restrained and meaningful; do not bold headings again, supporting examples, setup-only sentences, or text merely to decorate a page;
   - when the source ends with an author self-introduction or sign-off, preserve its exact wording and encode it as `<!-- author-signoff -->` followed by a `>` blockquote immediately before references; treat it as an author signature, not ordinary prose or an invented CTA;
   - keep uncertain passages as prose instead of inventing a stronger structure.
3. Check the semantic draft before presenting it. Reading only its title, headings, and emphasized passages should recover an accurate skeleton of the argument. Every emphasized passage must still be exact source text, and all source sentences must remain once and in order.
4. If the request ends at TXT-to-Markdown conversion, return the versioned `rendered.md` for human review and stop.
5. For a card workflow, prepare a complete review draft before rendering:
   - insert one supported `<!-- page: TYPE -->` marker for every body card;
   - use `<!-- column -->` only for a genuine two-sided comparison;
   - propose the cover's `cover_lead`, `cover_focus`, `cover_bridge`, and `cover_emphasis`, preserving the article's epistemic strength;
   - record the cover fields and the Markdown style legend in front matter so the user can review every planned visual treatment in one file;
   - run `.venv/bin/python scripts/paginate_article.py <semantic.md> <rendered.md> --source-txt <source.txt>` to replace provisional page markers with deterministic browser-measured boundaries;
   - paginate as a continuous reading flow: the paginator adds the next semantic atom while it fits, splits ordinary prose only at sentence boundaries, and keeps headings with their first sentence plus lists, callouts, and numbered arguments intact;
   - run `.venv/bin/python scripts/render_article.py <rendered.md> --source-txt <source.txt> --preflight`; it writes no PNGs and rejects overflow or any non-final body page below 75% fill;
   - if deterministic pagination cannot satisfy the 75% rule, stop and present the named semantic atom that blocked packing; do not manually shuffle boundaries by trial and error, shrink type, or weaken semantic integrity.
6. Present the exact versioned `rendered.md` with a compact review summary: cover copy, style legend, page count, page types/headings, and every uncertain classification. Stop and wait for explicit approval of that exact draft. Approval of an earlier semantic-only draft does not approve newly added cover copy, color, or pagination; any later Markdown change requires another review.
7. When the user edits an approved `rendered.md`, treat that edited file—not the original TXT or an earlier draft—as the canonical editorial input. Create a new versioned run, preserve `source.txt`, rerun deterministic pagination and preflight, and use `--allow-reviewed-edits` only when the user changed source wording. Never regenerate semantic choices from the original source and overwrite the review.
8. Only after approval of the current version, run the single renderer with source reconciliation:

   ```sh
   .venv/bin/python scripts/render_article.py \
     output/<slug>/<run-id>/rendered.md \
     --source-txt inputs/<article>.txt
   ```

9. If the renderer reports overflow or underfill, rerun the paginator from the current reviewed draft. Do not shrink body type below the theme defaults and do not rewrite or drop text to make a page fit. Keep headings with related body, list items intact, and short numbered arguments intact.
10. Visually inspect the contact sheet plus the cover, densest card, final prose card, author sign-off, and references. Confirm exact dimensions, no clipping, continuous non-final fill, and the approved visual roles before presenting the output. Present `contact-sheet.png`, the output directory, and any manifest warnings. Do not publish or automate upload.

## Semantic decisions

- Use `section_intro` for a major section opening with a short setup, not ordinary continuation prose. It is still subject to the 75% non-final-page fill rule.
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
- Final rendering enforces the same 75% non-final-page density rule as preflight and records every page's fill ratio in `manifest.json`.
- Pass `--source-txt` for final renders. A failed reconciliation means the Markdown changed, dropped, duplicated, or reordered source text; resolve the mismatch rather than bypassing validation.
- When the user explicitly edits article wording after review, preserve the original source and pass `--allow-reviewed-edits`; the manifest must report `human_approved_edits` rather than pretending exact reconciliation passed.
- When the review title or cover copy differs from the first line of the immutable source, record that original first line as `source_title`; do not edit `source.txt` merely to make reconciliation pass.
- Do not call the vendored publisher or install publishing dependencies.

