#!/usr/bin/env python3
"""Deterministically repaginate reviewed semantic Markdown using real browser layout.

The packing loop adapts the upstream renderer's measured auto-split approach,
then adds semantic atoms, sentence fallback, heading protection, and density
enforcement for this repository's fixed editorial theme.
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Awaitable, Callable, Sequence

from playwright.async_api import async_playwright

try:
    from scripts.render_article import (
        AUTHOR_SIGNOFF_MARKER,
        FOOTER_CLEARANCE,
        FRONT_MATTER,
        HEIGHT,
        MIN_CONTINUOUS_FILL_RATIO,
        WIDTH,
        SemanticPage,
        build_body_html,
        parse_article,
        reconcile_source,
    )
except ModuleNotFoundError:  # Direct execution from scripts/.
    from render_article import (  # type: ignore[no-redef]
        AUTHOR_SIGNOFF_MARKER,
        FOOTER_CLEARANCE,
        FRONT_MATTER,
        HEIGHT,
        MIN_CONTINUOUS_FILL_RATIO,
        WIDTH,
        SemanticPage,
        build_body_html,
        parse_article,
        reconcile_source,
    )


SENTENCE = re.compile(r".*?[。！？!?](?:[”’\"）】》])?|.+$", re.DOTALL)
SPECIAL_BLOCK = re.compile(r"^(?:#{1,6}\s|>|[-+*]\s|\d+[.)]\s)")


@dataclass(frozen=True)
class FlowUnit:
    text: str
    block_id: int


@dataclass(frozen=True)
class Measurement:
    fits: bool
    fill_ratio: float


def split_plain_sentences(block: str) -> list[str]:
    """Split ordinary prose at sentence boundaries; preserve semantic blocks."""
    stripped = block.strip()
    if stripped == AUTHOR_SIGNOFF_MARKER:
        return [stripped]
    if (
        not stripped
        or "\n" in stripped
        or SPECIAL_BLOCK.match(stripped)
        or any(token in stripped for token in ("**", "__", "![", "]("))
    ):
        return [stripped]
    sentences = [match.group(0) for match in SENTENCE.finditer(stripped) if match.group(0)]
    return sentences or [stripped]


def atomize_blocks(blocks: Sequence[str]) -> list[tuple[FlowUnit, ...]]:
    """Create indivisible layout atoms and keep headings with first body sentence."""
    units: list[FlowUnit] = []
    for block_id, block in enumerate(blocks):
        units.extend(FlowUnit(sentence, block_id) for sentence in split_plain_sentences(block))

    atoms: list[tuple[FlowUnit, ...]] = []
    index = 0
    while index < len(units):
        unit = units[index]
        if (
            re.match(r"^#{1,6}\s", unit.text)
            or unit.text == AUTHOR_SIGNOFF_MARKER
        ) and index + 1 < len(units):
            atoms.append((unit, units[index + 1]))
            index += 2
        else:
            atoms.append((unit,))
            index += 1
    return atoms


def assemble_units(units: Sequence[FlowUnit]) -> str:
    parts: list[str] = []
    previous_block: int | None = None
    for unit in units:
        if parts and unit.block_id != previous_block:
            parts.append("\n\n")
        parts.append(unit.text)
        previous_block = unit.block_id
    return "".join(parts)


async def paginate_segment(
    atoms: Sequence[tuple[FlowUnit, ...]],
    fits: Callable[[str], Awaitable[bool]],
) -> list[list[FlowUnit]]:
    """First-fit sequential packing against the caller's real layout measurement."""
    pages: list[list[FlowUnit]] = []
    current: list[FlowUnit] = []
    for atom in atoms:
        candidate = [*current, *atom]
        if await fits(assemble_units(candidate)):
            current = candidate
            continue
        if not current:
            raise ValueError(f"semantic atom does not fit on an empty page: {assemble_units(atom)!r}")
        pages.append(current)
        current = list(atom)
        if not await fits(assemble_units(current)):
            raise ValueError(f"semantic atom does not fit on an empty page: {assemble_units(atom)!r}")
    if current:
        pages.append(current)
    return pages


