#!/usr/bin/env python3
"""Render reviewed semantic Markdown into RedNote cover, cards, and review artifacts.

The HTML/CSS/Playwright approach is derived from cnfjlhj/xhs-note-creator at
commit ac61b840cbe3b378effd46484c1d92f697372a0d. This project entrypoint uses
explicit semantic page markers, local assets, exact DPR-1 capture, overflow
validation, an output manifest, and a contact sheet.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
import re
import shutil
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import markdown
import yaml
from playwright.async_api import Browser, Error as PlaywrightError
from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parent.parent
CSS_PATH = ROOT / "assets" / "themes" / "editorial-reference.css"
COVER_TEMPLATE_PATH = ROOT / "assets" / "templates" / "editorial-reference-cover.html"
CARD_TEMPLATE_PATH = ROOT / "assets" / "templates" / "editorial-reference-card.html"
WIDTH = 1080
HEIGHT = 1440
MIN_CONTINUOUS_FILL_RATIO = 0.75
FOOTER_CLEARANCE = 20
UPSTREAM_COMMIT = "ac61b840cbe3b378effd46484c1d92f697372a0d"
PAGE_TYPES = {
    "section_intro",
    "prose",
    "bullet_list",
    "numbered_framework",
    "two_column",
    "callout",
    "cta",
    "references",
}
PAGE_MARKER = re.compile(
    r"^<!--\s*page:\s*([a-z_]+)\s*-->\s*$", re.MULTILINE
)
COLUMN_MARKER = re.compile(r"^<!--\s*column\s*-->\s*$", re.MULTILINE)
FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
AUTHOR_SIGNOFF_MARKER = "<!-- author-signoff -->"


@dataclass(frozen=True)
class SemanticPage:
    kind: str
    markdown: str


@dataclass(frozen=True)
class Article:
    metadata: dict[str, object]
    pages: tuple[SemanticPage, ...]
    body: str


def density_is_required(page_number: int, page_count: int) -> bool:
    """Every body page except the final page must meet the fill threshold."""
    return page_number < page_count


def body_fill_ratio(metrics: dict[str, float]) -> float:
    """Return the fraction of usable body height occupied by rendered content."""
    usable_bottom = metrics["ruleTop"] - FOOTER_CLEARANCE
    usable_height = usable_bottom - metrics["contentTop"]
    used_height = metrics["contentBottom"] - metrics["contentTop"]
    return used_height / usable_height if usable_height else 0


def require_page_density(
    metrics: dict[str, float],
    page_number: int,
    page_count: int,
    page_type: str,
) -> float:
    """Validate the continuous-flow density invariant and return its ratio."""
    fill_ratio = body_fill_ratio(metrics)
    if density_is_required(page_number, page_count) and fill_ratio < MIN_CONTINUOUS_FILL_RATIO:
        raise ValueError(
            f"page {page_number} ({page_type}) is underfilled: "
            f"fill ratio {fill_ratio:.3f} is below {MIN_CONTINUOUS_FILL_RATIO:.2f}"
        )
    return fill_ratio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path, help="Reviewed semantic Markdown file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output run directory; defaults to the Markdown file's directory",
    )
    parser.add_argument(
        "--source-txt",
        type=Path,
        help="Original UTF-8 TXT file for exact content reconciliation",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Measure cover fit, overflow, and page density without writing PNGs",
    )
    parser.add_argument(
        "--allow-reviewed-edits",
        action="store_true",
        help="Record explicit human-approved text edits instead of requiring exact source equality",
    )
    return parser.parse_args()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_article(path: Path) -> Article:
    content = path.read_text(encoding="utf-8")
    front = FRONT_MATTER.match(content)
    if not front:
        raise ValueError("Markdown must begin with YAML front matter")
    metadata = yaml.safe_load(front.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError("YAML front matter must be a mapping")

    body = content[front.end() :]
    matches = list(PAGE_MARKER.finditer(body))
    if not matches:
        raise ValueError("article has no semantic page markers such as <!-- page: prose -->")
    if body[: matches[0].start()].strip():
        raise ValueError("body content appears before the first semantic page marker")

    pages: list[SemanticPage] = []
    for index, match in enumerate(matches):
        kind = match.group(1)
        if kind not in PAGE_TYPES:
            allowed = ", ".join(sorted(PAGE_TYPES))
            raise ValueError(f"unsupported page type '{kind}'; expected one of: {allowed}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        page_markdown = body[match.end() : end].strip()
        if not page_markdown:
            raise ValueError(f"page {index + 1} ({kind}) is empty")
        if kind == "two_column":
            if len(COLUMN_MARKER.findall(page_markdown)) != 2:
                raise ValueError(
                    f"page {index + 1} (two_column) requires exactly two <!-- column --> markers"
                )
        elif COLUMN_MARKER.search(page_markdown):
            raise ValueError(
                f"page {index + 1} ({kind}) contains a column marker but is not two_column"
            )
        if MARKDOWN_IMAGE.search(page_markdown):
            raise ValueError(
                f"page {index + 1} contains a Markdown image; body images are not supported in V1"
            )
        pages.append(SemanticPage(kind=kind, markdown=page_markdown))

    validate_cover_metadata(metadata)
    return Article(metadata=metadata, pages=tuple(pages), body=body)


def metadata_text(metadata: dict[str, object], key: str) -> str:
    return str(metadata.get(key, "")).strip()


def validate_cover_metadata(metadata: dict[str, object]) -> None:
    required = ("cover_lead", "cover_focus", "cover_bridge", "cover_emphasis")
    missing = [key for key in required if not metadata_text(metadata, key)]
    if missing:
        raise ValueError(
            "cover requires confirmed front-matter fields: " + ", ".join(missing)
        )


def build_cover_html(metadata: dict[str, object]) -> str:
    validate_cover_metadata(metadata)
    css = CSS_PATH.read_text(encoding="utf-8")
    document = COVER_TEMPLATE_PATH.read_text(encoding="utf-8")
    series = metadata_text(metadata, "series_label")
    topic = metadata_text(metadata, "topic_label")
    replacements = {
        "/*__CSS__*/": css,
        "__SERIES__": html.escape(series),
        "__TOPIC__": html.escape(topic),
        "__LEAD__": html.escape(metadata_text(metadata, "cover_lead")),
        "__FOCUS__": html.escape(metadata_text(metadata, "cover_focus")),
        "__BRIDGE__": html.escape(metadata_text(metadata, "cover_bridge")),
        "__EMPHASIS__": html.escape(metadata_text(metadata, "cover_emphasis")),
        "__SUBTITLE__": html.escape(metadata_text(metadata, "subtitle")),
    }
    for token, replacement in replacements.items():
        document = document.replace(token, replacement)
    if not series and not topic:
        document = re.sub(r"<header class=\"cover-kicker\">.*?</header>", "", document)
    elif not topic:
        document = document.replace('<span class="dot">·</span><span class="topic"></span>', "")
    elif not series:
        document = document.replace('<span class="label"></span><span class="dot">·</span>', "")
    return document


def safe_markdown(value: str) -> str:
    """Render Markdown while preventing raw HTML or runtime body assets."""
    # Escaping '<' is sufficient to disable raw HTML. Keep '>' intact because
    # it is the standard Markdown blockquote marker used by callout pages.
    escaped = value.replace("&", "&amp;").replace("<", "&lt;")
    return markdown.markdown(
        escaped,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )


def build_body_content(page: SemanticPage) -> str:
    if page.kind != "two_column":
        if AUTHOR_SIGNOFF_MARKER in page.markdown:
            if page.markdown.count(AUTHOR_SIGNOFF_MARKER) != 1:
                raise ValueError("a page may contain only one author-signoff marker")
            before, after = page.markdown.split(AUTHOR_SIGNOFF_MARKER, 1)
            if not re.match(r"^\s*>\s+", after):
                raise ValueError("author-signoff marker must be followed by a blockquote")
            before_html = safe_markdown(before.strip()) if before.strip() else ""
            after_html = safe_markdown(after.strip()).replace(
                "<blockquote>", '<blockquote class="author-signoff">', 1
            )
            return before_html + after_html
        return safe_markdown(page.markdown)

    parts = COLUMN_MARKER.split(page.markdown)
    if len(parts) != 3:
        raise ValueError("two_column page must contain a heading block and two columns")
    heading, left, right = (part.strip() for part in parts)
    if not left or not right:
        raise ValueError("two_column page columns cannot be empty")
    heading_html = safe_markdown(heading) if heading else ""
    return (
        heading_html
        + '<div class="semantic-columns">'
        + f'<section class="semantic-column">{safe_markdown(left)}</section>'
        + f'<section class="semantic-column">{safe_markdown(right)}</section>'
        + "</div>"
    )


def build_body_html(page: SemanticPage, number: int) -> str:
    document = CARD_TEMPLATE_PATH.read_text(encoding="utf-8")
    replacements = {
        "/*__CSS__*/": CSS_PATH.read_text(encoding="utf-8"),
        "__PAGE_TYPE__": page.kind,
        "__CONTENT__": build_body_content(page),
        "__PAGE_NUMBER__": f"{number:02d}",
    }
    for token, replacement in replacements.items():
        document = document.replace(token, replacement)
    return document


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a valid PNG: {path}")
    return struct.unpack(">II", data[16:24])


async def screenshot_document(
    browser: Browser,
    document: str,
    output: Path,
    *,
    cover: bool,
) -> dict[str, float]:
    page = await browser.new_page(
        viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1
    )
    await page.set_content(document, wait_until="load")
    await page.evaluate("document.fonts.ready")
    if cover:
        metrics = await page.evaluate(
            """() => ({
                width: document.body.scrollWidth,
                height: document.body.scrollHeight,
                headlineBottom: document.querySelector('.cover-title').getBoundingClientRect().bottom,
                ruleTop: document.querySelector('.cover-bottom-rule').getBoundingClientRect().top,
                subtitleBottom: document.querySelector('.cover-subtitle').getBoundingClientRect().bottom
            })"""
        )
        if metrics["width"] > WIDTH or metrics["height"] > HEIGHT:
            raise ValueError(f"cover overflows its canvas: {metrics}")
        if metrics["headlineBottom"] >= metrics["ruleTop"] - 20:
            raise ValueError(f"cover headline collides with the lower rule: {metrics}")
        if metrics["subtitleBottom"] > HEIGHT - 30:
            raise ValueError(f"cover subtitle overflows its canvas: {metrics}")
    else:
        metrics = await page.evaluate(
            """() => {
                const content = document.querySelector('.content').getBoundingClientRect();
                const rule = document.querySelector('.page-rule').getBoundingClientRect();
                return {
                    width: document.body.scrollWidth,
                    height: document.body.scrollHeight,
                    contentTop: content.top,
                    contentBottom: content.bottom,
                    ruleTop: rule.top,
                    contentRight: content.right
                };
            }"""
        )
        if metrics["width"] > WIDTH or metrics["height"] > HEIGHT:
            raise ValueError(f"body page overflows its canvas: {metrics}")
        if metrics["contentBottom"] >= metrics["ruleTop"] - FOOTER_CLEARANCE:
            raise ValueError(f"body content collides with the footer: {metrics}")
        if metrics["contentRight"] > WIDTH - 50:
            raise ValueError(f"body content overflows horizontally: {metrics}")

    await page.screenshot(path=str(output), full_page=False)
    await page.close()
    dimensions = png_dimensions(output)
    if dimensions != (WIDTH, HEIGHT):
        raise ValueError(
            f"expected {WIDTH}x{HEIGHT}, got {dimensions[0]}x{dimensions[1]} for {output.name}"
        )
    return metrics


async def inspect_document(
    browser: Browser,
    document: str,
    *,
    cover: bool,
) -> dict[str, float]:
    """Measure and validate one document without creating an image."""
    page = await browser.new_page(
        viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1
    )
    await page.set_content(document, wait_until="load")
    await page.evaluate("document.fonts.ready")
    if cover:
        metrics = await page.evaluate(
            """() => ({
                width: document.body.scrollWidth,
                height: document.body.scrollHeight,
                headlineBottom: document.querySelector('.cover-title').getBoundingClientRect().bottom,
                ruleTop: document.querySelector('.cover-bottom-rule').getBoundingClientRect().top,
                subtitleBottom: document.querySelector('.cover-subtitle').getBoundingClientRect().bottom
            })"""
        )
        if metrics["width"] > WIDTH or metrics["height"] > HEIGHT:
            raise ValueError(f"cover overflows its canvas: {metrics}")
        if metrics["headlineBottom"] >= metrics["ruleTop"] - 20:
            raise ValueError(f"cover headline collides with the lower rule: {metrics}")
        if metrics["subtitleBottom"] > HEIGHT - 30:
            raise ValueError(f"cover subtitle overflows its canvas: {metrics}")
    else:
        metrics = await page.evaluate(
            """() => {
                const content = document.querySelector('.content').getBoundingClientRect();
                const rule = document.querySelector('.page-rule').getBoundingClientRect();
                return {
                    width: document.body.scrollWidth,
                    height: document.body.scrollHeight,
                    contentTop: content.top,
                    contentBottom: content.bottom,
                    ruleTop: rule.top,
                    contentRight: content.right
                };
            }"""
        )
        if metrics["width"] > WIDTH or metrics["height"] > HEIGHT:
            raise ValueError(f"body page overflows its canvas: {metrics}")
        if metrics["contentBottom"] >= metrics["ruleTop"] - FOOTER_CLEARANCE:
            raise ValueError(f"body content collides with the footer: {metrics}")
        if metrics["contentRight"] > WIDTH - 50:
            raise ValueError(f"body content overflows horizontally: {metrics}")
    await page.close()
    return metrics


async def preflight_article(article_path: Path, source_path: Path | None) -> dict[str, object]:
    """Validate an approved review draft without producing render artifacts."""
    article_path = article_path.expanduser().resolve()
    source_path = source_path.expanduser().resolve() if source_path else None
    article = parse_article(article_path)
    reconciliation = reconcile_source(article, source_path)
    page_records: list[dict[str, object]] = []
    density_violations: list[str] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        await inspect_document(browser, build_cover_html(article.metadata), cover=True)
        for index, semantic_page in enumerate(article.pages, start=1):
            try:
                metrics = await inspect_document(
                    browser,
                    build_body_html(semantic_page, index),
                    cover=False,
                )
            except ValueError as error:
                raise ValueError(
                    f"page {index} ({semantic_page.kind}) failed layout inspection: {error}"
                ) from error
            fill_ratio = body_fill_ratio(metrics)
            density_checked = density_is_required(index, len(article.pages))
            if density_checked and fill_ratio < MIN_CONTINUOUS_FILL_RATIO:
                density_violations.append(
                    f"page {index} ({semantic_page.kind}) is underfilled: "
                    f"fill ratio {fill_ratio:.3f} is below {MIN_CONTINUOUS_FILL_RATIO:.2f}"
                )
            page_records.append(
                {
                    "number": index,
                    "type": semantic_page.kind,
                    "content_bottom": round(metrics["contentBottom"], 3),
                    "fill_ratio": round(fill_ratio, 3),
                    "density_checked": density_checked,
                }
            )
        await browser.close()
    if density_violations:
        raise ValueError("; ".join(density_violations))
    return {
        "status": "passed",
        "article": str(article_path),
        "page_count": len(article.pages),
        "minimum_continuous_fill_ratio": MIN_CONTINUOUS_FILL_RATIO,
        "source_reconciliation": reconciliation,
        "pages": page_records,
    }


def contact_sheet_html(paths: list[Path], page_types: list[str]) -> tuple[str, int, int]:
    columns = min(4, len(paths))
    tile_width = 360
    gap = 28
    padding = 46
    width = padding * 2 + columns * tile_width + (columns - 1) * gap
    rows = (len(paths) + columns - 1) // columns
    tile_height = 530
    height = 110 + padding * 2 + rows * tile_height + (rows - 1) * gap
    figures = []
    for path, label in zip(paths, page_types):
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        figures.append(
            '<figure><img src="data:image/png;base64,'
            + encoded
            + f'"><figcaption>{html.escape(label)}</figcaption></figure>'
        )
    document = f"""<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}html,body{{margin:0;width:{width}px;min-height:{height}px;background:#e9e5df}}
    body{{padding:{padding}px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}}
    h1{{margin:0 0 34px;font-size:38px;color:#222}}main{{display:grid;grid-template-columns:repeat({columns},1fr);gap:{gap}px}}
    figure{{margin:0;padding:12px;background:white;border-radius:12px;box-shadow:0 5px 18px rgba(0,0,0,.08)}}
    img{{display:block;width:100%;aspect-ratio:3/4;object-fit:contain}}
    figcaption{{padding:12px 2px 2px;text-align:center;font-size:18px;color:#625d57}}
    </style></head><body><h1>RedNote article review</h1><main>{''.join(figures)}</main></body></html>"""
    return document, width, height


async def render_contact_sheet(
    browser: Browser,
    paths: list[Path],
    page_types: list[str],
    output: Path,
) -> None:
    document, width, height = contact_sheet_html(paths, page_types)
    page = await browser.new_page(
        viewport={"width": width, "height": height}, device_scale_factor=1
    )
    await page.set_content(document, wait_until="load")
    await page.wait_for_function(
        "Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)",
        timeout=10000,
    )
    await page.screenshot(path=str(output), full_page=True)
    await page.close()


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def markdown_visible_text(value: str) -> str:
    without_markers = PAGE_MARKER.sub("", value)
    without_markers = COLUMN_MARKER.sub("", without_markers)
    without_markers = without_markers.replace(AUTHOR_SIGNOFF_MARKER, "")
    rendered = safe_markdown(without_markers)
    parser = TextExtractor()
    parser.feed(rendered)
    return "".join(parser.parts)


def semantic_source_text(value: str) -> str:
    """Remove project Markdown syntax without interpreting source prose as Markdown.

    The same normalization is applied to the plain source and reviewed Markdown.
    This avoids treating an original line such as ``1. Heading`` as a generated
    list marker on only one side of the comparison.
    """
    value = PAGE_MARKER.sub("", value)
    value = COLUMN_MARKER.sub("", value)
    value = value.replace(AUTHOR_SIGNOFF_MARKER, "")
    normalized_lines: list[str] = []
    for line in value.splitlines():
        line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)
        line = re.sub(r"^\s{0,3}>\s?", "", line)
        line = re.sub(r"^\s{0,3}[-+*]\s+", "", line)
        line = re.sub(r"^\s{0,3}\d+[.)]\s+", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
        # Apply symmetrically to source and reviewed Markdown so literal marks,
        # when present in the source, do not create a one-sided comparison.
        # This supports bold, red accent, and bold-red review syntax.
        line = line.replace("*", "").replace("_", "").replace("`", "")
        normalized_lines.append(line)
    return "\n".join(normalized_lines)


def comparison_key(value: str) -> str:
    return re.sub(r"\s+", "", html.unescape(value))


def reconcile_source(
    article: Article,
    source_path: Path | None,
    *,
    allow_reviewed_edits: bool = False,
) -> dict[str, object]:
    if source_path is None:
        return {
            "status": "not_requested",
            "note": "Pass --source-txt to verify that source text is preserved in order.",
        }
    raw = source_path.read_bytes()
    try:
        source = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("source TXT must be UTF-8 encoded") from exc
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    source_title = metadata_text(article.metadata, "source_title")
    title = source_title or metadata_text(article.metadata, "title")
    lines = source.splitlines()
    first = next((index for index, line in enumerate(lines) if line.strip()), None)
    if first is not None and title and lines[first].strip() == title:
        lines.pop(first)
        if first < len(lines) and not lines[first].strip():
            lines.pop(first)
        source = "\n".join(lines)

    source_key = comparison_key(semantic_source_text(source))
    rendered_key = comparison_key(semantic_source_text(article.body))
    if source_key != rendered_key:
        prefix = 0
        for left, right in zip(source_key, rendered_key):
            if left != right:
                break
            prefix += 1
        if not allow_reviewed_edits:
            raise ValueError(
                "source reconciliation failed: reviewed Markdown changes, drops, duplicates, "
                f"or reorders source text near normalized character {prefix}"
            )
        return {
            "status": "human_approved_edits",
            "source_path": str(source_path.resolve()),
            "source_sha256": sha256_bytes(raw),
            "source_normalized_character_count": len(source_key),
            "reviewed_normalized_character_count": len(rendered_key),
            "first_difference_at_normalized_character": prefix,
            "note": "Original source is preserved; reviewed text changes were explicitly approved by the user.",
        }
    return {
        "status": "passed",
        "source_path": str(source_path.resolve()),
        "source_sha256": sha256_bytes(raw),
        "normalized_character_count": len(source_key),
    }


def protected_outputs(output_dir: Path, page_count: int) -> list[Path]:
    expected = [output_dir / "cover.png", output_dir / "contact-sheet.png", output_dir / "manifest.json"]
    expected.extend(output_dir / f"card-{index:02d}.png" for index in range(1, page_count + 1))
    return expected


def assert_outputs_available(output_dir: Path, page_count: int) -> None:
    conflicts = [path for path in protected_outputs(output_dir, page_count) if path.exists()]
    conflicts.extend(path for path in output_dir.glob("card-*.png") if path not in conflicts)
    if conflicts:
        names = ", ".join(sorted({path.name for path in conflicts}))
        raise FileExistsError(f"refusing to overwrite existing render artifacts: {names}")


async def render_article(
    article_path: Path,
    output_dir: Path,
    source_path: Path | None,
    *,
    allow_reviewed_edits: bool = False,
) -> Path:
    article_path = article_path.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    source_path = source_path.expanduser().resolve() if source_path else None
    article = parse_article(article_path)
    reconciliation = reconcile_source(
        article,
        source_path,
        allow_reviewed_edits=allow_reviewed_edits,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    assert_outputs_available(output_dir, len(article.pages))

    with tempfile.TemporaryDirectory(prefix="rednote-render-", dir=output_dir.parent) as temporary:
        staging = Path(temporary)
        cover_path = staging / "cover.png"
        card_paths = [
            staging / f"card-{index:02d}.png"
            for index in range(1, len(article.pages) + 1)
        ]
        contact_path = staging / "contact-sheet.png"

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            await screenshot_document(
                browser, build_cover_html(article.metadata), cover_path, cover=True
            )
            page_metrics: list[dict[str, float]] = []
            for index, semantic_page in enumerate(article.pages, start=1):
                metrics = await screenshot_document(
                    browser,
                    build_body_html(semantic_page, index),
                    card_paths[index - 1],
                    cover=False,
                )
                require_page_density(
                    metrics,
                    index,
                    len(article.pages),
                    semantic_page.kind,
                )
                page_metrics.append(metrics)
            all_paths = [cover_path, *card_paths]
            all_types = ["cover", *[page.kind for page in article.pages]]
            await render_contact_sheet(browser, all_paths, all_types, contact_path)
            await browser.close()

        page_records = []
        for index, (page, path, metrics) in enumerate(
            zip(article.pages, card_paths, page_metrics),
            start=1,
        ):
            fill_ratio = body_fill_ratio(metrics)
            page_records.append(
                {
                    "number": index,
                    "type": page.kind,
                    "file": path.name,
                    "sha256": sha256_file(path),
                    "dimensions": [WIDTH, HEIGHT],
                    "fill_ratio": round(fill_ratio, 3),
                    "density_checked": density_is_required(index, len(article.pages)),
                    "source_character_count": len(comparison_key(semantic_source_text(page.markdown))),
                    "source_text_sha256": sha256_bytes(
                        comparison_key(semantic_source_text(page.markdown)).encode("utf-8")
                    ),
                }
            )

        manifest = {
            "schema_version": 1,
            "renderer": {
                "name": "rednote-editorial-renderer",
                "upstream": "cnfjlhj/xhs-note-creator",
                "upstream_commit": UPSTREAM_COMMIT,
                "canvas": [WIDTH, HEIGHT],
                "device_scale_factor": 1,
            },
            "input": {
                "path": str(article_path),
                "sha256": sha256_file(article_path),
            },
            "cover": {
                "file": "cover.png",
                "sha256": sha256_file(cover_path),
                "dimensions": [WIDTH, HEIGHT],
            },
            "pages": page_records,
            "structural_transformations": [
                {
                    "type": "semantic_page_assignment",
                    "page": index,
                    "page_type": page.kind,
                    "body_text_changed": False,
                }
                for index, page in enumerate(article.pages, start=1)
            ],
            "source_reconciliation": reconciliation,
            "review_artifact": {
                "file": "contact-sheet.png",
                "sha256": sha256_file(contact_path),
            },
        }
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        for staged in [cover_path, *card_paths, contact_path, manifest_path]:
            shutil.move(str(staged), str(output_dir / staged.name))

    return output_dir / "contact-sheet.png"


def main() -> int:
    args = parse_args()
    article_path = args.markdown.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else article_path.parent
    )
    try:
        if args.preflight:
            if args.allow_reviewed_edits:
                article = parse_article(article_path)
                reconcile_source(
                    article,
                    args.source_txt,
                    allow_reviewed_edits=True,
                )
                result = asyncio.run(preflight_article(article_path, None))
                result["source_reconciliation"] = reconcile_source(
                    article,
                    args.source_txt,
                    allow_reviewed_edits=True,
                )
            else:
                result = asyncio.run(preflight_article(article_path, args.source_txt))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        contact_sheet = asyncio.run(
            render_article(
                article_path,
                output_dir,
                args.source_txt,
                allow_reviewed_edits=args.allow_reviewed_edits,
            )
        )
    except (
        FileExistsError,
        FileNotFoundError,
        OSError,
        PlaywrightError,
        ValueError,
        yaml.YAMLError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(contact_sheet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
