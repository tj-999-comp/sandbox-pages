import copy
import tempfile
import unittest
from pathlib import Path

from scripts.publish.content_safety import (
    ContentSafetyError,
    validate_css_file,
    validate_html_file,
    validate_source_html_tree,
)
from scripts.publish.source_registry import load_registry


ROOT = Path(__file__).resolve().parents[1]


class ContentSafetyTests(unittest.TestCase):
    def setUp(self):
        self.source = copy.deepcopy(load_registry(ROOT / "config" / "sources.json")["sources"][0])

    def test_current_work_record_html_and_css_are_accepted(self):
        document = validate_html_file(ROOT / "work-records", "work_record_023.html")
        self.assertEqual(document.css_paths, ("work_record.css",))

    def test_dangerous_elements_and_attributes_are_rejected(self):
        for fragment in (
            "<script>alert(1)</script>",
            "<iframe src='https://example.com'></iframe>",
            "<object data='x'></object>",
            "<embed src='x'>",
            "<form action='/x'></form>",
            "<base href='/x'>",
            "<p onclick='alert(1)'>x</p>",
            "<meta http-equiv='refresh' content='0;url=https://example.com'>",
        ):
            with self.subTest(fragment=fragment), self.assertRaises(ContentSafetyError):
                _validate_html_fragment(fragment)

    def test_url_policy_rejects_traversal_and_dangerous_schemes(self):
        for href in ("../README.md", "/outside", "//example.com/x", "javascript:alert(1)",
                     "data:text/html,alert(1)", "http://example.com"):
            with self.subTest(href=href), self.assertRaises(ContentSafetyError):
                _validate_html_fragment(f"<a href='{href}'>link</a>")
        _validate_html_fragment("<a href='https://github.com/tj-999-comp/sandbox-pages'>link</a>")
        _validate_html_fragment("<a href='#section'>link</a>")

    def test_missing_local_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(_document("<link rel='stylesheet' href='missing.css'>"), encoding="utf-8")
            with self.assertRaisesRegex(ContentSafetyError, "missing"):
                validate_html_file(root, "index.html")

    def test_source_html_tree_reuses_acceptance_file_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "md").mkdir()
            (root / "metadata").mkdir()
            (root / "md" / "work_record_001.md").write_text("# Record\n", encoding="utf-8")
            (root / "metadata" / "work_record_001.yml").write_text("metadata\n", encoding="utf-8")
            (root / "README.md").write_text("README\n", encoding="utf-8")
            (root / "design.md").write_text("Design\n", encoding="utf-8")
            (root / "work_record.css").write_text("body { color: black; }", encoding="utf-8")
            (root / "work_record_001.html").write_text(
                _document("<a href='md/work_record_001.md'>source</a>"), encoding="utf-8"
            )
            documents = validate_source_html_tree(root, self.source)
        self.assertEqual(documents[0].path, "work_record_001.html")

    def test_source_html_tree_requires_registered_support_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "md").mkdir()
            (root / "metadata").mkdir()
            (root / "md" / "work_record_001.md").write_text("# Record\n", encoding="utf-8")
            (root / "metadata" / "work_record_001.yml").write_text("metadata\n", encoding="utf-8")
            (root / "README.md").write_text("README\n", encoding="utf-8")
            (root / "work_record.css").write_text("body { color: black; }", encoding="utf-8")
            (root / "work_record_001.html").write_text(_document("record"), encoding="utf-8")
            with self.assertRaisesRegex(ContentSafetyError, "acceptance failed"):
                validate_source_html_tree(root, self.source)

    def test_css_import_external_url_and_dangerous_syntax_are_rejected(self):
        cases = (
            "@import url('https://example.com/x.css');",
            ".x { background: url('https://example.com/x.png'); }",
            ".x { background: url('../x.png'); }",
            ".x { color: expression(alert(1)); }",
            ".x { behavior: url(x.htc); }",
            ".x { background: url('image.png'; }",
            "@keyframes spin { from { color: red; } to { color: blue; } }",
        )
        for css in cases:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "style.css").write_text(css, encoding="utf-8")
                with self.subTest(css=css), self.assertRaises(ContentSafetyError):
                    validate_css_file(root, "style.css")

    def test_css_local_url_must_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "style.css").write_text(".x { background: url('image.png'); }", encoding="utf-8")
            with self.assertRaisesRegex(ContentSafetyError, "missing"):
                validate_css_file(root, "style.css")


def _validate_html_fragment(fragment: str) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "work_record.css").write_text("body { color: black; }", encoding="utf-8")
        (root / "index.html").write_text(_document(fragment), encoding="utf-8")
        validate_html_file(root, "index.html")


def _document(body: str) -> str:
    return (
        "<!doctype html><html lang='ja'><head><meta charset='utf-8'>"
        "<link rel='stylesheet' href='work_record.css'></head><body>"
        f"{body}</body></html>"
    )


if __name__ == "__main__":
    unittest.main()
