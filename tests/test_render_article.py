import tempfile
import unittest
from pathlib import Path

from scripts.render_article import (
    PAGE_TYPES,
    SemanticPage,
    build_body_html,
    comparison_key,
    parse_article,
    reconcile_source,
    semantic_source_text,
)


ROOT = Path(__file__).resolve().parent.parent
SAMPLE_MD = ROOT / "tests" / "article-render" / "sample.md"
SAMPLE_TXT = ROOT / "tests" / "article-render" / "sample.txt"


class ArticleRendererTests(unittest.TestCase):
    def test_sample_exercises_every_supported_page_type(self):
        article = parse_article(SAMPLE_MD)
        self.assertEqual({page.kind for page in article.pages}, PAGE_TYPES)

    def test_reconciles_semantic_markdown_with_source(self):
        article = parse_article(SAMPLE_MD)
        result = reconcile_source(article, SAMPLE_TXT)
        self.assertEqual(result["status"], "passed")

    def test_reconciliation_rejects_changed_wording(self):
        article = parse_article(SAMPLE_MD)
        with tempfile.TemporaryDirectory() as temporary:
            changed = Path(temporary) / "changed.txt"
            changed.write_text(
                SAMPLE_TXT.read_text(encoding="utf-8").replace("一点点消失", "完全消失"),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                reconcile_source(article, changed)

    def test_numbered_source_heading_matches_markdown_heading(self):
        source = "1. 原始编号标题\n正文"
        reviewed = "## 1. 原始编号标题\n\n正文"
        self.assertEqual(
            comparison_key(semantic_source_text(source)),
            comparison_key(semantic_source_text(reviewed)),
        )

    def test_body_html_escapes_raw_html(self):
        document = build_body_html(
            SemanticPage(kind="prose", markdown="# 标题\n\n<script>alert(1)</script>"),
            1,
        )
        self.assertNotIn("<script>", document)
        self.assertIn("&lt;script&gt;", document.replace(">", "&gt;"))
        self.assertIn("page-type-prose", document)

    def test_two_column_requires_two_markers(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.md"
            path.write_text(
                "---\ncover_lead: a\ncover_focus: b\ncover_bridge: c\n"
                "cover_emphasis: d\n---\n<!-- page: two_column -->\n"
                "# 标题\n<!-- column -->\n左边",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                parse_article(path)


if __name__ == "__main__":
    unittest.main()
