---
name: rednote-editorial-cover
description: Create feed-optimized covers for long-form RedNote/Xiaohongshu analytical articles using a consistent restrained editorial system: warm off-white background, near-black typography, deep brick-red consequence/accent text, strong asymmetrical hierarchy, generous whitespace, and a compact secondary diagnostic line. Use when the user provides an article, draft, thesis, or post title and wants a RedNote cover consistent with serious analytical content rather than generic influencer graphics.
---

# RedNote Editorial Cover

## Purpose

Turn a finished long-form article into a RedNote/Xiaohongshu cover that:

1. can be understood at small two-column-feed thumbnail size;
2. creates enough cognitive tension to stop scrolling;
3. accurately represents the article rather than overselling it;
4. looks like the front cover of the same editorial system as the article's inner pages;
5. remains visually consistent across different topics so the account develops recognizable branding.

This skill is designed primarily for analytical long-form writing: workplace, power, psychology, institutions, culture, gender, careers, technology, and other idea-driven essays.

It is NOT intended for product advertisements, lifestyle collages, celebrity-style covers, or generic "viral template" graphics.

---

# Core design principle

The cover is not a summary of the article.

Its job is to make one tension immediately legible in the feed.

A strong cover should normally communicate:

**familiar belief / respectable behavior**
→ **unexpected consequence**

Examples of the pattern:

- 体面 → 功劳被让出去
- 谦虚 → 贡献从系统里消失
- 懂事 → 隐形成本
- 努力 → 不一定等于被看见
- 公平 → 不一定自动产生正确归因

Do not force every article into this exact rhetorical form. Find the article's real tension first.

---

# Step 1 — Read the article before writing the cover

When a full article is available, do not generate the cover from the title alone.

Extract:

- the central thesis;
- the reader-recognizable situation;
- the strongest paradox, reversal, or hidden cost;
- the concrete consequence that matters to the reader;
- the article's actual degree of certainty;
- 2–4 phrases already present in the article that could serve as cover language.

Prefer language that is already conceptually faithful to the article.

Do not invent a more sensational thesis merely because it would create a stronger hook.

---

# Step 2 — Separate post title from cover copy

The RedNote post title and the text printed on the cover do NOT need to be identical.

The post title can be nuanced and sentence-like.

The cover should be compressed for thumbnail recognition.

For example:

Post title:
`你以为这是体面，可能只是在默默把自己的功劳让出去`

Cover:
`你以为这是`
`体面`
`可能是在`
`把功劳让出去`

A small diagnostic line may be added:
`不抢功、不诉苦、不刷存在感，为什么反而更容易被低估？`

Do not mechanically shorten by deleting random words. Preserve the causal or rhetorical relationship.

---

# Step 3 — Preserve epistemic strength

Do not silently turn a qualified claim into a categorical claim.

Examples:

- Source says `可能` → default cover should keep `可能`, `也许`, or another equally qualified construction.
- Source strongly establishes a claim and the user wants a more assertive marketing variant → a stronger bridge such as `其实` may be offered as an optional A/B variant.
- Never strengthen a claim solely for CTR.

The cover should attract attention without misrepresenting the article.

---

# Step 4 — Cover-copy hierarchy

Default to FOUR functional layers, but only TWO should dominate visually.

## Layer A — optional eyebrow

Tiny, nonessential series/context label.

Examples:
- `职场观察 · 功劳与可见度`
- `权力与组织 / 02`
- `社会心理 · 职场`
- `AI × 组织权力`

Rules:
- 4–12 Chinese characters plus optional separator;
- deep brick red;
- small enough that the cover still works if it is unreadable at thumbnail size;
- never compete with the hook.

If the cover already feels busy, omit this layer.

## Layer B — premise / familiar belief

Short setup in near-black.

Examples:
- `你以为这是`
- `我们总以为`
- `看起来很公平`
- `你以为自己在谦虚`

Usually 4–10 Chinese characters.

This line provides the setup but is NOT the main focal point.

## Layer C — primary anchor word or phrase

The first major visual anchor.

Examples:
- `体面`
- `谦虚`
- `努力`
- `懂事`
- `公平`

Usually 2–6 Chinese characters.

Use near-black unless the article's meaning strongly benefits from another treatment.

Make this very large.

## Layer D — hidden consequence / reversal

The second major visual anchor and default red element.

Examples:
- `把功劳让出去`
- `让贡献从系统里消失`
- `正在变成隐形成本`
- `却没人记得是谁做的`

Use deep brick red.

The consequence should usually be more concrete than the premise.

---

# Optional secondary diagnostic line

Add ONE smaller diagnostic line only when it materially improves comprehension.

Example:
`不抢功、不诉苦、不刷存在感，为什么反而更容易被低估？`

Good diagnostic lines:
- specify the actual situation;
- contain recognizable behavior;
- tell the reader what question the article answers.

Bad diagnostic lines:
- repeat the headline;
- contain generic promises such as `三步破局`;
- add another abstract concept;
- become a mini-paragraph.

