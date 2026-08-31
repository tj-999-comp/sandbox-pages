import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.publish.source_registry import (
    SourceRegistryError,
    load_registry,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]


class SourceRegistryTests(unittest.TestCase):
    def test_repository_registry_loads_with_expected_sources(self):
        registry = load_registry(ROOT / "config" / "sources.json")
        self.assertEqual(registry["schema_version"], 1)
        self.assertEqual(
            [source["project_id"] for source in registry["sources"]],
            ["B_Stats_Site", "NBA_Draft_DB", "tech_article_nortification"],
        )
        source = registry["sources"][0]
        self.assertTrue(source["enabled"])
        self.assertEqual(source["html_mode"], "a_rendered")
        self.assertEqual(source["generator_id"], "a-rendered-work-record-v1")
        self.assertEqual(source["support_files"], [])
        self.assertIn("work_record_031.html", source["ignored_files"])
        nba_source = registry["sources"][1]
        self.assertEqual(nba_source["source_repository"], "tj-999-comp/NBA_Draft_DB")
        self.assertEqual(nba_source["source_ref"], "refs/heads/main")
        self.assertEqual(nba_source["source_directory"], "work-records")
        self.assertEqual(nba_source["metadata_directory"], "work-records/metadata")
        self.assertEqual(nba_source["destination_directory"], "projects/NBA_Draft_DB")
        self.assertEqual(nba_source["public_base_path"], "/sandbox-pages/projects/NBA_Draft_DB/")
        self.assertEqual(nba_source["html_mode"], "a_rendered")
        self.assertEqual(nba_source["generator_id"], "a-rendered-work-record-v1")
        self.assertTrue(nba_source["enabled"])
        self.assertEqual(nba_source["support_files"], [])
        self.assertEqual(nba_source["ignored_files"], [])

    def test_tech_article_source_has_the_fixed_issue_contract(self):
        registry = load_registry(ROOT / "config" / "sources.json")
        source = next(
            item for item in registry["sources"]
            if item["project_id"] == "tech_article_nortification"
        )

        self.assertEqual(source["source_repository"], "tj-999-comp/tech_article_nortification")
        self.assertEqual(source["source_ref"], "refs/heads/main")
        self.assertEqual(source["source_directory"], "work-records")
        self.assertEqual(source["metadata_directory"], "work-records/metadata")
        self.assertEqual(source["destination_directory"], "projects/tech_article_nortification")
        self.assertEqual(source["html_mode"], "a_rendered")
        self.assertTrue(source["enabled"])

    def test_loading_is_deterministic(self):
        first = load_registry(ROOT / "config" / "sources.json")
        second = load_registry(ROOT / "config" / "sources.json")
        self.assertEqual(first, second)

        reordered = _registry()
        additional = copy.deepcopy(reordered["sources"][0])
        additional["project_id"] = "Another_Project"
        additional["destination_directory"] = "projects/Another_Project"
        additional["public_base_path"] = "/sandbox-pages/projects/Another_Project/"
        reordered["sources"] = [additional, reordered["sources"][0]]
        normalized = validate_registry(reordered)
        self.assertEqual(
            [source["project_id"] for source in normalized["sources"]],
            ["Another_Project", "B_Stats_Site"],
        )
        self.assertEqual(
            normalized["sources"][0]["support_files"],
            [],
        )
        self.assertEqual(
            normalized["sources"][0]["ignored_files"],
            load_registry(ROOT / "config" / "sources.json")["sources"][0]["ignored_files"],
        )

    def test_a_rendered_source_may_have_no_support_files(self):
        registry = _registry()
        source = registry["sources"][1]
        normalized = validate_registry(registry)
        self.assertEqual(source["html_mode"], "a_rendered")
        self.assertEqual(normalized["sources"][1]["support_files"], [])

    def test_duplicate_project_ids_are_rejected(self):
        registry = _registry()
        registry["sources"].append(copy.deepcopy(registry["sources"][0]))
        with self.assertRaisesRegex(SourceRegistryError, "duplicate project_id"):
            validate_registry(registry)

    def test_unknown_fields_are_rejected(self):
        registry = _registry()
        registry["sources"][0]["unexpected"] = True
        with self.assertRaisesRegex(SourceRegistryError, "unknown field"):
            validate_registry(registry)

    def test_support_and_ignored_file_overlap_is_rejected(self):
        registry = _registry()
        registry["sources"][0]["support_files"] = ["README.md"]
        registry["sources"][0]["ignored_files"].append("README.md")
        with self.assertRaisesRegex(SourceRegistryError, "also registered"):
            validate_registry(registry)

    def test_invalid_paths_are_rejected(self):
        for field, value in (
            ("source_directory", "/work-records"),
            ("metadata_directory", "work-records/../private"),
            ("source_directory", "work-records/../work-records"),
            ("destination_directory", "projects/../outside"),
            ("source_directory", r"work-records\\md"),
            ("public_base_path", "/sandbox-pages/projects/../outside/"),
        ):
            registry = _registry()
            registry["sources"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(SourceRegistryError):
                validate_registry(registry)

    def test_unknown_mode_and_generator_are_rejected(self):
        for field in ("html_mode", "generator_id"):
            registry = _registry()
            registry["sources"][0][field] = "unknown"
            with self.subTest(field=field), self.assertRaises(SourceRegistryError):
                validate_registry(registry)

    def test_html_mode_and_generator_must_match(self):
        registry = _registry()
        registry["sources"][0]["html_mode"] = "a_rendered"
        registry["sources"][0]["generator_id"] = "b-stats-work-record-v1"
        with self.assertRaisesRegex(SourceRegistryError, "does not match"):
            validate_registry(registry)

        registry = _registry()
        registry["sources"][1]["generator_id"] = "b-stats-work-record-v1"
        with self.assertRaisesRegex(SourceRegistryError, "does not match"):
            validate_registry(registry)

        for field, value in (("html_mode", {}), ("generator_id", [])):
            registry = _registry()
            registry["sources"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(
                SourceRegistryError
            ):
                validate_registry(registry)

    def test_missing_and_wrong_schema_are_rejected(self):
        registry = _registry()
        del registry["sources"][0]["limits"]
        with self.assertRaises(SourceRegistryError):
            validate_registry(registry)
        registry = _registry()
        registry["schema_version"] = 2
        with self.assertRaises(SourceRegistryError):
            validate_registry(registry)

    def test_capacity_limits_are_validated(self):
        registry = _registry()
        registry["sources"][0]["limits"]["max_files"] = 0
        with self.assertRaises(SourceRegistryError):
            validate_registry(registry)
        registry = _registry()
        registry["sources"][0]["limits"]["max_total_size_bytes"] = 1
        with self.assertRaises(SourceRegistryError):
            validate_registry(registry)

    def test_load_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(SourceRegistryError):
                load_registry(path)

    def test_fixture_rejects_non_string_generator_id(self):
        fixture = (
            ROOT
            / "tests"
            / "fixtures"
            / "source_registry"
            / "invalid_generator_type.json"
        )
        with self.assertRaises(SourceRegistryError):
            load_registry(fixture)


def _registry():
    with (ROOT / "config" / "sources.json").open(encoding="utf-8") as stream:
        return json.load(stream)


if __name__ == "__main__":
    unittest.main()