async def pack_atom_pages(
    atoms: Sequence[tuple[FlowUnit, ...]],
    measure: Callable[[str], Awaitable[Measurement]],
) -> list[list[tuple[FlowUnit, ...]]]:
    """Greedily pack whole semantic atoms while retaining atom boundaries."""
    pages: list[list[tuple[FlowUnit, ...]]] = []
    current: list[tuple[FlowUnit, ...]] = []
    for atom in atoms:
        candidate = [*current, atom]
        candidate_units = [unit for item in candidate for unit in item]
        if (await measure(assemble_units(candidate_units))).fits:
            current = candidate
            continue
        if not current:
            raise ValueError(f"semantic atom does not fit on an empty page: {assemble_units(atom)!r}")
        pages.append(current)
        current = [atom]
        if not (await measure(assemble_units(atom))).fits:
            raise ValueError(f"semantic atom does not fit on an empty page: {assemble_units(atom)!r}")
    if current:
        pages.append(current)
    return pages


async def rebalance_tail(
    pages: list[list[tuple[FlowUnit, ...]]],
    measure: Callable[[str], Awaitable[Measurement]],
    minimum_fill: float,
    maximum_window: int = 4,
) -> list[list[tuple[FlowUnit, ...]]]:
    """Repartition a sparse segment tail without changing order or atom integrity."""
    if len(pages) < 2:
        return pages

    async def page_measure(atom_page: Sequence[tuple[FlowUnit, ...]]) -> Measurement:
        units = [unit for atom in atom_page for unit in atom]
        return await measure(assemble_units(units))

    if (await page_measure(pages[-1])).fill_ratio >= minimum_fill:
        return pages

    for window in range(2, min(maximum_window, len(pages)) + 1):
        prefix = pages[:-window]
        tail_atoms = [atom for page in pages[-window:] for atom in page]
        cache: dict[tuple[int, int], Measurement] = {}

        async def range_measure(start: int, end: int) -> Measurement:
            key = (start, end)
            if key not in cache:
                cache[key] = await page_measure(tail_atoms[start:end])
            return cache[key]

        best: tuple[float, list[list[tuple[FlowUnit, ...]]]] | None = None

        async def search(
            start: int,
            groups_left: int,
            selected: list[list[tuple[FlowUnit, ...]]],
            fills: list[float],
        ) -> None:
            nonlocal best
            if groups_left == 1:
                if start >= len(tail_atoms):
                    return
                measurement = await range_measure(start, len(tail_atoms))
                if not measurement.fits or measurement.fill_ratio < minimum_fill:
                    return
                candidate = [*selected, tail_atoms[start:]]
                candidate_fills = [*fills, measurement.fill_ratio]
                mean = sum(candidate_fills) / len(candidate_fills)
                score = sum((fill - mean) ** 2 for fill in candidate_fills)
                if best is None or score < best[0]:
                    best = (score, candidate)
                return

            final_end = len(tail_atoms) - groups_left + 1
            for end in range(start + 1, final_end + 1):
                measurement = await range_measure(start, end)
                if not measurement.fits:
                    break
                if measurement.fill_ratio < minimum_fill:
                    continue
                await search(
                    end,
                    groups_left - 1,
                    [*selected, tail_atoms[start:end]],
                    [*fills, measurement.fill_ratio],
                )

        await search(0, window, [], [])
        if best is not None:
            return [*prefix, *best[1]]
    return pages


def semantic_segments(pages: Sequence[SemanticPage]) -> list[tuple[str, list[str]]]:
    """Flatten old page markers while retaining semantic page-type transitions."""
    segments: list[tuple[str, list[str]]] = []
    for page in pages:
        blocks = [block.strip() for block in re.split(r"\n\s*\n", page.markdown) if block.strip()]
        if segments and segments[-1][0] == page.kind:
            segments[-1][1].extend(blocks)
        else:
            segments.append((page.kind, blocks))
    return segments


