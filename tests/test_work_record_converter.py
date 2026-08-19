import unittest
from pathlib import Path

from scripts.dev.convert_work_records_to_html import render_document


ROOT = Path(__file__).resolve().parents[1]


class WorkRecordConverterTests(unittest.TestCase):
    def test_generated_record_has_no_upper_navigation_links(self):
        html = render_document(ROOT / "work-records" / "md" / "work_record_001.md")
        self.assertNotIn('<header class="topbar">', html)
        self.assertNotIn('class="wordmark"', html)
        self.assertNotIn('class="toplinks"', html)
        self.assertIn('<span><a href="md/work_record_001.md">Markdown原本</a></span>', html)


if __name__ == "__main__":
    unittest.main()
