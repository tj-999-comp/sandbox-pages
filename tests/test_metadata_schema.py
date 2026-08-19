import tempfile
import unittest
from pathlib import Path

from scripts.publish.metadata_schema import (
    MetadataSchemaError,
    is_publish_candidate,
    load_metadata,
    load_registered_metadata,
    validate_record_filenames,
    validate_metadata,
)

ROOT = Path(__file__).resolve().parents[1]


class MetadataSchemaTests(unittest.TestCase):
    def test_valid_metadata_is_normalized_deterministically(self):
        data = _metadata()
        data["title"] = "  A title  "
        data["tags"] = ["z", "a"]
        self.assertEqual(validate_metadata(data, expected_basename="work_record_001",
                                           registered_project_ids={"B_Stats_Site"}),
                         {"schema_version": 1, "title": "A title", "date": "2026-08-20",
                          "project_id": "B_Stats_Site", "tags": ["a", "z"], "publish": True})

    def test_registered_metadata_file_loads_from_yaml(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "work_record_002.yml"
            path.write_text("schema_version: 1\ntitle: Second record\ndate: '2026-08-19'\n"
                            "project_id: B_Stats_Site\ntags:\n  - publish\n  - validation\n"
                            "publish: true\n", encoding="utf-8")
            normalized = load_registered_metadata(path, registry_path=ROOT / "config" / "sources.json")
        self.assertEqual(normalized["date"], "2026-08-19")
        self.assertTrue(is_publish_candidate(normalized))

    def test_invalid_basename_is_rejected(self):
        for basename in ("work_record_000", "work_record_1000", "work_record_01", "Work_record_001"):
            with self.subTest(basename=basename), self.assertRaises(MetadataSchemaError):
                validate_metadata(_metadata(), expected_basename=basename)

    def test_record_filenames_require_one_shared_case_sensitive_basename(self):
        self.assertEqual(validate_record_filenames(("work_record_001.md", "work_record_001.yml",
                                                    "work_record_001.html")), "work_record_001")
        for filenames in (("work_record_001.md", "work_record_002.yml"),
                          ("work_record_001.md", "work_Record_001.yml"),
                          ("work_record_001.md", "work_record_001.json")):
            with self.subTest(filenames=filenames), self.assertRaises(MetadataSchemaError):
                validate_record_filenames(filenames)

    def test_missing_and_unknown_fields_are_rejected(self):
        for field in ("title", "date", "project_id", "tags", "publish"):
            data = _metadata()
            del data[field]
            with self.subTest(field=field), self.assertRaises(MetadataSchemaError):
                validate_metadata(data, expected_basename="work_record_001")
        data = _metadata()
        data["unknown"] = "not allowed"
        with self.assertRaises(MetadataSchemaError):
            validate_metadata(data, expected_basename="work_record_001")

    def test_field_types_and_project_registration_are_rejected(self):
        for field, value in (("schema_version", "1"), ("date", "2026-02-30"),
                             ("tags", ["ok", 1]), ("publish", "true")):
            data = _metadata()
            data[field] = value
            with self.subTest(field=field), self.assertRaises(MetadataSchemaError):
                validate_metadata(data, expected_basename="work_record_001",
                                  registered_project_ids={"B_Stats_Site"})
        data = _metadata()
        data["project_id"] = "Unregistered"
        with self.assertRaises(MetadataSchemaError):
            validate_metadata(data, expected_basename="work_record_001",
                              registered_project_ids={"B_Stats_Site"})

    def test_publish_false_and_missing_metadata_are_not_candidates(self):
        data = _metadata()
        data["publish"] = False
        self.assertFalse(is_publish_candidate(validate_metadata(data, expected_basename="work_record_001")))
        self.assertFalse(is_publish_candidate(None))
        fixture = ROOT / "tests" / "fixtures" / "metadata" / "work_record_003.yml"
        self.assertFalse(is_publish_candidate(load_metadata(fixture, registered_project_ids={"B_Stats_Site"})))

    def test_load_metadata_rejects_invalid_fixture(self):
        fixture = ROOT / "tests" / "fixtures" / "metadata" / "invalid_unknown_field.yml"
        with self.assertRaises(MetadataSchemaError):
            load_metadata(fixture, registered_project_ids={"B_Stats_Site"})


def _metadata():
    return {"schema_version": 1, "title": "Record", "date": "2026-08-20",
            "project_id": "B_Stats_Site", "tags": ["publish"], "publish": True}


if __name__ == "__main__":
    unittest.main()
