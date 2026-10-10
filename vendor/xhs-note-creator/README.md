# xhs-note-creator

[中文] | [English](README.en.md)

这是一个从 [`ai-collab-playbook`](https://github.com/cnfjlhj/ai-collab-playbook) 里拆出来的独立小红书笔记生产线仓，聚焦一件事：
**把笔记文案、卡片 Markdown、封面和正文图片渲染，以及可选发布流程收进一套可复用工具链。**

如果你想要的是“可以单独 fork 回去改主题、改模板、改脚本”的版本，这个仓比母仓更合适。

## 仓库内容

- [`SKILL.md`](SKILL.md)：skill 工作流说明
- [`README.reference.md`](README.reference.md)：原始详细说明文档（已保留）
- [`STYLES.md`](STYLES.md)：样式与主题说明
- [`assets/`](assets)：模板、样式、示例 Markdown 与主题 CSS
- [`scripts/`](scripts)：Python / Node 渲染与发布脚本
- [`package.json`](package.json) / [`requirements.txt`](requirements.txt)：依赖声明
- [`env.example.txt`](env.example.txt)：环境变量示例

## 适用场景

- 想从内容撰写一路走到卡片渲染
- 想在多个主题之间切换，保持图片风格统一
- 想把“小红书卡片生成”单独做成一个可 fork 的工具仓
- 想保留可选发布步骤，但不把自动发布当成唯一目的

## 快速开始

Python 渲染：

```bash
pip install -r requirements.txt
playwright install chromium
python scripts/render_xhs.py assets/example.md -m auto-split
```

Node 渲染：

```bash
npm install
npx playwright install chromium
node scripts/render_xhs.js assets/example.md -t default -m separator
```

发布前请先准备你自己的 Cookie：

```bash
cp env.example.txt .env
```

## 注意事项

- 真正发布依赖平台 Cookie、登录态和风控状态
- 平台规则或页面变化会直接影响发布链路稳定性
- 渲染与发布是两件事；就算你不用自动发布，这个仓仍然可以单独当卡片渲染工具来用

## 关联主仓

- 主仓首页：<https://github.com/cnfjlhj/ai-collab-playbook>
- 更聚焦长文发布的 companion skill：<https://github.com/cnfjlhj/ai-collab-playbook/tree/main/skills/full/xhs-longform-private-publisher>
