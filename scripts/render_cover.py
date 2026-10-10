#!/usr/bin/env python3
"""Compatibility entrypoint for rendering only the project cover.

New article workflows should use render_article.py. This wrapper retains the
earlier cover-only CLI while delegating HTML and screenshot behavior to the
single project renderer.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

import yaml
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

try:
    from scripts.render_article import build_cover_html, screenshot_document
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from render_article import build_cover_html, screenshot_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path, help="Markdown file with YAML front matter")
    parser.add_argument("--lead", help="Black lead line; overrides cover_lead metadata")
    parser.add_argument("--focus", help="Oversized black focal line; overrides cover_focus metadata")
    parser.add_argument("--bridge", help="Black bridge line; overrides cover_bridge metadata")
    parser.add_argument("--emphasis", help="Red emphasis line; overrides cover_emphasis metadata")
    parser.add_argument("--subtitle", help="Optional subtitle; overrides subtitle metadata")
    parser.add_argument("--series-label", help="Overrides series_label metadata")
    parser.add_argument("--topic-label", help="Overrides topic_label metadata")
    parser.add_argument("--output", type=Path, required=True, help="New output PNG path")
    return parser.parse_args()


def read_metadata(markdown: Path) -> dict[str, object]:
    content = markdown.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        raise ValueError("Markdown must begin with YAML front matter")
    parsed = yaml.safe_load(match.group(1)) or {}
    if not isinstance(parsed, dict):
        raise ValueError("YAML front matter must be a mapping")
    return parsed


def build_html(metadata: dict[str, object], args: argparse.Namespace) -> str:
    merged = dict(metadata)
    overrides = {
        "cover_lead": args.lead,
        "cover_focus": args.focus,
        "cover_bridge": args.bridge,
        "cover_emphasis": args.emphasis,
        "subtitle": args.subtitle,
        "series_label": args.series_label,
        "topic_label": args.topic_label,
    }
    for key, override in overrides.items():
        if override is not None:
            merged[key] = override
    return build_cover_html(merged)


async def render(document: str, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        await screenshot_document(browser, document, output, cover=True)
        await browser.close()


def main() -> int:
    args = parse_args()
    try:
        metadata = read_metadata(args.markdown)
        document = build_html(metadata, args)
        asyncio.run(render(document, args.output))
    except (FileExistsError, OSError, PlaywrightError, ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
