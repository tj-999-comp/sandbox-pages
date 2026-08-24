import copy
import tempfile
import unittest
from pathlib import Path

from scripts.publish.acceptance_files import (
    AcceptanceFileError,
    validate_source_tree,
)
from scripts.publish.source_registry import load_registry


ROOT = Path(__file__).resolve().parents[1]


class AcceptanceFileTests(unittest.TestCase):
    def setUp(self):
        self.source = copy.deepcopy(load_registry(ROOT / "config" / "sources.json")["sources"][0])

    def test_valid_source_returns_deterministic_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_valid_record(root, "work_record_001")
            for name in self.source["support_files"]:
                (root / name).write_text(name, encoding="utf-8")
            first = validate_source_tree(root, self.source)
            second = validate_source_tree(root, self.source)

        self.assertEqual(first, second)
        self.assertEqual(first.record_basenames, ("work_record_001",))
        self.assertEqual(
            [item.path for item in first.files],
            [
                "README.md",
                "design.md",
                "md/work_record_001.md",
                "metadata/work_record_001.yml",
                "work_record.css",
                "work_record_001.html",
            ],
        )
        self.assertTrue(all(len(item.sha256) == 64 for item in first.files))

    def test_missing_record_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_valid_record(root, "work_record_001")
            (root / "work_record_001.html").unlink()
            with self.assertRaisesRegex(AcceptanceFileError, "incomplete"):
                validate_source_tree(root, self.source)

    def test_unregistered_extra_and_numberless_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_valid_record(root, "work_record_001")
            (root / "phase_1_tasks.html").write_text("extra", encoding="utf-8")
            with self.assertRaisesRegex(AcceptanceFileError, "not registered"):
                validate_source_tree(root, self.source)

    def test_registered_ignored_files_are_excluded_from_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_valid_record(root, "work_record_001")
            for name in self.source["support_files"]:
                (root / name).write_text(name, encoding="utf-8")
            ignored = [
                "md/phase_1_tasks.md",
                "work_record_extra_01.html",
            ]
            self.source["ignored_files"] = ignored
            for path in ignored:
                ignored_path = root / path
                ignored_path.parent.mkdir(parents=True, exist_ok=True)
                ignored_path.write_text("ignored", encoding="utf-8")

            result = validate_source_tree(root, self.source)

        self.assertNotIn("md/phase_1_tasks.md", [item.path for item in result.files])
        self.assertNotIn("work_record_extra_01.html", [item.path for item in result.files])

    def test_unregistered_empty_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_valid_record(root, "work_record_001")
            for name in self.source["support_files"]:
                (root / name).write_text(name, encoding="utf-8")
            (root / "unexpected").mkdir()
            with self.assertRaisesRegex(AcceptanceFileError, "directory is not registered"):
                validate_source_tree(root, self.source)

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_valid_record(root, "work_record_001")
            for name in self.source["support_files"]:
                (root / name).write_text(name, encoding="utf-8")
            (root / "README.link").symlink_to(root / "README.md")
            with self.assertRaisesRegex(AcceptanceFileError, "symlink"):
                validate_source_tree(root, self.source)

    def test_file_and_total_limits_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_valid_record(root, "work_record_001")
            for name in self.source["support_files"]:
                (root / name).write_text(name, encoding="utf-8")
            limited = copy.deepcopy(self.source)
            limited["limits"]["max_file_size_bytes"] = 1
            with self.assertRaisesRegex(AcceptanceFileError, "file exceeds"):
                validate_source_tree(root, limited)
            limited = copy.deepcopy(self.source)
            limited["limits"]["max_total_size_bytes"] = 1
            with self.assertRaisesRegex(AcceptanceFileError, "total size"):
                validate_source_tree(root, limited)

    def test_a_rendered_does_not_require_source_html(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rendered = copy.deepcopy(self.source)
            rendered["html_mode"] = "a_rendered"
            _write_valid_record(root, "work_record_001", include_html=False)
            for name in rendered["support_files"]:
                (root / name).write_text(name, encoding="utf-8")
            result = validate_source_tree(root, rendered)
        self.assertEqual(result.record_basenames, ("work_record_001",))


def _write_valid_record(root: Path, basename: str, *, include_html: bool = True):
    (root / "md").mkdir(parents=True, exist_ok=True)
    (root / "metadata").mkdir(parents=True, exist_ok=True)
    (root / "md" / f"{basename}.md").write_text("# Record\n", encoding="utf-8")
    (root / "metadata" / f"{basename}.yml").write_text(
        "schema_version: 1\ntitle: Record\ndate: '2026-08-20'\n"
        "project_id: B_Stats_Site\ntags: []\npublish: true\n",
        encoding="utf-8",
    )
    if include_html:
        (root / f"{basename}.html").write_text("<html></html>\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