class BrowserMeasurer:
    """One reusable browser page hides all physical-layout measurement details."""

    def __init__(self, browser):
        self.browser = browser
        self.page = None

    async def __aenter__(self):
        self.page = await self.browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        await self.page.close()

    async def measure(self, kind: str, markdown_text: str) -> Measurement:
        document = build_body_html(SemanticPage(kind=kind, markdown=markdown_text), 1)
        await self.page.set_content(document, wait_until="load")
        metrics = await self.page.evaluate(
            """() => {
                const content = document.querySelector('.content').getBoundingClientRect();
                const rule = document.querySelector('.page-rule').getBoundingClientRect();
                return {
                    width: document.body.scrollWidth,
                    height: document.body.scrollHeight,
                    contentTop: content.top,
                    contentBottom: content.bottom,
                    contentRight: content.right,
                    ruleTop: rule.top
                };
            }"""
        )
        usable_bottom = metrics["ruleTop"] - FOOTER_CLEARANCE
        usable_height = usable_bottom - metrics["contentTop"]
        used_height = metrics["contentBottom"] - metrics["contentTop"]
        fits = (
            metrics["width"] <= WIDTH
            and metrics["height"] <= HEIGHT
            and metrics["contentBottom"] < usable_bottom
            and metrics["contentRight"] <= WIDTH - 50
        )
        return Measurement(fits=fits, fill_ratio=used_height / usable_height)


async def paginate_document(input_path: Path, minimum_fill: float) -> tuple[SemanticPage, ...]:
    article = parse_article(input_path)
    planned: list[SemanticPage] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        async with BrowserMeasurer(browser) as measurer:
            segments = semantic_segments(article.pages)
            for segment_index, (kind, blocks) in enumerate(segments):
                atoms = atomize_blocks(blocks)

                async def measure(markdown_text: str, page_kind: str = kind) -> Measurement:
                    return await measurer.measure(page_kind, markdown_text)

                packed_atoms = await pack_atom_pages(atoms, measure)
                if segment_index < len(segments) - 1:
                    packed_atoms = await rebalance_tail(
                        packed_atoms,
                        measure,
                        minimum_fill,
                    )
                packed = [
                    [unit for atom in atom_page for unit in atom]
                    for atom_page in packed_atoms
                ]
                planned.extend(
                    SemanticPage(kind=kind, markdown=assemble_units(page_units))
                    for page_units in packed
                )

            violations: list[str] = []
            for number, page in enumerate(planned, start=1):
                measurement = await measurer.measure(page.kind, page.markdown)
                if not measurement.fits:
                    violations.append(f"page {number} overflows")
                if number < len(planned) and measurement.fill_ratio < minimum_fill:
                    violations.append(
                        f"page {number} is {measurement.fill_ratio:.1%} full; "
                        f"minimum is {minimum_fill:.0%}"
                    )
        await browser.close()
    if violations:
        raise ValueError("deterministic pagination could not satisfy constraints: " + "; ".join(violations))
    return tuple(planned)


def serialize_review(input_path: Path, pages: Sequence[SemanticPage]) -> str:
    original = input_path.read_text(encoding="utf-8")
    front = FRONT_MATTER.match(original)
    if not front:
        raise ValueError("Markdown must begin with YAML front matter")
    body = "\n\n".join(
        f"<!-- page: {page.kind} -->\n\n{page.markdown.strip()}" for page in pages
    )
    return front.group(0) + body + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Reviewed semantic Markdown")
    parser.add_argument("output", type=Path, help="New paginated Markdown; must not exist")
    parser.add_argument("--source-txt", type=Path, help="Immutable source for reconciliation")
    parser.add_argument(
        "--minimum-fill",
        type=float,
        default=MIN_CONTINUOUS_FILL_RATIO,
        help=f"Required non-final fill ratio (default: {MIN_CONTINUOUS_FILL_RATIO:.2f})",
    )
    parser.add_argument(
        "--allow-reviewed-edits",
        action="store_true",
        help="Record explicit human-approved text edits while preserving the original source",
    )
    return parser.parse_args()


async def async_main() -> int:
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if output_path.exists():
        raise ValueError(f"refusing to overwrite existing output: {output_path}")
    if not 0 < args.minimum_fill < 1:
        raise ValueError("--minimum-fill must be between 0 and 1")
    pages = await paginate_document(input_path, args.minimum_fill)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialize_review(input_path, pages), encoding="utf-8")
    if args.source_txt:
        reconcile_source(
            parse_article(output_path),
            args.source_txt.expanduser().resolve(),
            allow_reviewed_edits=args.allow_reviewed_edits,
        )
    print(output_path)
    print(f"pages={len(pages)} minimum_non_final_fill={args.minimum_fill:.0%}")
    return 0


def main() -> int:
    try:
        return asyncio.run(async_main())
    except (OSError, ValueError) as error:
        print(f"error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
