import tempfile
import unittest
from pathlib import Path

from scripts.publish.rendered_renderer import RenderedRendererError, render_work_record
from scripts.publish.record_navigation import build_record_navigation


class RenderedRendererTests(unittest.TestCase):
    def test_golden_fixture_is_reproducible(self):
        markdown = Path(__file__).parent / "fixtures/rendered_renderer/work_record_001.md"
        expected = (
            Path(__file__).parent / "fixtures/rendered_renderer/golden.html"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            render_work_record(markdown, _metadata(title="Golden record", tags=["golden"])),
            expected,
        )

    def test_render_is_deterministic_and_uses_normalized_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "work_record_001.md"
            markdown.write_text(
                "# Markdown title\n"
                "\n"
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
        self.assertIn("作業記録 001 ・ 2026-08-28", first)
        self.assertIn('<section class="record-section">', first)
        self.assertIn('<p class="section-label">01　概要</p>', first)
        self.assertIn("<h2>概要</h2>", first)
        self.assertIn('<div class="section-content">', first)
        self.assertIn("<strong>強調</strong>", first)
        self.assertIn('<a href="https://example.com/a?b=1">参照</a>', first)
        self.assertNotIn('<ul class="tag-list">', first)
        self.assertNotIn("2000-01-01", first)
        self.assertNotIn("作成日:", first)

    def test_render_can_include_record_navigation(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "work_record_001.md"
            markdown.write_text("# Record\n\n## 概要\n\n本文。\n", encoding="utf-8")
            metadata = _metadata()
            navigation = build_record_navigation(
                [
                    {
                        "project_id": "tech_article_nortification",
                        "records": [
                            {"basename": "work_record_001", "metadata": metadata},
                            {"basename": "work_record_002", "metadata": {**metadata, "title": "Older", "date": "2026-08-27"}},
                        ],
                    }
                ],
                project_id="tech_article_nortification",
                basename="work_record_001",
            )

            rendered = render_work_record(markdown, metadata, navigation=navigation)

        self.assertIn('class="record-navigation"', rendered)
        self.assertIn('href="index.html">このproject', rendered)
        self.assertIn('href="../index.html">全project', rendered)
        self.assertIn('href="work_record_002.html"', rendered)
        self.assertNotIn('href="work_record_001.html"', rendered)

    def test_local_record_markdown_links_target_published_html(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "work_record_001.md"
            markdown.write_text(
                "# Record\n\n## 関連\n\n"
                "[同じ階層](work_record_002.md) [md階層](md/work_record_003.md)\n",
                encoding="utf-8",
            )

            rendered = render_work_record(markdown, _metadata())

        self.assertIn('href="work_record_002.html"', rendered)
        self.assertIn('href="work_record_003.html"', rendered)
        self.assertIn('Markdown原本: <code>md/work_record_001.md</code>', rendered)
        self.assertNotIn('href="md/work_record_001.md"', rendered)

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


def _metadata(*, title="Record", tags=None):
    return {
        "schema_version": 1,
        "title": title,
        "date": "2026-08-28",
        "project_id": "tech_article_nortification",
        "tags": [] if tags is None else tags,
        "publish": True,
    }


if __name__ == "__main__":
    unittest.main()
