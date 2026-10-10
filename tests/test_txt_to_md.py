import argparse
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.txt_to_md import convert


class TxtToMarkdownTests(unittest.TestCase):
    def make_args(self, source: Path, output_root: Path, run_id: str = "test-run"):
        return argparse.Namespace(
            source=source,
            title="测试标题",
            subtitle=None,
            series_label="社会观察",
            footer_label="POWER & BEHAVIOR",
            output_root=output_root,
            slug="test-article",
            run_id=run_id,
            infer_structure=False,
        )

    def test_preserves_body_and_records_normalization(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "article.txt"
            raw = "第一段。\r\n\r\n第二段。".encode("utf-8")
            source.write_bytes(raw)

            output = convert(self.make_args(source, root / "output"))
            rendered = output.read_text(encoding="utf-8")
            body = rendered.split("---\n", 2)[2]
            self.assertEqual(body, "第一段。\n\n第二段。\n")

            manifest = json.loads((output.parent / "conversion.json").read_text())
            self.assertEqual(manifest["source"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(manifest["semantic_classification"], "not_performed")
            self.assertIn(
                "normalize_line_endings",
                [item["type"] for item in manifest["transformations"]],
            )

    def test_refuses_to_overwrite_an_existing_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "article.txt"
            source.write_text("正文\n", encoding="utf-8")
            args = self.make_args(source, root / "output")
            convert(args)
            with self.assertRaises(FileExistsError):
                convert(args)

    def test_rejects_non_txt_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "article.md"
            source.write_text("正文\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                convert(self.make_args(source, root / "output"))

    def test_infers_structure_without_rewriting_words(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "article.txt"
            source.write_text(
                "测试标题\n\n一、第一部分\n小时候，我们得到这样的反馈：\n"
                "第一项；\n第二项；\n第三项。\n\n问几个更实际的问题。\n"
                "问题一？\n问题二？\n这是后续正文。\n\n1. 第一步\n“原话。”\n",
                encoding="utf-8",
            )
            args = self.make_args(source, root / "output")
            args.infer_structure = True
            output = convert(args)
            body = output.read_text(encoding="utf-8").split("---\n", 2)[2]
            self.assertNotIn("测试标题\n", body)
            self.assertIn("# 一、第一部分", body)
            self.assertIn("- 第一项；", body)
            self.assertIn("## 1. 第一步", body)
            self.assertIn("> “原话。”", body)
            self.assertIn("- 问题二？\n这是后续正文。", body)
            self.assertNotIn("- 这是后续正文。", body)

            plain = re.sub(r"(?m)^(?:#{1,2}|>|-)\s+", "", body)
            self.assertIn("一、第一部分", plain)
            self.assertIn("第一项；\n第二项；\n第三项。", plain)


if __name__ == "__main__":
    unittest.main()
