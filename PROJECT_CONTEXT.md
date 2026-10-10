# Project Context: Automated RedNote Long-Article Publishing Pipeline

## 1. Why this project exists

I am building a serious long-form writing practice, primarily in Chinese on RedNote/Xiaohongshu, with the possibility of adapting some of the work later for English-language platforms such as Substack, Medium, Threads, Reddit, or other channels.

My writing is not primarily lifestyle content, product promotion, or short-form entertainment. I tend to write analytical essays about subjects such as:

- power and status,
- workplace and organizational behavior,
- incentives and institutions,
- social psychology,
- culture and media,
- gender and social expectations,
- technology and AI,
- careers and professional strategy,
- other cross-disciplinary social observations.

The writing style is intentionally more intellectually substantive than typical short-form social content. A good article often starts with a recognizable real-life situation, identifies an underlying mechanism, introduces a small number of useful frameworks, analyzes why intuitive responses fail, and then converts the analysis into a practical strategy or higher-level reframing.

I already have a separate writing workflow/skill for developing these essays. This project is NOT intended to replace that writing process.

This project exists because the step *after the article is finished* is unnecessarily manual.

---

## 2. My current workflow and pain point

My current process is roughly:

1. Develop an idea.
2. Research and write a long Chinese article.
3. Finalize the substantive argument.
4. Open Xiaohongshu/RedNote's built-in long-article creation tool.
5. Select one of its templates.
6. Manually tell the editor which pieces are:
   - article title,
   - major section heading,
   - secondary heading,
   - body paragraph,
   - bullet point,
   - numbered argument,
   - important sentence / highlight,
   - comparison block,
   - author CTA,
   - references.
7. Manually adjust:
   - spacing,
   - pagination,
   - line breaks,
   - hierarchy,
   - page density,
   - bullets,
   - visual emphasis.
8. Review the pages.
9. Publish them to RedNote.

The RedNote templates themselves are useful and visually good. The problem is that they still require many repetitive editorial decisions.

Those decisions are predictable enough that an AI agent should be able to make most of them.

The goal is therefore NOT "generate random social-media graphics."

The goal is:

> Take a finished article whose intellectual content is already approved, understand its structure, convert it into a coherent set of editorial page types, and render polished RedNote-ready images with minimal human intervention.

---

## 3. The experience I want

The ideal interaction should eventually be as simple as:

> "Turn this finished article into RedNote cards using my editorial template."

The system should then:

1. Read the full article.
2. Understand its argumentative structure.
3. Detect major and minor headings.
4. Detect explicit or implicit lists.
5. Recognize frameworks, steps, comparisons, callouts, and references.
6. Decide where semantic page breaks should happen.
7. Map the content into a small reusable set of page layouts.
8. Render 3:4 image cards.
9. Export them in sequence.
10. Produce a quick review artifact such as a contact sheet.
11. Preserve the intermediate structured Markdown/page plan so I can revise a specific page without touching code.

I want to review the result, not typeset the article manually.

For V1, I am comfortable uploading the resulting images to RedNote manually.

---

## 4. What this project is NOT

This is not a general "AI social media content generator."

Do NOT turn my essays into generic influencer copy.

Do NOT automatically rewrite them into:
- clickbait listicles,
- motivational slogans,
- shallow "3 truths you need to know" content,
- therapy-style language,
- overly emotional copy,
- generic career advice,
- exaggerated "viral" language.

Do NOT optimize away the intellectual substance in order to make every page punchier.

The rendering system should respect the article.

Its job is primarily:
- interpretation,
- hierarchy,
- formatting,
- pagination,
- visual communication.

It should not silently change the thesis.

---

## 5. Relationship to my writing workflow

My existing writing workflow aims for essays with a structure roughly like:

**recognizable situation**
→ **underlying mechanism**
→ **useful theory/framework**
→ **why intuitive responses fail**
→ **strategic implications**
→ **concrete examples**
→ **higher-level synthesis**

Not every article follows this exact structure, but it is representative.

Typical characteristics:
- 1,500–5,500+ Chinese characters,
- multiple named sections,
- analytical prose,
- occasional academic concepts,
- some concrete examples,
- lists/frameworks where appropriate,
- sometimes a reference section.

The image-card pipeline should be able to handle this kind of material gracefully.

The rendering system must therefore be optimized for **long analytical writing**, not only short social-media captions.

---

## 6. Why semantic layout matters

The hardest part is not drawing text on a canvas.

The hardest part is deciding:

- What deserves to be a major heading?
- What is merely a paragraph?
- Which three statements form a real list?
- Which two blocks are actually comparable?
- Where should a dense paragraph be split?
- Where does a page break preserve the logic?
- Which sentence deserves visual emphasis?
- When is a page too dense?
- When would a two-column layout clarify the argument?
- Should a "first/second/third" section become a numbered visual framework?
- Which material belongs on dedicated reference pages?

These are editorial decisions.

The agent should make those decisions using the article's meaning, not fixed character counts alone.

Rendering should then be deterministic.

This separation is central to the architecture:

### Editorial layer
Understands meaning and produces structured content.

### Rendering layer
Takes structured content and applies visual rules.

---

## 7. Why we are reusing an existing renderer

I do not want to reinvent the wheel.

There are already open-source Xiaohongshu/RedNote card-rendering projects that implement:
- 3:4 image output,
- HTML/CSS or Canvas templates,
- pagination,
- screenshot rendering,
- themes,
- cover cards,
- batch export.

We should reuse those capabilities rather than reimplement them.

The initial preferred upstream is:

`cnfjlhj/xhs-note-creator`

A related broader project worth inspecting is:

`tensorslab/xhs-skills`

