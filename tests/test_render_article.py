import tempfile
import unittest
from pathlib import Path

from scripts.render_article import (
    AUTHOR_SIGNOFF_MARKER,
    FOOTER_CLEARANCE,
    MIN_CONTINUOUS_FILL_RATIO,
    PAGE_TYPES,
    Article,
    SemanticPage,
    body_fill_ratio,
    build_body_html,
    comparison_key,
    density_is_required,
    parse_article,
    reconcile_source,
    require_page_density,
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

            result = reconcile_source(article, changed, allow_reviewed_edits=True)
            self.assertEqual(result["status"], "human_approved_edits")
            self.assertIn("first_difference_at_normalized_character", result)

    def test_reconciliation_uses_immutable_source_title(self):
        article = Article(
            metadata={"title": "新的封面标题", "source_title": "原始文章标题"},
            pages=(SemanticPage(kind="prose", markdown="正文。"),),
            body="<!-- page: prose -->\n\n正文。",
        )
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.txt"
            source.write_text("原始文章标题\n\n正文。\n", encoding="utf-8")
            self.assertEqual(reconcile_source(article, source)["status"], "passed")

    def test_density_requires_seventy_five_percent_except_final_page(self):
        self.assertEqual(MIN_CONTINUOUS_FILL_RATIO, 0.75)
        self.assertTrue(density_is_required(1, 2))
        self.assertFalse(density_is_required(2, 2))

    def test_final_render_density_validation_matches_preflight(self):
        metrics = {
            "contentTop": 100.0,
            "contentBottom": 700.0,
            "ruleTop": 1000.0,
        }
        expected_ratio = 600 / (900 - FOOTER_CLEARANCE)
        self.assertAlmostEqual(body_fill_ratio(metrics), expected_ratio)
        with self.assertRaisesRegex(ValueError, "page 1 .* is underfilled"):
            require_page_density(metrics, 1, 2, "prose")
        self.assertAlmostEqual(require_page_density(metrics, 2, 2, "prose"), expected_ratio)

    def test_numbered_source_heading_matches_markdown_heading(self):
        source = "1. 原始编号标题\n正文"
        reviewed = "## 1. 原始编号标题\n\n正文"
        self.assertEqual(
            comparison_key(semantic_source_text(source)),
            comparison_key(semantic_source_text(reviewed)),
        )

    def test_color_and_bold_emphasis_preserve_source_text(self):
        source = "普通句子。\n红色重点。\n加粗红色重点。"
        reviewed = "普通句子。\n\n*红色重点。*\n\n***加粗红色重点。***"
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

    def test_author_signoff_marker_creates_reference_style_callout(self):
        document = build_body_html(
            SemanticPage(
                kind="prose",
                markdown=f"正文。\n\n{AUTHOR_SIGNOFF_MARKER}\n\n> 作者签名。",
            ),
            1,
        )
        self.assertIn('<blockquote class="author-signoff">', document)
        self.assertNotIn(AUTHOR_SIGNOFF_MARKER, document)

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