Target: about 15–30 Chinese characters, maximum two visual lines.

If the main hook is already self-explanatory, omit the diagnostic line.

---

# Feed-mode text budget

Design for the Xiaohongshu two-column feed, not full-screen viewing.

At thumbnail size, a user should perceive the semantic skeleton in roughly one glance.

Default constraints:

- 1 dominant premise/anchor cluster;
- 1 dominant consequence cluster;
- maximum 4 large headline lines;
- optional 1–2 small subtitle lines;
- no body paragraph;
- no first article section heading;
- no reading-time badge by default;
- no list of benefits;
- no multiple callouts.

The cover should not attempt to explain the article.

---

# Visual system

The supplied reference cover and content page are the visual anchors. Follow them more closely than generic design conventions.

## Canvas

- Exact final export: `1080 × 1440 px`.
- Aspect ratio: `3:4`.
- Portrait orientation.
- Final delivery PNG must be exactly 1080×1440.
- Internal DPR 2 rendering is acceptable if final output is deterministically downsampled to 1080×1440.

## Palette

Use a restrained three-color system.

Recommended tokens:

```css
--bg: #FCFBF9;
--ink: #141210;
--accent: #A01412;
--divider: #E7DDD9;
```

When matching an existing article template, prefer sampling/reusing that template's exact background and red token rather than introducing a new shade.

Do not introduce bright blue, yellow, gradients, or unrelated accent colors by default.

Blue may appear inside article pages for an established secondary semantic role, but the default cover remains off-white + near-black + brick red.

## Background

- warm off-white;
- visually quiet;
- no texture unless nearly imperceptible;
- no photographic background by default.

## Typography

Use a heavy, clean Chinese sans-serif / grotesk style for primary headline text.

Requirements:
- bold/black weight for dominant lines;
- high legibility;
- compact enough to feel editorial rather than playful;
- avoid decorative, handwritten, rounded-cute, or calligraphic display fonts.

Body/subtitle should use the same family or a visually compatible clean sans-serif at normal/medium weight.

Do not package or share font files with the skill.

## Alignment

Default: left-aligned.

The design should feel editorial and asymmetrical rather than centered like a presentation slide.

## Whitespace

Whitespace is part of the brand.

Do not fill the full canvas merely because space is available.

The headline cluster should feel large and confident, but avoid pushing text so close to edges that the cover becomes aggressive or cramped.

Recommended safe horizontal margin:
- approximately 8–10% of canvas width.

Recommended top breathing space:
- approximately 6–9% of canvas height before the primary headline system begins.

---

# Color semantics

Use color to carry meaning rather than decoration.

Default semantic rule:

- near-black = the familiar belief / respectable self-image;
- brick red = the hidden cost, reversal, or consequential phrase.

Example:

BLACK:
`你以为这是`
`体面`

RED:
`把功劳让出去`

This visually enacts the article's argument.

Do not alternate red and black arbitrarily.

Avoid coloring more than roughly one-third to two-fifths of the main headline area red.

---

# Editorial devices

Allowed:
- one thin brick-red horizontal rule;
- one short red line after the eyebrow;
- one small red vertical rule beside the diagnostic line;
- a subtle divider near the bottom;
- occasional quotation marks when semantically meaningful.

Avoid:
- icons;
- stickers;
- emojis;
- multiple boxes;
- gradients;
- shadows;
- neon colors;
- decorative shapes;
- fake paper textures;
- large translucent numbers;
- unnecessary illustrations.

The default style wins attention through typography and contrast, not decoration.

---

# Recommended default composition

A strong baseline composition is:

```text
[small red eyebrow] ─────

[black setup]
[VERY LARGE BLACK ANCHOR]

[black bridge]
[VERY LARGE RED CONSEQUENCE]

────────────────────────

▌ [small black diagnostic line]
  [second line if needed]
```

Example:

```text
职场观察 · 功劳与可见度  ─────

你以为这是
体面

可能是在
把功劳让出去

────────────────────────

▌ 不抢功、不诉苦、不刷存在感，
  为什么反而更容易被低估？
```

Do not treat this as a rigid template. Preserve the hierarchy while adapting line breaks to the actual language.

---

# Line-breaking rules

Line breaks are a design decision.

Prefer semantic chunks.

Good:
`把自己的`
`功劳让出去`

or:
`把功劳`
`让出去`

depending on visual balance.

Bad:
breaking a fixed phrase in a way that changes reading rhythm or makes a grammatical particle visually dominant.

For each headline:
1. identify semantic chunks;
2. test 2–3 line-break options;
3. prefer the version whose key words remain visually intact;
4. ensure the cover still reads correctly when visually reduced.

Never stretch character spacing just to fill a line.

---

# Headline sizing

Relative rather than absolute sizing is the governing rule.

Suggested hierarchy for 1080×1440:

- eyebrow: ~24–36 px equivalent;
- setup/bridge: ~64–100 px equivalent;
- main black anchor: ~150–230 px equivalent;
- red consequence: ~115–180 px equivalent depending on length;
- diagnostic line: ~36–54 px equivalent.

