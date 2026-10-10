#!/usr/bin/env python3
"""Convert a finished UTF-8 text article into an auditable Markdown intermediate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Wrap a finished UTF-8 .txt article in renderer-compatible YAML "
            "front matter without rewriting its body."
        )
    )
    parser.add_argument("source", type=Path, help="Path to the finished .txt article")
    parser.add_argument("--title", help="Cover/article title; defaults to the filename stem")
    parser.add_argument("--subtitle", help="Optional cover subtitle")
    parser.add_argument("--series-label", help="Optional publication series label")
    parser.add_argument("--footer-label", help="Optional English cover footer label")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output"),
        help="Versioned output root (default: output)",
    )
    parser.add_argument(
        "--slug",
        help="Output article slug; defaults to a filesystem-safe form of the title",
    )
    parser.add_argument(
        "--run-id",
        help="Run folder name; defaults to a UTC timestamp. Existing runs are never overwritten.",
    )
    parser.add_argument(
        "--infer-structure",
        action="store_true",
        help=(
            "Add conservative Markdown headings, lists, quotes, and emphasis. "
            "The body wording and order remain unchanged."
        ),
    )
    return parser.parse_args()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_text(raw: bytes) -> tuple[str, list[dict[str, object]]]:
    transformations: list[dict[str, object]] = []
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("source must be UTF-8 encoded") from exc

    if raw.startswith(b"\xef\xbb\xbf"):
        transformations.append({"type": "remove_utf8_bom"})

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized != text:
        transformations.append({"type": "normalize_line_endings", "to": "LF"})

    if not normalized.endswith("\n"):
        normalized += "\n"
        transformations.append({"type": "add_final_newline"})

    return normalized, transformations


def safe_slug(value: str) -> str:
    slug = value.strip().lower()
    slug = re.sub(r"[\\/:*?\"<>|]", "-", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-. ")
    return slug[:80] or "article"


def yaml_string(value: str) -> str:
    # JSON strings are valid YAML scalars and avoid a second serialization dependency.
    return json.dumps(value, ensure_ascii=False)


def build_front_matter(metadata: dict[str, str]) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if value:
            lines.append(f"{key}: {yaml_string(value)}")
    lines.extend(["---", ""])
    return "\n".join(lines)


SECTION_PATTERN = re.compile(r"^[一二三四五六七八九十]+、\S")
SUBSECTION_PATTERN = re.compile(r"^\d+\.\s+\S")
LIST_TRIGGER_FRAGMENTS = (
    "两件完全不同的事",
    "这样的反馈",
    "可以读取的信号",
    "更实际的问题",
)
EMPHASIS_PREFIXES = (
    "能力 → 贡献 →",
    "无法被读取的价值",
    "健康的自我呈现",
    "不要再主动删除事实",
    "真正的体面",
)


def infer_markdown_structure(body: str, title: str) -> tuple[str, list[dict[str, object]]]:
    """Apply conservative, text-preserving Markdown classification."""
    lines = body.rstrip("\n").split("\n")
    transformations: list[dict[str, object]] = []

    first_content = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first_content is not None and lines[first_content].strip() == title:
        lines.pop(first_content)
        if first_content < len(lines) and not lines[first_content].strip():
            lines.pop(first_content)
        transformations.append(
            {
                "type": "promote_first_line_to_title",
                "text": title,
                "body_text_changed": False,
            }
        )

    classified: list[str] = []
    previous_plain = ""
    for line in lines:
        stripped = line.strip()
        replacement = line
        role = None
        if SECTION_PATTERN.match(stripped):
            replacement = f"# {stripped}"
            role = "section_heading"
        elif SUBSECTION_PATTERN.match(stripped):
            replacement = f"## {stripped}"
            role = "numbered_subheading"
        elif stripped.startswith("“") and stripped.endswith("”"):
            replacement = f"> {stripped}"
            role = "quotation"
        elif stripped and (
            stripped.startswith(EMPHASIS_PREFIXES)
            or previous_plain in {"而是：", "所以我越来越喜欢一句话：", "你只需要先做一件事："}
        ):
            replacement = f"**{stripped}**"
            role = "emphasis"

        classified.append(replacement)
        if role:
            transformations.append(
                {"type": "classify_block", "role": role, "text": stripped, "body_text_changed": False}
            )
        if stripped:
            previous_plain = stripped

    lines = classified
    i = 0
    while i < len(lines):
        trigger = re.sub(r"^[#>*\-\s]+", "", lines[i]).strip("*")
        if not any(fragment in trigger for fragment in LIST_TRIGGER_FRAGMENTS):
            i += 1
            continue

        candidates: list[int] = []
        j = i + 1
        question_list = j < len(lines) and lines[j].strip().endswith(("？", "?"))
        while j < len(lines) and len(candidates) < 8:
            plain = lines[j].strip()
            if not plain or plain.startswith(("# ", "## ")):
                break
            if len(plain) > 90:
                break
            if question_list and not plain.endswith(("？", "?")):
                break
            if plain.endswith(("；", ";", "？", "?", "。")):
                candidates.append(j)
                if plain.endswith("。") and len(candidates) >= 2:
                    break
                j += 1
                continue
            break

        if len(candidates) >= 2:
            for index in candidates:
                plain = lines[index].strip()
                lines[index] = f"- {plain}"
                transformations.append(
                    {
                        "type": "classify_block",
                        "role": "bullet_item",
                        "text": plain,
                        "body_text_changed": False,
                    }
                )
            i = candidates[-1] + 1
        else:
            i += 1

    return "\n".join(lines).rstrip() + "\n", transformations


def choose_run_directory(output_root: Path, slug: str, requested_id: str | None) -> Path:
    run_id = requested_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = output_root / slug / run_id
    if candidate.exists():
        raise FileExistsError(
            f"refusing to overwrite existing run: {candidate}. Choose a different --run-id."
        )
    return candidate


def convert(args: argparse.Namespace) -> Path:
    source = args.source.expanduser().resolve()
    if source.suffix.lower() != ".txt":
        raise ValueError(f"expected a .txt source, got: {source.name}")
    if not source.is_file():
        raise FileNotFoundError(f"source file not found: {source}")

    raw = source.read_bytes()
    body, transformations = normalize_text(raw)
    title = (args.title or source.stem).strip()
    if not title:
        raise ValueError("title cannot be empty")

    semantic_transformations: list[dict[str, object]] = []
    if args.infer_structure:
        body, semantic_transformations = infer_markdown_structure(body, title)

    metadata = {
        "title": title,
        "subtitle": (args.subtitle or "").strip(),
        "series_label": (args.series_label or "").strip(),
        "footer_label": (args.footer_label or "").strip(),
        "source_file": source.name,
        "source_format": "txt",
        "conversion_mode": "structured" if args.infer_structure else "faithful",
    }
    slug = safe_slug(args.slug or title)
    run_dir = choose_run_directory(args.output_root, slug, args.run_id)
    run_dir.mkdir(parents=True)

    rendered = build_front_matter(metadata) + body
    rendered_path = run_dir / "rendered.md"
    rendered_path.write_text(rendered, encoding="utf-8", newline="\n")

    manifest = {
        "schema_version": 1,
        "stage": "txt_to_semantic_md" if args.infer_structure else "txt_to_md",
        "source": {
            "path": str(source),
            "filename": source.name,
            "sha256": sha256(raw),
            "encoding": "utf-8",
        },
        "output": {
            "path": str(rendered_path.resolve()),
            "sha256": sha256(rendered.encode("utf-8")),
        },
        "metadata": metadata,
        "transformations": [
            *transformations,
            {"type": "add_yaml_front_matter", "body_text_changed": False},
            *semantic_transformations,
        ],
        "semantic_classification": "conservative_heuristic" if args.infer_structure else "not_performed",
    }
    (run_dir / "conversion.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return rendered_path


def main() -> int:
    args = parse_args()
    try:
        output = convert(args)
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
