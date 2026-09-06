import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts.publish.index_generator import load_current_manifests
from scripts.publish.record_navigation import build_record_navigation


ROOT = Path(__file__).resolve().parents[1]


class NavigationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_navigation = False
        self.navigation_depth = 0
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "nav" and attributes.get("class") == "record-navigation":
            self.in_navigation = True
            self.navigation_depth = 1
        elif self.in_navigation:
            self.navigation_depth += 1
        if self.in_navigation and tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])

    def handle_endtag(self, tag):
        if self.in_navigation:
            self.navigation_depth -= 1
            if self.navigation_depth == 0:
                self.in_navigation = False


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])


class PublishedNavigationTests(unittest.TestCase):
    def test_project_and_global_indexes_match_published_records(self):
        manifests = load_current_manifests(ROOT / "provenance")
        expected_global = {
            f'./{manifest["project_id"]}/{record["basename"]}.html'
            for manifest in manifests
            for record in manifest["records"]
        }
        global_html = (ROOT / "projects" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(
            {
                href
                for href in _hrefs(global_html)
                if href.startswith("./") and "/work_record_" in href
            },
            expected_global,
        )
        for manifest in manifests:
            project_id = manifest["project_id"]
            html = (ROOT / "projects" / project_id / "index.html").read_text(encoding="utf-8")
            expected_project = {f'./{record["basename"]}.html' for record in manifest["records"]}
            self.assertEqual(
                {href for href in _hrefs(html) if href.startswith("./work_record_")},
                expected_project,
            )

    def test_every_published_detail_has_resolvable_navigation_without_self_link(self):
        manifests = load_current_manifests(ROOT / "provenance")
        for manifest in manifests:
            project_id = manifest["project_id"]
            project_root = ROOT / "projects" / project_id
            for record in manifest["records"]:
                basename = record["basename"]
                page = project_root / f"{basename}.html"
                self.assertTrue(page.is_file(), page)
                parser = NavigationParser()
                parser.feed(page.read_text(encoding="utf-8"))
                self.assertTrue(parser.links, page)
                self.assertNotIn(f"{basename}.html", parser.links, page)
                for href in parser.links:
                    self.assertFalse(href.startswith("/"), (page, href))
                    target = (page.parent / href.split("#", 1)[0]).resolve()
                    self.assertTrue(target.is_file(), (page, href, target))

    def test_navigation_matches_project_order_for_both_html_modes(self):
        manifests = load_current_manifests(ROOT / "provenance")
        for manifest in manifests:
            project_id = manifest["project_id"]
            project_root = ROOT / "projects" / project_id
            for record in manifest["records"]:
                basename = record["basename"]
                expected = build_record_navigation(
                    manifests,
                    project_id=project_id,
                    basename=basename,
                )
                parser = NavigationParser()
                parser.feed((project_root / f"{basename}.html").read_text(encoding="utf-8"))
                expected_hrefs = {"index.html", "../index.html"}
                if expected.previous:
                    expected_hrefs.add(expected.previous.href)
                if expected.next:
                    expected_hrefs.add(expected.next.href)
                self.assertEqual(set(parser.links), expected_hrefs)


if __name__ == "__main__":
    unittest.main()


def _hrefs(document):
    parser = LinkParser()
    parser.feed(document)
    return parser.links
