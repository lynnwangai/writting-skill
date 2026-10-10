# RedNote Long-Article → Image Cards
## Codex Project Brief

### 1. Background and what we are trying to solve

The current workflow is:

1. Write a long-form Chinese article.
2. Open RedNote/Xiaohongshu's native long-article creation tool.
3. Choose a template.
4. Manually mark which text is:
   - main title,
   - section heading,
   - subsection heading,
   - body text,
   - bullet points,
   - numbered arguments,
   - callouts / key statements,
   - references.
5. Manually adjust spacing and page breaks.
6. Export / publish the resulting image-style article.

The problem is not article writing itself. The expensive part is the repetitive editorial layout work between a finished article and a set of postable 3:4 images.

The desired end state is:

> Give the agent a finished article and optional cover image(s), then have it automatically create a polished set of Xiaohongshu/RedNote image cards in a consistent personal editorial style.

The user should only need to review the generated cards and, for V1, upload them to RedNote manually.

---

## 2. Product goal

Create a local, reusable pipeline:

**finished article**
→ **semantic structure**
→ **RedNote page plan**
→ **rendered 1080×1440 PNG cards**
→ **human review**
→ **manual upload**

The system should automate the layout decisions that are currently manual:
- detecting headings,
- identifying list-like passages,
- deciding where to break pages,
- choosing an appropriate page layout,
- applying typography and spacing consistently,
- formatting references and author CTA,
- exporting all pages with stable filenames.

---

## 3. Important product principles

### Do not reinvent the rendering engine

Start from an existing open-source Xiaohongshu card renderer and modify the minimum necessary.

Preferred base:
- `cnfjlhj/xhs-note-creator`, or equivalently the `xhs-note-creator` component in `tensorslab/xhs-skills`.

Why:
- already designed around Markdown → Xiaohongshu card rendering,
- already has Python and Node renderers,
- uses Playwright,
- supports 1080×1440,
- supports automatic pagination modes,
- separates cover/card templates and themes,
- already uses a Skill-style workflow that can work well with Codex,
- rendering can be used independently of publishing.

Do not build a new canvas/layout engine unless the existing renderer proves unable to support the required layouts.

### Separate editorial reasoning from rendering

The system has two jobs:

**Editorial layer**
- understands the article,
- decides hierarchy and page types,
- decides what goes together,
- chooses where to break pages.

**Rendering layer**
- applies deterministic layout rules,
- controls fonts, margins, colors, spacing,
- outputs PNGs.

The renderer should not have to "understand" the article.

### Preserve the article

Default behavior:
- do not rewrite the intellectual content,
- do not summarize away substantive arguments,
- do not invent material,
- only make layout-level transformations unless the user explicitly asks for editing.

Allowed layout transformations:
- convert parallel sentences into bullets,
- split overly dense paragraphs,
- convert explicit sequences into numbered items,
- shorten a page heading only when necessary and flag the change,
- move citations/references to a dedicated reference page.

---

## 4. Visual style to reproduce

The reference screenshots show a restrained editorial system.

### Base visual language
- 3:4 portrait pages.
- Light warm gray / off-white background.
- Near-black body text.
- Deep dark red as the primary accent.
- Muted blue as the secondary accent for author CTA / references.
- Strong typography hierarchy.
- Generous margins.
- Large phone-readable body type.
- Generous line spacing.
- Minimal decorative elements.
- Subtle divider line near the bottom on standard pages.

### Cover
- Small gray metadata badge near the top:
  - example: word count + estimated reading time.
- Very large bold black title.
- Optional illustration or image occupying the lower portion.
- Lots of negative space.

### Major section heading
- Large bold heading.
- Thick red vertical bar on the left.
- May coexist with a short setup paragraph.

### Subheading
- Dark red.
- Often underlined.
- Stronger than body, smaller than major section heading.

### Body
- Large black Chinese text.
- Comfortable line height.
- Long paragraphs may span multiple cards.

### Bullet block
- Red small vertical marker or red accent.
- Large spacing between bullets.

### Numbered argument block
- Large red `1./`, `2./`, `3./`.
- Supporting black text to the right.
- Thin separators may be used.

### Two-column comparison
Used for:
- "TA has" vs "you have",
- two sides of a framework,
- paired comparison.

Each column can have a short red top rule.

### CTA / author note
- Muted blue highlight.
- Pale blue callout box or blue vertical accent.
- Used sparingly.

### References
- Separate reference page(s).
- Simpler typography.
- Lower density where possible.
- No need to make bibliography pages visually elaborate.

---

## 5. Required page types

V1 should support at least:

1. `cover`
2. `section_intro`
3. `prose`
4. `bullet_list`
5. `numbered_framework`
6. `two_column`
7. `callout`
8. `cta`
9. `references`

Do not create a unique template for every article section. Reuse these primitives.

---

## 6. Proposed semantic markup

Use Markdown as the intermediate representation.

Example:

