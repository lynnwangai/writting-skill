# Semantic Markdown contract

`rendered.md` is the human-reviewable contract between editorial reasoning and deterministic rendering. Markdown carries meaning; the HTML/CSS theme determines appearance.

## Front matter

Every file starts with YAML front matter:

```yaml
---
title: "完整文章标题"
series_label: "职场观察"
topic_label: "功劳与可见度"
cover_lead: "你以为这是"
cover_focus: "体面"
cover_bridge: "其实是在"
cover_emphasis: "把功劳让出去"
subtitle: "不抢功、不诉苦、不刷存在感，为什么反而更容易被低估？"
source_file: "article.txt"
source_format: "txt"
conversion_mode: "semantic"
---
```

The four `cover_*` fields are required. `title`, labels, and `subtitle` are metadata; the renderer does not silently derive or truncate the approved cover copy.

## Page markers

Every body card starts with a page marker on its own line:

```md
<!-- page: prose -->
```

Supported body types:

- `section_intro`
- `prose`
- `bullet_list`
- `numbered_framework`
- `two_column`
- `callout`
- `cta`
- `references`

The cover comes from front matter and must not have a body page marker.

Page markers determine layout and page breaks. The renderer never chooses a different semantic role. If a card overflows, it fails so the reviewed Markdown can be divided at a meaningful boundary.

## Standard Markdown roles

```md
# Major section heading

## Secondary heading

Ordinary paragraph text.

**Visually important sentence.**

> Quotation or callout text.

- Parallel item one
- Parallel item two

1. **Framework title**
   Framework explanation.
2. **Second framework title**
   Framework explanation.
```

The visual theme—not the Markdown—controls the red rules, font sizes, spacing, numbering treatment, and callout colors.

## Editorial emphasis pass

Bold is part of the semantic conversion, not a cosmetic afterthought. After identifying headings and lists, read the whole article and wrap the smallest intact source sentence or clause that carries one of these roles in `**...**`:

- the article's central thesis;
- a key distinction, reversal, or causal mechanism;
- a section-level conclusion or decision rule;
- the final synthesis.

Use exact source wording. Do not paraphrase, shorten, combine, or strengthen a claim to make it more emphatic. Do not bold a heading again, a supporting example, a citation, a setup-only sentence, or an entire long paragraph when one sentence carries the point. Do not force a quota or add emphasis merely to balance a page.

The result should have a restrained reading rhythm. As a quality check, skim only the title, headings, and bold passages: together they should form an accurate outline of the argument. A major section should normally expose its key claim when one exists; if the source contains no clear claim, leave it unbolded rather than inventing one.

Example:

```md
很多人以为，只要工作做得足够好，价值自然会被看见。

**但组织能够分配的，往往不是全部价值，而是它能够识别的价值。**
```

## Examples by page type

### Section introduction

```md
<!-- page: section_intro -->

# 二、理论视角：你真正面对的是什么？

想系统地处理这种困境，先要看清三个底层结构。
```

### Prose

```md
<!-- page: prose -->

# 一、真正危险的不是别人抢你的功劳

## 而是你从来没有把功劳留下来

第一段原文。

第二段原文，其中有一句**需要视觉强调的话**。
```

### Bullet list

```md
<!-- page: bullet_list -->

# 系统能够读取的信号

- 谁在汇报；
- 谁的名字在材料里；
- 谁是项目 owner；
- 谁被客户反复提到。
```

Only add list punctuation when it is formatting, not replacement prose. Preserve the original words and punctuation whenever possible.

### Numbered framework

```md
<!-- page: numbered_framework -->

# 四、价值在中途“掉了”

1. **能力 → 贡献**
   你会什么，不等于你真正创造了什么。

2. **贡献 → 可见**
   你创造了价值，关键的人知道吗？
```

Use one ordered list. Do not type decorative `1./` text; the theme creates that visual numbering.

### Two-column comparison

```md
<!-- page: two_column -->

# 三、职场真正变掉的是“谁负责看见你”

<!-- column -->

## 学校里

学校很大程度上替你完成了“记录价值”这件事。

<!-- column -->

## 职场里

再也没有人负责完整地观察你。
```

A `two_column` page requires exactly two `<!-- column -->` markers. Text before the first marker is the shared page heading. Do not use columns merely to fill space.

### Callout

```md
<!-- page: callout -->

# 一个重要结论

> 无法被读取的价值，很难参与分配。

Supporting prose may follow when it fits.
```

### CTA

```md
<!-- page: cta -->

# 关于作者

Optional publication text configured separately from the article.
```

Do not insert a CTA unless the user supplies or approves it. CTA text is publication chrome and is excluded from source-text reconciliation only if it is kept outside the source-backed Markdown; V1 therefore recommends omitting it from reconciled article runs.

### References

```md
<!-- page: references -->

# 参考资料

1. An intact reference supplied by the source.
2. Another intact supplied reference.
```

Do not invent or normalize references. V1 preserves their source order rather than relocating them automatically.

## Content reconciliation

For final rendering, pass the original TXT file with `--source-txt`. The renderer removes only semantic Markdown markers and whitespace before comparing source and reviewed text. It also allows the source's first nonblank line to be promoted to the `title` front-matter field when the text matches exactly.

Any other changed, missing, duplicated, or reordered text causes rendering to stop before output artifacts are written.

