import unittest

from scripts.publish.record_navigation import (
    build_record_navigation,
    decorate_record_html,
    render_record_navigation,
    update_record_navigation,
)


class RecordNavigationTests(unittest.TestCase):
    def test_navigation_uses_project_sort_and_never_links_to_current_record(self):
        manifests = [
            {
                "project_id": "project_a",
                "records": [
                    {"basename": "work_record_001", "metadata": _metadata("First", "2026-08-20")},
                    {"basename": "work_record_002", "metadata": _metadata("Second", "2026-08-20")},
                    {"basename": "work_record_003", "metadata": _metadata("Third", "2026-08-19")},
                ],
            },
            {
                "project_id": "project_b",
                "records": [
                    {"basename": "work_record_001", "metadata": _metadata("Other", "2026-08-21")},
                ],
            },
        ]

        navigation = build_record_navigation(
            manifests,
            project_id="project_a",
            basename="work_record_001",
        )
        rendered = render_record_navigation(navigation)

        self.assertEqual(navigation.position, 2)
        self.assertEqual(navigation.total, 3)
        self.assertEqual(navigation.previous.basename, "work_record_002")
        self.assertEqual(navigation.next.basename, "work_record_003")
        self.assertIn('href="index.html">このproject', rendered)
        self.assertIn('href="../index.html">全project', rendered)
        self.assertIn('href="work_record_002.html"', rendered)
        self.assertIn('href="work_record_003.html"', rendered)
        self.assertNotIn('href="work_record_001.html"', rendered)
        self.assertNotIn("project_b", rendered)

    def test_source_html_decoration_is_idempotent_and_precedes_main(self):
        navigation = build_record_navigation(
            [
                {
                    "project_id": "project_a",
                    "records": [
                        {"basename": "work_record_001", "metadata": _metadata("Record", "2026-08-20")}
                    ],
                }
            ],
            project_id="project_a",
            basename="work_record_001",
        )
        document = "<!doctype html>\n<html><head></head><body>\n  <div class=\"shell\">\n    <main>body</main>\n  </div>\n</body></html>"

        decorated = decorate_record_html(document, navigation)

        self.assertLess(decorated.index('class="record-navigation"'), decorated.index("<main>"))
        self.assertEqual(decorated, decorate_record_html(decorated, navigation))

        updated_navigation = build_record_navigation(
            [
                {
                    "project_id": "project_a",
                    "records": [
                        {"basename": "work_record_001", "metadata": _metadata("Record", "2026-08-20")},
                        {"basename": "work_record_002", "metadata": _metadata("Other", "2026-08-21")},
                    ],
                }
            ],
            project_id="project_a",
            basename="work_record_001",
        )
        updated = update_record_navigation(decorated, updated_navigation)
        self.assertEqual(updated.count('class="record-navigation"'), 1)
        self.assertIn('href="work_record_002.html"', updated)
        self.assertNotIn('href="work_record_001.html"', updated)


def _metadata(title, record_date):
    return {
        "schema_version": 1,
        "title": title,
        "date": record_date,
        "project_id": "project_a",
        "tags": [],
        "publish": True,
    }


if __name__ == "__main__":
    unittest.main()
