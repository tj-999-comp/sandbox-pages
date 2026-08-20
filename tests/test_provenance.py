import copy
import json
import unittest
from pathlib import Path

from scripts.publish.provenance import (
    ProvenanceDriftError,
    ProvenanceError,
    assert_no_drift,
    build_manifest,
    inspect_drift,
    load_manifest,
    serialize_manifest,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


class ProvenanceTests(unittest.TestCase):
    def test_manifest_is_normalized_and_serialized_deterministically(self):
        manifest = build_manifest(
            publication_id="pub-001",
            project_id="B_Stats_Site",
            source_repository="tj-999-comp/B_Stats_Site",
            source_ref="refs/heads/main",
            source_commit_sha="A" * 40,
            public_base_path="/sandbox-pages/projects/B_Stats_Site/",
            accepted_at="2026-08-20T10:00:00+09:00",
            operation="create",
            metadata_by_basename={"work_record_001": _metadata()},
            source_files=[
                _file("metadata/work_record_001.yml", "1"),
                _file("work_record_001.html", "2"),
                _file("md/work_record_001.md", "3"),
                _file("work_record.css", "4"),
            ],
            published_files=[_file("work_record_001.html", "2"), _file("md/work_record_001.md", "3"), _file("work_record.css", "4")],
            notify=False,
        )
        self.assertEqual(manifest["accepted_at"], "2026-08-20T01:00:00Z")
        self.assertEqual([item["path"] for item in manifest["source_files"]], [
            "md/work_record_001.md", "metadata/work_record_001.yml", "work_record.css", "work_record_001.html"
        ])
        self.assertEqual(serialize_manifest(manifest), serialize_manifest(validate_manifest(json.loads(serialize_manifest(manifest)))))

    def test_unknown_schema_and_unknown_fields_are_rejected(self):
        manifest = _manifest()
        manifest["schema_version"] = 2
        with self.assertRaises(ProvenanceError):
            validate_manifest(manifest)

    def test_json_fixtures_cover_valid_and_unknown_schema_manifests(self):
        fixture = ROOT / "tests" / "fixtures" / "provenance" / "valid_manifest.json"
        loaded = load_manifest(fixture)
        self.assertEqual(loaded["publication_id"], "pub-001")
        invalid = ROOT / "tests" / "fixtures" / "provenance" / "invalid_unknown_schema.json"
        with self.assertRaises(ProvenanceError):
            load_manifest(invalid)
        manifest = _manifest()
        manifest["unexpected"] = True
        with self.assertRaises(ProvenanceError):
            validate_manifest(manifest)

    def test_metadata_digest_and_public_url_are_verified(self):
        manifest = _manifest()
        manifest["records"][0]["metadata"]["title"] = "changed"
        with self.assertRaisesRegex(ProvenanceError, "metadata digest"):
            validate_manifest(manifest)
        manifest = _manifest()
        manifest["records"][0]["public_url"] = "/outside.html"
        with self.assertRaisesRegex(ProvenanceError, "public_url"):
            validate_manifest(manifest)

    def test_drift_report_detects_missing_extra_and_changed_files(self):
        manifest = _manifest()
        with (ROOT / "tests" / "fixtures" / "provenance" / "drift_current_files.json").open(encoding="utf-8") as stream:
            fixture_files = json.load(stream)
        report = inspect_drift(
            manifest,
            fixture_files,
        )
        self.assertEqual(report.missing, ())
        self.assertEqual(report.extra, ("unexpected.txt",))
        self.assertEqual(report.changed, ("work_record_001.html",))
        with self.assertRaises(ProvenanceDriftError):
            assert_no_drift(manifest, [_file("work_record_001.html", "changed")])

    def test_clean_drift_check_passes(self):
        manifest = _manifest()
        files = [
            _file("work_record_001.html", "html"),
            _file("work_record.css", "css"),
        ]
        self.assertTrue(inspect_drift(manifest, files).clean)
        assert_no_drift(manifest, files)

    def test_a_rendered_manifest_can_track_generated_public_html_separately(self):
        source_files = [_file("md/work_record_001.md", "markdown")]
        published_files = [_file("work_record_001.html", "rendered html")]
        manifest = build_manifest(
            publication_id="pub-rendered",
            project_id="B_Stats_Site",
            source_repository="tj-999-comp/B_Stats_Site",
            source_ref="refs/heads/main",
            source_commit_sha="b" * 40,
            public_base_path="/sandbox-pages/projects/B_Stats_Site/",
            accepted_at="2026-08-20T01:00:00Z",
            operation="create",
            metadata_by_basename={"work_record_001": _metadata()},
            source_files=source_files,
            published_files=published_files,
            notify=False,
        )
        self.assertEqual(manifest["published_files"][0]["path"], "work_record_001.html")


def _file(path: str, value: str) -> dict[str, object]:
    import hashlib

    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return {"path": path, "size_bytes": len(value.encode("utf-8")), "sha256": digest}


def _metadata() -> dict[str, object]:
    return {
        "schema_version": 1,
        "title": "Record",
        "date": "2026-08-20",
        "project_id": "B_Stats_Site",
        "tags": ["publish"],
        "publish": True,
    }


def _manifest() -> dict:
    metadata = _metadata()
    source_files = [_file("work_record_001.html", "html"), _file("work_record.css", "css")]
    return build_manifest(
        publication_id="pub-001",
        project_id="B_Stats_Site",
        source_repository="tj-999-comp/B_Stats_Site",
        source_ref="refs/heads/main",
        source_commit_sha="a" * 40,
        public_base_path="/sandbox-pages/projects/B_Stats_Site/",
        accepted_at="2026-08-20T01:00:00Z",
        operation="create",
        metadata_by_basename={"work_record_001": metadata},
        source_files=source_files,
        published_files=source_files,
        notify=False,
    )


if __name__ == "__main__":
    unittest.main()
