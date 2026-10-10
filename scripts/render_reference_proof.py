#!/usr/bin/env python3
"""Render the reference-matched cover and representative body-card proof set."""

from __future__ import annotations

import asyncio
import base64
import html
import json
import struct
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "tests" / "reference-proof" / "sample-pages.json"
OUT = ROOT / "tests" / "reference-proof" / "rendered"
CONTACT = ROOT / "tests" / "reference-proof" / "contact-sheet.png"
CSS = (ROOT / "assets" / "themes" / "editorial-reference.css").read_text(encoding="utf-8")
COVER_TEMPLATE = (ROOT / "assets" / "templates" / "editorial-reference-cover.html").read_text(encoding="utf-8")
CARD_TEMPLATE = (ROOT / "assets" / "templates" / "editorial-reference-card.html").read_text(encoding="utf-8")
WIDTH, HEIGHT = 1080, 1440


def escaped(value: object, allow_breaks: bool = False) -> str:
    safe = html.escape(str(value))
    return safe.replace("&lt;br&gt;", "<br>") if allow_breaks else safe


def cover_html(data: dict[str, object]) -> str:
    replacements = {
        "/*__CSS__*/": CSS,
        "__SERIES__": escaped(data["series"]),
        "__TOPIC__": escaped(data["topic"]),
        "__LEAD__": escaped(data["lead"], allow_breaks=True),
        "__FOCUS__": escaped(data["focus"], allow_breaks=True),
        "__BRIDGE__": escaped(data["bridge"], allow_breaks=True),
        "__EMPHASIS__": escaped(data["emphasis"], allow_breaks=True),
        "__SUBTITLE__": escaped(data["subtitle"], allow_breaks=True),
    }
    document = COVER_TEMPLATE
    for token, value in replacements.items():
        document = document.replace(token, value)
    return document


def body_html(page: dict[str, object], number: int) -> str:
    content = [f'<h1 class="major-heading">{escaped(page["heading"])}</h1>']
    kind = page["type"]
    if kind == "prose":
        content.append(f'<div class="subheading">{escaped(page["subheading"])}</div>')
        content.append('<div class="quote-stack">')
        content.extend(f"<p>{escaped(quote)}</p>" for quote in page["quotes"])
        content.append("</div><div class=\"body-copy\">")
        content.extend(f"<p>{escaped(paragraph)}</p>" for paragraph in page["paragraphs"])
        content.append("</div>")
    elif kind == "numbered_framework":
        content.append(f'<div class="chain">{escaped(page["chain"])}</div><div class="framework">')
        for numeral, title, text in page["items"]:
            content.append(
                '<section class="framework-item">'
                f'<div class="framework-number">{escaped(numeral)}</div>'
                f'<div><h2 class="framework-title">{escaped(title)}</h2>'
                f'<p class="framework-text">{escaped(text)}</p></div></section>'
            )
        content.append("</div>")
    elif kind == "comparison":
        content.append('<div class="comparison">')
        for title, text in page["columns"]:
            content.append(
                f'<section class="comparison-column"><h2>{escaped(title)}</h2>'
                f'<p>{escaped(text)}</p></section>'
            )
        content.append("</div>")
        content.append(f'<aside class="callout"><p>{escaped(page["callout"])}</p></aside>')
        content.append('<div class="body-copy">')
        content.extend(f"<p>{escaped(paragraph)}</p>" for paragraph in page["paragraphs"])
        content.append("</div>")
    else:
        raise ValueError(f"unsupported proof page type: {kind}")

    return CARD_TEMPLATE.replace("/*__CSS__*/", CSS).replace("__CONTENT__", "".join(content)).replace("__PAGE_NUMBER__", f"{number:02d}")


def dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    return struct.unpack(">II", data[16:24])


async def screenshot(browser, document: str, path: Path) -> None:
    page = await browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
    await page.set_content(document, wait_until="load")
    await page.evaluate("document.fonts.ready")
    overflow = await page.evaluate("document.documentElement.scrollHeight > 1440 || document.documentElement.scrollWidth > 1080")
    if overflow:
        raise ValueError(f"layout overflow: {path.name}")
    await page.screenshot(path=str(path), full_page=False)
    await page.close()
    if dimensions(path) != (WIDTH, HEIGHT):
        raise ValueError(f"invalid dimensions for {path.name}: {dimensions(path)}")


def contact_html(paths: list[Path]) -> str:
    figures = []
    labels = ("cover", "prose", "numbered framework", "comparison")
    for path, label in zip(paths, labels):
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        figures.append(f'<figure><img src="data:image/png;base64,{encoded}"><figcaption>{label}</figcaption></figure>')
    return f"""<!doctype html><html><head><style>
    *{{box-sizing:border-box}}html,body{{margin:0;width:2200px;height:1600px;background:#e9e5df}}
    body{{padding:50px;font-family:-apple-system,BlinkMacSystemFont,sans-serif}}
    h1{{margin:0 0 30px;font-size:40px}}main{{display:grid;grid-template-columns:repeat(4,1fr);gap:28px}}
    figure{{margin:0;padding:14px;background:white;border-radius:12px}}img{{display:block;width:100%;aspect-ratio:3/4;object-fit:contain}}
    figcaption{{padding:12px 0 2px;text-align:center;font-size:22px;color:#625d57}}
    </style></head><body><h1>Editorial reference proof</h1><main>{''.join(figures)}</main></body></html>"""


async def main() -> None:
    data = json.loads(SPEC.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [OUT / "cover.png"] + [OUT / f"card-{index:02d}.png" for index in range(1, 4)]
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        await screenshot(browser, cover_html(data["cover"]), paths[0])
        for index, page_data in enumerate(data["pages"], start=1):
            await screenshot(browser, body_html(page_data, index), paths[index])
        contact = await browser.new_page(viewport={"width": 2200, "height": 1600}, device_scale_factor=1)
        await contact.set_content(contact_html(paths), wait_until="load")
        await contact.wait_for_function("Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)")
        await contact.screenshot(path=str(CONTACT), full_page=False)
        await browser.close()
    print(CONTACT)


if __name__ == "__main__":
    asyncio.run(main())