```md
---
title: 当一个比你有权力的人在占你便宜，你到底能怎么办？
word_count: 5299
reading_minutes: 11
cover_image: assets/cover.png
---

# 二、理论视角：你真正面对的是什么？

想系统地处理这种困境，先要看清三个底层结构。

## 权力与依赖

社会学家 Emerson 提出的……

## 权力来源的类型

French & Raven……

:::twocolumn
### 主任有
- 职位权
- 评价权
- 对上汇报权
- 平台资源

### 她有
- 外部合作资源
- 专业能力
- 部分对外声誉
:::

:::callout
这三点决定了：
- 你为什么不爽
- 对方为什么敢这样做
- 你为什么容易陷入本能反应
:::
```

The exact syntax can be changed after inspecting the existing renderer. Prefer extending its current Markdown parser rather than replacing it.

---

## 7. Semantic mapping rules

Codex should build a reusable mapping rule set.

### Heading inference
- Existing explicit article headings should remain headings.
- Major numbered headings such as `一、`, `二、`, `三、` → `section_intro`.
- Step headings such as `第一步：` → subheading within a framework.
- Do not promote a sentence merely because it sounds dramatic.

### Lists
Convert to a visual list when:
- 3–6 parallel items appear,
- the items share the same grammatical role,
- treating them as separate bullets improves scanning.

Do not convert ordinary prose into bullets purely to make pages look "social-media-like."

### Numbered frameworks
Use numbered cards for:
- explicit 1/2/3 arguments,
- stepwise procedures,
- ranked or sequential reasoning.

### Two-column layouts
Use only when the concepts are genuinely paired:
- person A vs person B,
- current state vs desired state,
- benefit vs cost,
- two dimensions being directly compared.

### Callouts
Use sparingly for:
- a thesis sentence,
- an important reframing,
- a transition sentence that deserves visual emphasis.

### References
If the article contains a reference section, keep it intact and place it at the end.
Do not invent or normalize citations automatically in V1.

---

## 8. Pagination requirements

The current source tools already support auto pagination. Keep that system and improve it only where needed.

Rules:
- Never leave a heading at the bottom of a page without at least some body content below it.
- Avoid splitting a bullet item across pages.
- Avoid splitting a short numbered argument across pages.
- Prefer semantic boundaries over exact character counts.
- Allow a page to be slightly less full rather than visibly cramped.
- Use a target density range rather than trying to fill every pixel.
- For prose, split first at paragraph boundaries.
- If one paragraph is too long for one page, split at sentence boundaries.
- Avoid single orphan lines when possible.

Output dimensions:
- default 1080×1440.
- DPR 2 when supported.

---

## 9. What existing code to reuse

### Primary upstream
`cnfjlhj/xhs-note-creator`

Expected reusable pieces:
- `SKILL.md`
- `scripts/render_xhs.py`
- `scripts/render_xhs.js`
- `assets/cover.html`
- `assets/card.html`
- `assets/styles.css`
- existing themes
- automatic pagination code

### Alternative / broader upstream
`tensorslab/xhs-skills`

Useful if later adding:
- additional image-design skill,
- separate publisher skill,
- more maintained skill organization,
- shared formatting/lint conventions.

### Reference-only tool
`geekfoxcharlie/XHS-TextCard`

Do not make it the first base unless the HTML/Playwright renderer becomes limiting.

Useful ideas to borrow:
- template configuration,
- intelligent pagination UX,
- style controls,
- ZIP export,
- browser preview.

---

## 10. Scope

### V1: build now
- Local rendering only.
- Input: Markdown or plain-text finished article.
- Optional supplied cover image.
- Automatic semantic page planning by Codex.
- One custom visual theme matching reference screenshots.
- Auto pagination.
- 1080×1440 PNG export.
- Stable sequential filenames.
- Contact sheet or preview index for fast review.
- Keep generated intermediate Markdown/page plan for debugging.

### V1 non-goals
- Do not automatically publish publicly to Xiaohongshu.
- Do not reverse-engineer undocumented Xiaohongshu APIs.
- Do not build a cloud service.
- Do not build authentication.
- Do not build a database.
- Do not build a mobile app.
- Do not create an elaborate GUI.
- Do not add follower analytics yet.
- Do not rewrite finished articles by default.

### V2 later
Possible additions after V1 is stable:
- manual browser UI for theme preview,
- one-click ZIP export,
- multiple personal themes,
- optional AI-generated cover illustration,
- article → caption/title suggestion,
- private-draft upload through browser automation,
- analytics feedback loop.

---

## 11. Implementation plan for Codex

### Phase 0 — Inspect upstream and establish baseline

1. Clone the chosen upstream.
2. Read:
   - `README.md`
   - `SKILL.md`
   - `STYLES.md` if present
   - renderer scripts
   - cover/card HTML
   - theme CSS
   - pagination implementation.
3. Install dependencies.
4. Run the existing example.
5. Confirm that the repo can produce a full set of 1080×1440 cards locally.
6. Do not modify code until baseline output is saved.

