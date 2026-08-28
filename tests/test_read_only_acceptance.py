import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.publish.read_only_acceptance import (
    ReadOnlyAcceptanceError,
    run_acceptance,
    resolve_source,
)
from scripts.publish.provenance import build_manifest, serialize_manifest


ROOT = Path(__file__).resolve().parents[1]


class ReadOnlyAcceptanceTests(unittest.TestCase):
    def test_unregistered_project_is_rejected(self):
        with self.assertRaisesRegex(ReadOnlyAcceptanceError, "not registered"):
            resolve_source(
                registry_path=ROOT / "config/sources.json",
                project_id="unregistered-project",
                source_commit_sha="a" * 40,
                target_basename="work_record_001",
            )

    def test_disabled_registered_source_is_resolved_as_disabled(self):
        source = resolve_source(
            registry_path=ROOT / "config/sources.json",
            project_id="tech_article_nortification",
            source_commit_sha="a" * 40,
            target_basename="work_record_001",
        )
        self.assertFalse(source["enabled"])
        self.assertEqual(source["destination_directory"], "projects/tech_article_nortification")

    def test_resolve_allows_registered_enabled_source_with_explicit_opt_in(self):
        source = resolve_source(
            registry_path=ROOT / "config/sources.json",
            project_id="B_Stats_Site",
            source_commit_sha="a" * 40,
            target_basename="work_record_001",
            allow_enabled=True,
        )
        self.assertEqual(source["source_repository"], "tj-999-comp/B_Stats_Site")
        self.assertTrue(source["enabled"])

    def test_enabled_source_requires_explicit_apply_mode_opt_in(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = json.loads(
                (ROOT / "config/sources.json").read_text(encoding="utf-8")
            )
            registry["sources"][0]["enabled"] = True
            registry_path = Path(temp_dir) / "sources.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with self.assertRaisesRegex(ReadOnlyAcceptanceError, "enabled:false"):
                resolve_source(
                    registry_path=registry_path,
                    project_id="B_Stats_Site",
                    source_commit_sha="a" * 40,
                    target_basename="work_record_001",
                )

            source = resolve_source(
                registry_path=registry_path,
                project_id="B_Stats_Site",
                source_commit_sha="a" * 40,
                target_basename="work_record_001",
                allow_enabled=True,
            )
            self.assertTrue(source["enabled"])

    def test_run_acceptance_outputs_selected_inventory_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            checkout = temp / "checkout"
            source_root = checkout / "work-records"
            (source_root / "md").mkdir(parents=True)
            (source_root / "metadata").mkdir()
            for name, content in {
                "README.md": "# Readme\n",
                "design.md": "# Design\n",
                "work_record.css": "body { color: #111; }\n",
                "md/work_record_001.md": "# Record\n",
                "metadata/work_record_001.yml": (
                    "schema_version: 1\n"
                    "title: Test record\n"
                    "date: 2026-08-20\n"
                    "project_id: B_Stats_Site\n"
                    "tags: []\n"
                    "publish: true\n"
                ),
                "work_record_001.html": (
                    "<!DOCTYPE html><html lang=\"ja\"><head>"
                    "<meta charset=\"utf-8\"><link rel=\"stylesheet\" href=\"work_record.css\">"
                    "<title>Test</title></head><body><h1>Test</h1></body></html>\n"
                ),
            }.items():
                path = source_root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            _run_git(checkout, "init", "--quiet")
            _run_git(checkout, "config", "user.email", "test@example.com")
            _run_git(checkout, "config", "user.name", "Test")
            _run_git(checkout, "add", ".")
            _run_git(checkout, "commit", "--quiet", "-m", "fixture")
            commit = _run_git(checkout, "rev-parse", "HEAD")
            _run_git(checkout, "branch", "-M", "main")

            provenance_dir = temp / "provenance" / "B_Stats_Site"
            provenance_dir.mkdir(parents=True)
            manifest = json.loads(
                (ROOT / "provenance/B_Stats_Site/initial.json").read_text(encoding="utf-8")
            )
            manifest["source"]["commit_sha"] = commit
            (provenance_dir / "initial.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            output_dir = temp / "output"
            result = run_acceptance(
                registry_path=ROOT / "config/sources.json",
                project_id="B_Stats_Site",
                source_commit_sha=commit,
                target_basename="work_record_001",
                source_checkout=checkout,
                branch_ref="refs/heads/main",
                provenance_root=temp / "provenance",
                output_dir=output_dir,
                allow_enabled=True,
            )

            self.assertTrue(result["dry_run"])
            self.assertFalse(result["apply"])
            self.assertEqual(result["target_basename"], "work_record_001")
            self.assertEqual(result["destination"]["directory"], "projects/B_Stats_Site")
            self.assertEqual(
                result["destination"]["public_base_path"],
                "/sandbox-pages/projects/B_Stats_Site/",
            )
            self.assertEqual(result["validators"]["content_safety"], "passed")
            self.assertEqual(
                {item["path"] for item in result["inventory"]},
                {
                    "README.md",
                    "design.md",
                    "work_record.css",
                    "md/work_record_001.md",
                    "metadata/work_record_001.yml",
                    "work_record_001.html",
                },
            )
            self.assertEqual(
                {item["path"] for item in result["target_inventory"]},
                {
                    "README.md",
                    "design.md",
                    "work_record.css",
                    "md/work_record_001.md",
                    "metadata/work_record_001.yml",
                    "work_record_001.html",
                },
            )
            saved = json.loads((output_dir / "acceptance.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, result)

    def test_source_commit_must_be_branch_ancestor(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir) / "checkout"
            checkout.mkdir()
            _run_git(checkout, "init", "--quiet")
            _run_git(checkout, "config", "user.email", "test@example.com")
            _run_git(checkout, "config", "user.name", "Test")
            (checkout / "file").write_text("one\n", encoding="utf-8")
            _run_git(checkout, "add", ".")
            _run_git(checkout, "commit", "--quiet", "-m", "one")
            first = _run_git(checkout, "rev-parse", "HEAD")
            (checkout / "file").write_text("two\n", encoding="utf-8")
            _run_git(checkout, "commit", "--quiet", "-am", "two")
            _run_git(checkout, "branch", "-M", "main")

            with self.assertRaises(ReadOnlyAcceptanceError):
                from scripts.publish.read_only_acceptance import _verify_fixed_commit

                _verify_fixed_commit(checkout, first, "refs/heads/missing")

    def test_a_rendered_validates_markdown_without_source_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            checkout = temp / "checkout"
            (checkout / "seed").parent.mkdir(parents=True)
            _run_git(checkout, "init", "--quiet")
            _run_git(checkout, "config", "user.email", "test@example.com")
            _run_git(checkout, "config", "user.name", "Test")
            (checkout / "seed").write_text("seed\n", encoding="utf-8")
            _run_git(checkout, "add", "seed")
            _run_git(checkout, "commit", "--quiet", "-m", "seed")
            previous = _run_git(checkout, "rev-parse", "HEAD")
            source_root = checkout / "work-records"
            (source_root / "md").mkdir(parents=True)
            (source_root / "metadata").mkdir()
            (source_root / "md/work_record_001.md").write_text(
                "# Source title\n\n## 概要\n\nRenderer input.\n", encoding="utf-8"
            )
            (source_root / "metadata/work_record_001.yml").write_text(
                "schema_version: 1\n"
                "title: Rendered record\n"
                "date: 2026-08-28\n"
                "project_id: tech_article_nortification\n"
                "tags: []\n"
                "publish: false\n",
                encoding="utf-8",
            )
            _run_git(checkout, "add", "work-records")
            _run_git(checkout, "commit", "--quiet", "-m", "record")
            commit = _run_git(checkout, "rev-parse", "HEAD")
            _run_git(checkout, "branch", "-M", "main")

            provenance_dir = temp / "provenance/tech_article_nortification"
            provenance_dir.mkdir(parents=True)
            manifest = build_manifest(
                publication_id="bootstrap-tech-article",
                project_id="tech_article_nortification",
                source_repository="tj-999-comp/tech_article_nortification",
                source_ref="refs/heads/main",
                source_commit_sha=previous,
                public_base_path="/sandbox-pages/projects/tech_article_nortification/",
                accepted_at="2026-08-20T00:00:00Z",
                operation="create",
                metadata_by_basename={},
                source_files=[],
                published_files=[],
                notify=False,
            )
            (provenance_dir / "initial.json").write_text(
                serialize_manifest(manifest), encoding="utf-8"
            )

            result = run_acceptance(
                registry_path=ROOT / "config/sources.json",
                project_id="tech_article_nortification",
                source_commit_sha=commit,
                target_basename="work_record_001",
                source_checkout=checkout,
                branch_ref="refs/heads/main",
                provenance_root=temp / "provenance",
                output_dir=temp / "output",
            )

        self.assertEqual(result["validators"]["renderer"], "passed")
        self.assertEqual(
            {item["path"] for item in result["target_inventory"]},
            {"md/work_record_001.md", "metadata/work_record_001.yml"},
        )


def _run_git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


if __name__ == "__main__":
    unittest.main()
