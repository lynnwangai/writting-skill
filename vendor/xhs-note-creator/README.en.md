# xhs-note-creator

[中文](README.md) | English

This is a standalone Xiaohongshu note-production toolkit spun out from [`ai-collab-playbook`](https://github.com/cnfjlhj/ai-collab-playbook), focused on one thing:
**turning note copy, card-oriented Markdown, cover generation, content-card rendering, and optional publishing into a reusable workflow.**

If you want something you can fork and customize as a standalone rendering / publishing toolkit, this repo is easier to use than the mother repo.

## Repository Contents

- [`SKILL.md`](SKILL.md): the skill workflow definition
- [`README.reference.md`](README.reference.md): the original detailed reference document, preserved as-is
- [`STYLES.md`](STYLES.md): style and theme notes
- [`assets/`](assets): templates, CSS, example Markdown, and theme files
- [`scripts/`](scripts): Python and Node rendering / publishing scripts
- [`package.json`](package.json) / [`requirements.txt`](requirements.txt): dependency manifests
- [`env.example.txt`](env.example.txt): environment variable example

## When to Use It

- You want a workflow from copywriting to rendered Xiaohongshu cards
- You want theme switching and consistent visual output
- You want a Xiaohongshu card generator that is easy to fork and customize
- You want optional publishing support, but do not want publishing to be the only purpose of the repo

## Quick Start

Python rendering:

```bash
pip install -r requirements.txt
playwright install chromium
python scripts/render_xhs.py assets/example.md -m auto-split
```

Node rendering:

```bash
npm install
npx playwright install chromium
node scripts/render_xhs.js assets/example.md -t default -m separator
```

Before publishing, prepare your own cookie:

```bash
cp env.example.txt .env
```

## Notes

- Real publishing depends on platform cookies, login state, and anti-abuse controls
- Platform or UI changes can break the publishing path
- Rendering and publishing are separate concerns; this repo is still useful as a standalone card-rendering toolkit even if you never automate publishing

## Origin

- Main repo: <https://github.com/cnfjlhj/ai-collab-playbook>
- Long-form companion skill in the mother repo: <https://github.com/cnfjlhj/ai-collab-playbook/tree/main/skills/full/xhs-longform-private-publisher>