Deliverable:
- `docs/upstream-assessment.md`
- baseline images in `tests/baseline/`

### Phase 1 — Add personal editorial theme

Add a new theme, e.g.:
- `editorial-red`

Do not modify existing themes unless required.

Implement:
- colors,
- typography,
- margins,
- section heading,
- subheading,
- bullet style,
- numbered style,
- two-column layout,
- CTA style,
- references style,
- bottom divider,
- cover badge.

Deliverable:
- sample article rendered with the new theme.

### Phase 2 — Add semantic-layout conventions

Create:
- `references/editorial-mapping.md`

This file should instruct the agent how to map a finished article into rendering Markdown.

It should define:
- page types,
- heading rules,
- list rules,
- callout rules,
- comparison rules,
- reference rules,
- preservation rules.

Update or add a project `SKILL.md` so Codex can be asked:

> Convert this finished article into RedNote cards using the editorial-red theme. Preserve the article's content; only make layout-level transformations.

### Phase 3 — Improve pagination for long analytical articles

Test on a 4,000–6,000 Chinese-character article.

Fix only observed failures.

High-priority failures:
- orphan heading,
- page overflow,
- page too sparse,
- bullet split,
- bad two-column balance,
- references overflowing,
- unreadably small text.

Do not over-engineer pagination before testing real articles.

### Phase 4 — Add review artifacts

For every render, output:
- `cover.png`
- `card_01.png`, `card_02.png`, ...
- `manifest.json`
- `rendered.md`
- `contact-sheet.png`

`manifest.json` should contain:
- page number,
- page type,
- source section,
- rendered filename,
- any content changes made for layout.

This makes the workflow auditable and easy to revise.

### Phase 5 — Test against the reference style

Create a representative test article containing:
- opening story,
- major headings,
- red subheadings,
- bullets,
- numbered framework,
- two-column comparison,
- CTA,
- references.

Visually compare output against the user's supplied screenshots.

Adjust theme tokens rather than hardcoding one-off fixes.

---

## 12. Suggested project structure

```text
rednote-editorial/
├── AGENTS.md
├── README.md
├── SKILL.md
├── requirements.txt
├── package.json
├── docs/
│   ├── project-brief.md
│   ├── upstream-assessment.md
│   └── visual-spec.md
├── references/
│   └── editorial-mapping.md
├── examples/
│   ├── article.md
│   ├── cover.png
│   └── expected/
├── assets/
│   ├── cover.html
│   ├── card.html
│   └── themes/
│       └── editorial-red.css
├── scripts/
│   ├── render_xhs.py
│   ├── make_contact_sheet.py
│   └── validate_render.py
├── output/
└── tests/
```

If the upstream already has a good structure, preserve it rather than forcing this exact tree.

---

## 13. Acceptance criteria for V1

V1 is successful when all of the following are true:

- One command / one Codex task can turn a finished long article into image cards.
- No manual heading/subheading/bullet marking is required for a normally structured article.
- Output pages are 1080×1440.
- The output visually resembles the reference editorial style.
- Major sections are automatically identified.
- Explicit lists render as lists.
- Numbered frameworks render correctly.
- Paired comparisons can render in two columns.
- References render on dedicated pages.
- No card has clipped text.
- No major heading is orphaned at the bottom.
- Body text remains comfortably readable on a phone.
- All output images can be regenerated deterministically from the saved intermediate Markdown.
- User can revise the generated Markdown and rerun the renderer without touching code.
- Publishing remains manual in V1.

---

## 14. Testing strategy

Create at least five fixture articles:

1. `short-prose.md`
2. `long-analytical.md`
3. `lists-and-steps.md`
4. `comparison-heavy.md`
5. `references-heavy.md`

For each:
- render,
- assert image dimensions,
- assert expected card count range,
- detect overflow if possible,
- save a contact sheet,
- visually inspect.

Do not rely only on unit tests; this is a visual-layout project.

---

## 15. Guardrails

- Do not use undocumented/private Xiaohongshu publishing APIs.
- Do not add automated public posting in V1.
- Do not add hidden browser anti-detection tricks.
- Do not send content to a third-party hosted service unless explicitly approved.
- Keep the renderer local.
- Do not modify the user's article silently.
- Log every content-level transformation in `manifest.json`.
- Prefer simple, maintainable CSS/layout changes over clever rendering logic.

---

## 16. First milestone

The first milestone is intentionally small:

> Render one supplied article into 8–15 polished 1080×1440 cards using the new `editorial-red` theme, with automatic semantic layout and no manual formatting.

Do not attempt publishing, analytics, or multiple themes before this milestone is working.

---

## 17. Definition of "done" for the first Codex session

The first Codex session should end with:

1. upstream repo cloned,
2. dependencies installed,
3. baseline example successfully rendered,
4. repo architecture summarized,
5. exact files to modify identified,
6. implementation plan written,
7. no major refactor yet.

The second session can begin implementation of the custom theme.