`geekfoxcharlie/XHS-TextCard` can also be used as a reference for template/pagination ideas.

The project should begin by proving the upstream works unchanged.

Only then should we customize it.

---

## 8. Visual style I want to preserve

I have reference screenshots from RedNote's native long-article output.

The target is a restrained editorial style, not flashy social graphics.

### Overall
- 3:4 portrait cards.
- Light warm-gray / off-white background.
- Near-black body text.
- Deep dark red as the main accent.
- Muted blue as a secondary accent.
- Large, readable Chinese typography.
- Generous whitespace.
- Strong editorial hierarchy.
- Minimal decoration.

### Cover
- Small gray badge with word count / reading time.
- Very large bold black title.
- Optional illustration occupying the lower part.
- Strong negative space.

### Major section heading
- Large, bold black title.
- Thick red vertical bar at the left.

### Secondary heading
- Dark red.
- Often underlined.
- Clearly distinct from body text.

### Body text
- Large enough to read on a phone.
- Comfortable line height.
- Strong left/right margins.
- No cramped pages.

### Bullets
- Red vertical or linear accent.
- Generous space between items.

### Numbered frameworks
- Large red number such as `1./`.
- Supporting black text aligned beside it.
- Thin divider between items when useful.

### Comparisons
- Optional two-column layout.
- Short red rules at the top of columns.
- Used only for genuinely paired concepts.

### CTA / author box
- Muted blue accent or pale-blue box.
- Used sparingly.

### References
- Dedicated end pages.
- Clean and simple.
- Do not force bibliography into decorative layouts.

The supplied screenshots are the authoritative visual reference.

---

## 9. Content-preservation rule

This is one of the most important requirements.

The source article is assumed to be substantively approved.

By default, the layout pipeline may:
- split a paragraph,
- convert clearly parallel items into bullets,
- place paired concepts side by side,
- move references to a dedicated page,
- extract an existing sentence as a callout,
- shorten a display heading only when necessary.

It may NOT silently:
- rewrite the thesis,
- delete a substantive argument,
- invent an example,
- add a new theory,
- change factual claims,
- remove nuance for engagement,
- add unsupported claims.

Any content-level alteration should be visible in a manifest or diff-like record.

The system should make editorial layout decisions, not become an invisible co-author.

---

## 10. Intended V1

V1 is deliberately narrow.

### Input
- finished Markdown or plain-text Chinese article,
- optional cover image / illustration,
- optional metadata such as title.

### Processing
- semantic analysis,
- page-type selection,
- semantic pagination,
- deterministic rendering.

### Output
- `cover.png`
- `card_01.png`
- `card_02.png`
- ...
- `rendered.md` or equivalent intermediate representation,
- `manifest.json`,
- `contact-sheet.png`

### V1 page primitives
1. cover
2. section intro
3. prose
4. bullet list
5. numbered framework
6. two-column comparison
7. callout
8. author CTA
9. references

These primitives should cover most of the reference design without making the system unnecessarily complex.

---

## 11. What V1 should NOT contain

Do not add these until the core workflow works reliably:

- public auto-posting to Xiaohongshu,
- undocumented/private Xiaohongshu APIs,
- anti-detection browser automation,
- follower analytics,
- content-performance prediction,
- database,
- cloud backend,
- authentication system,
- mobile app,
- elaborate web UI,
- multi-user support,
- ten themes,
- automatic article rewriting.

The first milestone should remain small enough to finish.

---

## 12. First milestone

The first meaningful milestone is:

> Take one representative finished long-form Chinese article and automatically turn it into approximately 8–15 polished 1080×1440 image cards that visually resemble my reference screenshots, without requiring me to manually classify headings, bullets, sections, or page breaks.

The cards must:
- contain no clipped text,
- remain easily readable on a phone,
- preserve the article's argument,
- have coherent semantic page breaks,
- use the right page primitive for the content,
- retain a consistent visual system.

Publishing can remain manual.

---

## 13. Longer-term motivation

The broader goal is to reduce the operational cost of publishing.

I want to spend my time on:
- generating ideas,
- reasoning,
- research,
- writing,
- improving the intellectual quality of the work,
- learning what readers respond to.

I do not want to spend a large fraction of publishing time repeatedly:
- selecting text styles,
- inserting line breaks,
- choosing bullet formatting,
- nudging spacing,
- repairing page breaks.

If this project works, it becomes the bridge between my writing workflow and my RedNote publishing workflow.

Later, the same structured article representation may support:
- RedNote card generation,
- Substack adaptation,
- Threads / X extraction,
- newsletter formatting,
- cross-platform repurposing,
- performance review.

But those are future layers.

The current project should solve **one problem extremely well**:

> Finished analytical article → polished RedNote image set.

---

## 14. Product philosophy

When making implementation decisions, optimize for:

1. **faithfulness to the article**
2. **readability**
3. **semantic coherence**
4. **consistent visual hierarchy**
5. **low manual effort**
6. **maintainability**
7. **reuse of proven open-source components**

Do not optimize for:
- cleverness,
- maximum automation at any cost,
- architectural novelty,
- superficial virality.

The ideal system should feel boring technically and excellent editorially.

---

## 15. How Codex should work on this project

Before major changes:

1. Read this file.
2. Read `REDNOTE_CODEX_PROJECT_BRIEF.md`.
3. Read the repo-root `AGENTS.md`.
4. Inspect the upstream renderer thoroughly.
5. Run the upstream baseline.
6. Preserve a baseline output.
7. Identify the minimum viable modifications.
8. Prefer extension over refactoring.
9. Test against real representative articles.
10. Visually inspect generated cards, not just code/tests.

When uncertain whether to modify article content, preserve the original and ask rather than silently rewriting it.
