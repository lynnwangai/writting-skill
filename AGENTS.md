# AGENTS.md

## Mission

This repository builds a local pipeline that converts a finished long-form Chinese analytical article into polished RedNote/Xiaohongshu 3:4 image cards.

The source article is considered substantively approved. Preserve its intellectual content. The main job is semantic layout, pagination, styling, and deterministic rendering.

## Required context

Before substantial work, read:

- `PROJECT_CONTEXT.md` — product background, motivation, editorial philosophy, and user workflow.
- `REDNOTE_CODEX_PROJECT_BRIEF.md` — scope, architecture, implementation phases, acceptance criteria.
- `SKILL.md` — required workflow when converting or rendering an article.
- reference screenshots under `references/screenshots/` when present.
- representative source articles under `examples/`.

## Engineering principles

- Reuse the selected open-source renderer; do not build a new rendering engine unless a demonstrated blocker requires it.
- Separate semantic/editorial mapping from deterministic rendering.
- Prefer extension to refactoring.
- Preserve upstream behavior until a baseline render has been captured.
- Keep V1 local and simple.
- No undocumented Xiaohongshu APIs.
- No public auto-posting in V1.
- No cloud backend, database, authentication layer, or elaborate GUI in V1.
- Do not silently rewrite or summarize source articles.
- Record content-level layout transformations in the output manifest.
- Test with real long Chinese analytical articles and visually inspect output.

## V1 success criterion

A finished article can be turned into approximately 8–15 readable 1080×1440 cards with semantic page breaks and the target editorial style, without manual classification of headings, bullets, or page breaks.
