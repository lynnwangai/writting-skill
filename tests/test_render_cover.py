import argparse
import unittest

from scripts.render_cover import build_html


class CoverTemplateTests(unittest.TestCase):
    def test_requires_confirmed_headline_split(self):
        args = argparse.Namespace(
            lead=None,
            focus=None,
            bridge=None,
            emphasis=None,
            subtitle=None,
            series_label=None,
            topic_label=None,
        )
        with self.assertRaises(ValueError):
            build_html({"title": "未拆分标题"}, args)

    def test_escapes_content_and_has_no_remote_assets(self):
        args = argparse.Namespace(
            lead="黑色 <主标题>",
            focus="体面",
            bridge="其实是在",
            emphasis="红色 & 强调",
            subtitle=None,
            series_label=None,
            topic_label=None,
        )
        document = build_html(
            {
                "series_label": "社会观察",
                "topic_label": "功劳与可见度",
            },
            args,
        )
        self.assertIn("黑色 &lt;主标题&gt;", document)
        self.assertIn("红色 &amp; 强调", document)
        self.assertNotIn("https://", document)
        self.assertNotIn("@import", document)


if __name__ == "__main__":
    unittest.main()
