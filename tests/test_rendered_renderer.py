import tempfile
import unittest
from pathlib import Path

from scripts.publish.rendered_renderer import RenderedRendererError, render_work_record


class RenderedRendererTests(unittest.TestCase):
    def test_render_is_deterministic_and_uses_normalized_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "work_record_001.md"
            markdown.write_text(
                "# Markdown title\n"
                "作成日: 2000-01-01\n\n"
                "## 概要\n\n"
                "本文 **強調** と [参照](https://example.com/a?b=1)。\n\n"
                "- 項目\n",
                encoding="utf-8",
            )
            metadata = {
                "schema_version": 1,
                "title": "Metadata <title>",
                "date": "2026-08-28",
                "project_id": "tech_article_nortification",
                "tags": ["z", "a"],
                "publish": True,
            }

            first = render_work_record(markdown, metadata)
            second = render_work_record(markdown, metadata)

        self.assertEqual(first, second)
        self.assertIn("Metadata &lt;title&gt; — 作業記録 001", first)
        self.assertIn('datetime="2026-08-28">2026-08-28</time>', first)
        self.assertIn("<h2>概要</h2>", first)
        self.assertIn("<strong>強調</strong>", first)
        self.assertIn('<a href="https://example.com/a?b=1">参照</a>', first)
        self.assertIn("<li>a</li><li>z</li>", first)
        self.assertNotIn("2000-01-01", first)

    def test_raw_html_is_escaped_and_unsafe_links_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "work_record_001.md"
            metadata = _metadata()
            markdown.write_text("# Record\n\n<script>alert(1)</script>\n", encoding="utf-8")
            rendered = render_work_record(markdown, metadata)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
            self.assertNotIn("<script>", rendered)

            markdown.write_text("# Record\n\n[危険](javascript:alert(1))\n", encoding="utf-8")
            with self.assertRaises(RenderedRendererError):
                render_work_record(markdown, metadata)

            markdown.write_text("# Record\n\n[外部](../private.md)\n", encoding="utf-8")
            with self.assertRaises(RenderedRendererError):
                render_work_record(markdown, metadata)

    def test_markdown_must_start_with_h1_and_metadata_must_match_basename(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "work_record_001.md"
            markdown.write_text("本文だけ\n", encoding="utf-8")
            with self.assertRaises(RenderedRendererError):
                render_work_record(markdown, _metadata())

            markdown.write_text("# Record\n", encoding="utf-8")
            with self.assertRaises(RenderedRendererError):
                render_work_record(
                    markdown,
                    {**_metadata(), "project_id": "other"},
                    expected_project_id="tech_article_nortification",
                )


def _metadata():
    return {
        "schema_version": 1,
        "title": "Record",
        "date": "2026-08-28",
        "project_id": "tech_article_nortification",
        "tags": [],
        "publish": True,
    }


if __name__ == "__main__":
    unittest.main()
