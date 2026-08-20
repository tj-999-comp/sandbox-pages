import copy
import tempfile
import unittest
from pathlib import Path

from scripts.publish.index_generator import (
    generate_indexes,
    load_current_manifests,
    render_global_index,
    render_project_index,
)
from scripts.publish.provenance import load_manifest, serialize_manifest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "index_generator"


class IndexGeneratorTests(unittest.TestCase):
    def test_project_and_global_indexes_match_golden_files(self):
        manifest = load_manifest(str(ROOT / "tests/fixtures/provenance/valid_manifest.json"))
        self.assertEqual(
            render_project_index(manifest),
            (FIXTURES / "project.html").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            render_global_index([manifest]),
            (FIXTURES / "global.html").read_text(encoding="utf-8"),
        )

    def test_metadata_is_escaped_and_only_records_are_listed(self):
        manifest = load_manifest(str(ROOT / "tests/fixtures/provenance/valid_manifest.json"))
        manifest = copy.deepcopy(manifest)
        manifest["records"][0]["metadata"]["title"] = '<script>alert("x")</script>'
        manifest["records"][0]["metadata"]["tags"] = ["<unsafe>"]
        rendered = render_project_index(manifest)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;unsafe&gt;", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("work_record.css", rendered)

    def test_sort_is_date_descending_then_record_number_descending(self):
        manifest = load_manifest(str(ROOT / "provenance/B_Stats_Site/initial.json"))
        rendered = render_project_index(manifest)
        positions = [rendered.index(f"work_record_{number:03d}") for number in (10, 9, 8, 7, 6)]
        self.assertEqual(positions, sorted(positions))

    def test_latest_manifest_wins_and_check_detects_stale_output(self):
        manifest = load_manifest(str(ROOT / "tests/fixtures/provenance/valid_manifest.json"))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            provenance = root / "provenance/B_Stats_Site"
            provenance.mkdir(parents=True)
            (provenance / "initial.json").write_text(serialize_manifest(manifest), encoding="utf-8")
            newer = copy.deepcopy(manifest)
            newer["publication_id"] = "pub-002"
            newer["accepted_at"] = "2026-08-21T01:00:00Z"
            (provenance / "current.json").write_text(serialize_manifest(newer), encoding="utf-8")
            loaded = load_current_manifests(root / "provenance")
            self.assertEqual(loaded[0]["publication_id"], "pub-002")
            with self.assertRaisesRegex(ValueError, "generated indexes are stale"):
                generate_indexes(root, check=True)
            generate_indexes(root)
            generate_indexes(root, check=True)


if __name__ == "__main__":
    unittest.main()