Adjust based on Chinese character count.

The largest word should not be so oversized that it loses the sophisticated visual character of the inner pages.

If a phrase is long, reduce size rather than squeezing tracking.

---

# Article-to-cover reasoning workflow

Given an article:

1. State the article's thesis in one sentence.
2. Identify the moral/social assumption or familiar behavior.
3. Identify the hidden cost/consequence.
4. Check which of these is concrete enough to stop a scroll.
5. Draft 3 possible cover compressions.
6. Reject any that:
   - exaggerate the article;
   - become generic career advice;
   - rely on clickbait vocabulary;
   - require more than one glance to decode.
7. Choose the strongest cover.
8. Create a small diagnostic line only if needed.
9. Map premise → black and consequence → red.
10. Choose semantic line breaks.
11. Render using the fixed visual system.
12. Inspect at simulated feed-thumbnail size before finalizing.

---

# Thumbnail QA

Before finalizing, mentally or literally reduce the cover to roughly 25–35% of full width.

Ask:

1. Can I immediately read the two or three semantic anchors?
2. Do I understand the conflict without reading the small subtitle?
3. Is there exactly one obvious focal path?
4. Does the red phrase communicate the consequence?
5. Is anything present that only works at full-screen size?
6. Does the design still look like serious editorial content rather than a generic marketing card?
7. Does it look consistent with the supplied inner-page reference?

If the answer to 1–4 is no, simplify.

---

# Brand consistency rules

Across articles, keep consistent:

- canvas ratio;
- off-white background;
- near-black main type;
- brick-red consequence/accent;
- left alignment;
- spacing logic;
- thin-rule vocabulary;
- headline weight;
- overall restraint.

Vary:

- headline wording;
- line breaks;
- which concept is largest;
- whether an eyebrow is used;
- whether a diagnostic line is needed.

The account should have a recognizable visual grammar without making every cover look mechanically identical.

---

# Anti-patterns

Do NOT default to:

- `3步破局`
- `职场人必看`
- `建议收藏`
- `看完你就懂了`
- `99%的人不知道`
- multiple exclamation marks
- emojis
- exaggerated pain points
- motivational-copy tone
- five different font sizes competing for attention
- bright blue bars inconsistent with the article palette
- a paragraph of body text on the cover
- first article section appearing below the cover title
- reading time as a major visual element

These may be used only if the user specifically requests a different, more conventional RedNote marketing style.

---

# Rendering modes

## If an image-generation tool is available

Generate the cover directly, using the reference images as style anchors when possible.

Prioritize:
1. exact Chinese text;
2. typography hierarchy;
3. palette consistency;
4. whitespace;
5. layout.

Do not add objects, people, illustrations, or decorative graphics unless requested.

After generation, visually verify that all Chinese characters are correct. If text is malformed, regenerate or use deterministic rendering.

## If HTML/CSS, Canvas, SVG, or another deterministic renderer is available

Prefer deterministic rendering for production covers because it preserves exact Chinese text and allows reliable reuse.

Use the palette and hierarchy in this skill.

Final output must be exactly 1080×1440 PNG.

## If no renderer is available

Return a structured cover specification containing:

```yaml
eyebrow:
setup:
anchor:
bridge:
consequence:
diagnostic:
palette:
line_breaks:
layout_notes:
```

Do not claim to have rendered an image.

---

# Output behavior

When the user asks to "make/generate the cover":

1. Read the article/title.
2. Choose or propose the cover copy.
3. If the user already approved the wording, do not re-litigate it.
4. Render the cover if a suitable image/rendering tool is available.
5. Return the visual, not a long explanation.

When the user asks to "design/evaluate the cover":

Return:
- proposed cover copy;
- why it works in feed mode;
- hierarchy/layout;
- any important tradeoff.

Keep the explanation concise unless the user asks for detail.

---

# Reference example

Input article theme:
People avoid correcting credit attribution or making their work visible because self-promotion can feel socially improper, but organizations cannot reconstruct invisible contributions automatically.

Post title:
`你以为这是体面，可能只是在默默把自己的功劳让出去`

Strong cover mapping:

```yaml
eyebrow: "职场观察 · 功劳与可见度"
setup: "你以为这是"
anchor: "体面"
bridge: "可能是在"
consequence: "把功劳让出去"
diagnostic: "不抢功、不诉苦、不刷存在感，为什么反而更容易被低估？"
```

Visual mapping:
- setup: black
- anchor: very large black
- bridge: black
- consequence: very large brick red
- eyebrow: small brick red
- diagnostic: smaller near-black with small red vertical rule
- background: warm off-white

The supplied `references/reference-cover.png` is the primary visual target.
The supplied `references/reference-content-page.jpg` shows the inner-page color/hierarchy system the cover should belong to.

---

# Final standard

A successful cover should feel like:

**a serious magazine/editorial cover adapted for the Xiaohongshu feed**

not:

**a generic Xiaohongshu marketing poster.**

The user should be able to scroll past many covers and recognize this visual family before reading the account name.
