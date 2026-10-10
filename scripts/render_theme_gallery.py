#!/usr/bin/env python3
"""Render a cover/body comparison sheet for every vendored upstream theme."""

from __future__ import annotations

import asyncio
import base64
import subprocess
import sys
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "tests" / "theme-gallery" / "sample.md"
RAW = ROOT / "tests" / "theme-gallery" / "raw"
OUTPUT = ROOT / "tests" / "theme-gallery" / "all-upstream-themes.png"
RENDERER = ROOT / "vendor" / "xhs-note-creator" / "scripts" / "render_xhs.py"
THEMES = (
    "default",
    "playful-geometric",
    "neo-brutalism",
    "botanical",
    "professional",
    "retro",
    "terminal",
    "sketch",
)


def render_themes() -> None:
    for theme in THEMES:
        destination = RAW / theme
        destination.mkdir(parents=True, exist_ok=True)
        if (destination / "cover.png").is_file() and (destination / "card_1.png").is_file():
            continue
        for existing in destination.glob("*.png"):
            existing.unlink()
        subprocess.run(
            [
                sys.executable,
                str(RENDERER),
                str(SAMPLE),
                "--theme",
                theme,
                "--mode",
                "separator",
                "--dpr",
                "1",
                "--output-dir",
                str(destination),
            ],
            check=True,
        )


def gallery_html() -> str:
    def embedded_png(path: Path) -> str:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    tiles = []
    for theme in THEMES:
        cover = embedded_png(RAW / theme / "cover.png")
        card = embedded_png(RAW / theme / "card_1.png")
        tiles.append(
            f"""
            <article class="theme">
              <h2>{theme}</h2>
              <div class="pair">
                <figure><img src="{cover}"><figcaption>cover</figcaption></figure>
                <figure><img src="{card}"><figcaption>content</figcaption></figure>
              </div>
            </article>
            """
        )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: 2520px; min-height: 3560px; background: #e9e7e2; }}
body {{ padding: 70px; color: #222; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }}
h1 {{ margin: 0 0 16px; font-size: 54px; }}
.note {{ margin: 0 0 48px; color: #625f59; font-size: 25px; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 42px; }}
.theme {{ padding: 30px; border: 1px solid #d4d0c8; border-radius: 24px; background: #f7f6f3; }}
h2 {{ margin: 0 0 22px; font: 700 30px ui-monospace, SFMono-Regular, Menlo, monospace; }}
.pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
figure {{ margin: 0; }}
img {{ display: block; width: 100%; aspect-ratio: 3 / 4; object-fit: contain; background: white; box-shadow: 0 8px 24px rgba(0,0,0,.12); }}
figcaption {{ padding-top: 11px; color: #77716a; font-size: 20px; text-align: center; }}
</style></head><body>
<h1>Upstream theme comparison</h1>
<p class="note">Same short Chinese sample · cover and first content card · DPR 1</p>
<main class="grid">{''.join(tiles)}</main>
</body></html>"""


async def build_gallery() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 2520, "height": 3560}, device_scale_factor=1)
        await page.set_content(gallery_html(), wait_until="load")
        await page.wait_for_function(
            "Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)",
            timeout=10000,
        )
        height = await page.evaluate("document.documentElement.scrollHeight")
        await page.set_viewport_size({"width": 2520, "height": height})
        await page.screenshot(path=str(OUTPUT), full_page=True)
        await browser.close()


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    render_themes()
    asyncio.run(build_gallery())
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
