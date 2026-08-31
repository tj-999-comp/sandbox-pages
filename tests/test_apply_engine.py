import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.publish.apply_engine import (
    ApplyConflictError,
    ApplyEngineError,
    apply_verified_payload,
    apply_with_bounded_retry,
    infer_operation,
)
from scripts.publish.provenance import build_manifest, serialize_manifest
from scripts.publish.read_only_acceptance import run_acceptance
from scripts.publish.withdraw_engine import apply_withdrawal, plan_withdrawal


ROOT = Path(__file__).resolve().parents[1]


class ApplyEngineTests(unittest.TestCase):
    def test_create_result_and_manifest_mark_notification_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            result = fixture.apply(acceptance, "pub-011", "create", notify=True)

            self.assertTrue(result.notify)
            manifest = json.loads(
                (fixture.repo / "provenance/B_Stats_Site/pub-011.json").read_text(encoding="utf-8")
            )
            self.assertTrue(manifest["notify"])

    def test_operation_inference_uses_previous_provenance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")

            self.assertEqual(
                infer_operation(
                    acceptance_path=acceptance,
                    provenance_root=fixture.repo / "provenance",
                ),
                "create",
            )
            fixture.apply(acceptance, "pub-011", "create")
            _git(fixture.repo, "add", ".")
            _git(fixture.repo, "commit", "--quiet", "-m", "apply record")

            self.assertEqual(
                infer_operation(
                    acceptance_path=acceptance,
                    provenance_root=fixture.repo / "provenance",
                ),
                "update",
            )

    def test_create_rechecks_payload_and_updates_only_allowed_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            result = fixture.apply(acceptance, "pub-011", "create")

            self.assertFalse(result.no_op)
            self.assertIn("projects/B_Stats_Site/md/work_record_011.md", result.changed_paths)
            self.assertIn("projects/B_Stats_Site/work_record_011.html", result.changed_paths)
            self.assertIn("provenance/B_Stats_Site/pub-011.json", result.changed_paths)
            self.assertIn("projects/index.html", result.changed_paths)
            self.assertFalse((fixture.repo / "projects/B_Stats_Site/metadata").exists())
            manifest = json.loads(
                (fixture.repo / "provenance/B_Stats_Site/pub-011.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["operation"], "create")
            self.assertEqual(manifest["source"]["commit_sha"], fixture.source_head)
            self.assertIn(
                "work_record_011",
                {record["basename"] for record in manifest["records"]},
            )

    def test_metadata_tampering_is_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            data = json.loads(acceptance.read_text(encoding="utf-8"))
            data["metadata"]["title"] = "tampered"
            acceptance.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ApplyEngineError, "metadata no longer matches"):
                fixture.apply(acceptance, "pub-011", "create")
            self.assertFalse((fixture.repo / "provenance/B_Stats_Site/pub-011.json").exists())
            self.assertFalse(
                (fixture.repo / "projects/B_Stats_Site/md/work_record_011.md").exists()
            )

    def test_same_repository_source_checkout_must_be_isolated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            with self.assertRaisesRegex(ApplyEngineError, "source checkout must be isolated"):
                apply_verified_payload(
                    acceptance_path=acceptance,
                    source_checkout=fixture.repo,
                    repository_root=fixture.repo,
                    registry_path=fixture.repo / "config/sources.json",
                    provenance_root=fixture.repo / "provenance",
                    publication_id="pub-isolated",
                    accepted_at="2026-08-20T02:00:00Z",
                    operation="create",
                    expected_main_sha=_git(fixture.repo, "rev-parse", "HEAD"),
                    source_branch_ref="refs/heads/main",
                )

    def test_source_change_after_acceptance_is_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            source_file = fixture.checkout / "work-records/md/work_record_011.md"
            source_file.write_text("# Changed after acceptance\n", encoding="utf-8")
            with self.assertRaisesRegex(ApplyEngineError, "inventory digest"):
                fixture.apply(acceptance, "pub-source-changed", "create")
            self.assertFalse(
                (fixture.repo / "provenance/B_Stats_Site/pub-source-changed.json").exists()
            )

    def test_target_inventory_cannot_add_an_unauthorized_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            data = json.loads(acceptance.read_text(encoding="utf-8"))
            unauthorized = dict(data["target_inventory"][0])
            unauthorized["path"] = "not-allowed.txt"
            data["target_inventory"].append(unauthorized)
            acceptance.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ApplyEngineError, "outside the registered target set"):
                fixture.apply(acceptance, "pub-unauthorized", "create")
            self.assertFalse(
                (fixture.repo / "provenance/B_Stats_Site/pub-unauthorized.json").exists()
            )

    def test_manifest_drift_is_rejected_before_apply(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            public_file = fixture.repo / "projects/B_Stats_Site/work_record_001.html"
            public_file.write_text("changed\n", encoding="utf-8")
            _git(fixture.repo, "add", ".")
            _git(fixture.repo, "commit", "-m", "simulate drift")

            with self.assertRaisesRegex(ApplyEngineError, "published files differ"):
                fixture.apply(acceptance, "pub-011", "create")
            self.assertFalse((fixture.repo / "provenance/B_Stats_Site/pub-011.json").exists())

    def test_extra_public_file_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            extra = fixture.repo / "projects/B_Stats_Site/unexpected.txt"
            extra.write_text("keep me\n", encoding="utf-8")
            _git(fixture.repo, "add", ".")
            _git(fixture.repo, "commit", "-m", "simulate extra file")

            with self.assertRaisesRegex(ApplyEngineError, "published files differ"):
                fixture.apply(acceptance, "pub-011", "create")
            self.assertEqual(extra.read_text(encoding="utf-8"), "keep me\n")

    def test_payload_cannot_redirect_to_another_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            data = json.loads(acceptance.read_text(encoding="utf-8"))
            data["destination"]["directory"] = "projects/Other"
            acceptance.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ApplyEngineError, "destination directory"):
                fixture.apply(acceptance, "pub-011", "create")

    def test_apply_rejects_non_contract_commit_and_basename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            data = json.loads(acceptance.read_text(encoding="utf-8"))

            data["source"]["commit_sha"] = "a" * 64
            acceptance.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ApplyEngineError, "full lowercase SHA"):
                fixture.apply(acceptance, "pub-011", "create")

            data["source"]["commit_sha"] = fixture.source_head
            data["target_basename"] = "../work_record_011"
            acceptance.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ApplyEngineError, "target_basename"):
                fixture.apply(acceptance, "pub-012", "create")

    def test_source_commit_mismatch_is_rejected_before_apply(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            acceptance = fixture.create_acceptance("work_record_011")
            data = json.loads(acceptance.read_text(encoding="utf-8"))
            data["source"]["commit_sha"] = "a" * 40
            acceptance.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ApplyEngineError, "source checkout does not match"):
                fixture.apply(acceptance, "pub-mismatched-source", "create")
            self.assertFalse(
                (fixture.repo / "provenance/B_Stats_Site/pub-mismatched-source.json").exists()
            )

    def test_second_application_with_same_content_is_a_noop(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            first_acceptance = fixture.create_acceptance("work_record_011")
            fixture.apply(first_acceptance, "pub-011", "create")
            _git(fixture.repo, "add", ".")
            _git(fixture.repo, "commit", "--quiet", "-m", "apply record")
            main_before = _git(fixture.repo, "rev-parse", "HEAD")
            second_acceptance = fixture.create_acceptance("work_record_011")
            result = fixture.apply(second_acceptance, "pub-012", "update")

            self.assertTrue(result.no_op)
            self.assertEqual(result.changed_paths, ())
            self.assertEqual(_git(fixture.repo, "rev-parse", "HEAD"), main_before)
            self.assertFalse((fixture.repo / "provenance/B_Stats_Site/pub-012.json").exists())

    def test_retry_is_bounded_after_a_second_head_change(self):
        heads = iter(("a" * 40, "b" * 40, "c" * 40))
        with self.assertRaises(ApplyConflictError):
            apply_with_bounded_retry(
                initial_main_sha="a" * 40,
                current_main_sha=lambda: next(heads),
                attempt=lambda _sha, _retry: (_ for _ in ()).throw(
                    ApplyConflictError("attempt saw a conflict")
                ),
                max_retries=1,
            )

    def test_a_rendered_apply_generates_public_html_from_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _RenderedFixture(Path(temp_dir))
            acceptance = fixture.create_acceptance()
            result = fixture.apply(acceptance)

            self.assertFalse(result.no_op)
            generated = fixture.repo / "projects/tech_article_nortification/work_record_001.html"
            self.assertTrue(generated.is_file())
            rendered = generated.read_text(encoding="utf-8")
            self.assertIn("Rendered record", rendered)
            self.assertIn('<section class="record-section">', rendered)
            self.assertIn("<h2>概要</h2>", rendered)
            self.assertNotIn('class="record-content"', rendered)
            self.assertNotIn("<script>", rendered)
            self.assertFalse(
                (fixture.repo / "projects/tech_article_nortification/metadata").exists()
            )
            manifest = json.loads(
                (fixture.repo / "provenance/tech_article_nortification/pub-001.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                {item["path"] for item in manifest["source_files"]},
                {"md/work_record_001.md", "metadata/work_record_001.yml"},
            )
            self.assertIn("work_record_001.html", {item["path"] for item in manifest["published_files"]})

    def test_withdraw_plan_is_read_only_and_names_exact_target_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            head = _git(fixture.repo, "rev-parse", "HEAD")
            result = plan_withdrawal(
                repository_root=fixture.repo,
                registry_path=fixture.repo / "config/sources.json",
                provenance_root=fixture.repo / "provenance",
                project_id="B_Stats_Site",
                target_basename="work_record_001",
                withdrawal_id="withdraw-preview",
                expected_main_sha=head,
            )

            self.assertEqual(
                set(result["removed_paths"]),
                {
                    "projects/B_Stats_Site/md/work_record_001.md",
                    "projects/B_Stats_Site/work_record_001.html",
                },
            )
            self.assertEqual(_git(fixture.repo, "rev-parse", "HEAD"), head)
            self.assertEqual(_git(fixture.repo, "status", "--porcelain"), "")

    def test_withdraw_apply_removes_target_and_writes_a_non_notifying_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            result = apply_withdrawal(
                repository_root=fixture.repo,
                registry_path=fixture.repo / "config/sources.json",
                provenance_root=fixture.repo / "provenance",
                project_id="B_Stats_Site",
                target_basename="work_record_001",
                withdrawal_id="withdraw-001",
                expected_main_sha=_git(fixture.repo, "rev-parse", "HEAD"),
                expected_publication_id="bootstrap-20260820-b-stats-site",
                confirmation="WITHDRAW",
                accepted_at="2026-08-28T03:00:00Z",
            )

            self.assertFalse((fixture.repo / "projects/B_Stats_Site/work_record_001.html").exists())
            self.assertFalse((fixture.repo / "projects/B_Stats_Site/md/work_record_001.md").exists())
            self.assertTrue((fixture.repo / "projects/B_Stats_Site/work_record_002.html").exists())
            manifest = json.loads(
                (fixture.repo / "provenance/B_Stats_Site/withdraw-001.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["operation"], "withdraw")
            self.assertFalse(manifest["notify"])
            self.assertNotIn("work_record_001", {record["basename"] for record in manifest["records"]})
            self.assertIn("projects/B_Stats_Site/work_record_001.html", result["changed_paths"])
            self.assertIn("projects/B_Stats_Site/md/work_record_001.md", result["changed_paths"])

    def test_withdraw_rejects_wrong_confirmation_and_repeated_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            kwargs = {
                "repository_root": fixture.repo,
                "registry_path": fixture.repo / "config/sources.json",
                "provenance_root": fixture.repo / "provenance",
                "project_id": "B_Stats_Site",
                "target_basename": "work_record_001",
                "withdrawal_id": "withdraw-001",
                "expected_main_sha": _git(fixture.repo, "rev-parse", "HEAD"),
                "expected_publication_id": "bootstrap-20260820-b-stats-site",
            }
            with self.assertRaisesRegex(ValueError, "confirmation"):
                apply_withdrawal(**kwargs, confirmation="DELETE")
            apply_withdrawal(**kwargs, confirmation="WITHDRAW", accepted_at="2026-08-28T03:00:00Z")
            _git(fixture.repo, "add", ".")
            _git(fixture.repo, "commit", "--quiet", "-m", "withdraw record")
            with self.assertRaisesRegex(ValueError, "target does not exist"):
                plan_withdrawal(
                    repository_root=fixture.repo,
                    registry_path=fixture.repo / "config/sources.json",
                    provenance_root=fixture.repo / "provenance",
                    project_id="B_Stats_Site",
                    target_basename="work_record_001",
                    withdrawal_id="withdraw-preview-2",
                )

    def test_withdraw_rejects_public_drift_without_deleting_anything(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _Fixture(Path(temp_dir))
            extra = fixture.repo / "projects/B_Stats_Site/unexpected.txt"
            extra.write_text("keep me\n", encoding="utf-8")
            _git(fixture.repo, "add", "projects/B_Stats_Site/unexpected.txt")
            _git(fixture.repo, "commit", "--quiet", "-m", "simulate drift")
            with self.assertRaisesRegex(ValueError, "published files differ"):
                plan_withdrawal(
                    repository_root=fixture.repo,
                    registry_path=fixture.repo / "config/sources.json",
                    provenance_root=fixture.repo / "provenance",
                    project_id="B_Stats_Site",
                    target_basename="work_record_001",
                    withdrawal_id="withdraw-preview",
                )
            self.assertTrue(extra.exists())
            self.assertTrue((fixture.repo / "projects/B_Stats_Site/work_record_001.html").exists())


class _Fixture:
    def __init__(self, root: Path):
        self.root = root
        self.repo = root / "repo"
        self.checkout = root / "source"
        self._prepare_repository()
        self._prepare_source()

    def _prepare_repository(self):
        (self.repo / "config").mkdir(parents=True)
        (self.repo / "projects/B_Stats_Site").mkdir(parents=True)
        (self.repo / "projects").mkdir(exist_ok=True)
        (self.repo / "provenance/B_Stats_Site").mkdir(parents=True)
        shutil.copy2(ROOT / "config/sources.json", self.repo / "config/sources.json")
        shutil.copy2(ROOT / "projects/index.html", self.repo / "projects/index.html")
        shutil.copy2(
            ROOT / "projects/progress-index.css", self.repo / "projects/progress-index.css"
        )
        for path in (ROOT / "projects/B_Stats_Site").iterdir():
            if path.name != "index.html":
                destination = self.repo / "projects/B_Stats_Site" / path.name
                if path.is_dir():
                    shutil.copytree(path, destination)
                else:
                    shutil.copy2(path, destination)
        shutil.copy2(
            ROOT / "projects/B_Stats_Site/index.html",
            self.repo / "projects/B_Stats_Site/index.html",
        )
        manifest = json.loads(
            _latest_manifest_path().read_text(encoding="utf-8")
        )
        manifest.update(
            {
                "accepted_at": "2026-08-20T00:00:00Z",
                "notify": False,
                "publication_id": "bootstrap-20260820-b-stats-site",
                "source_files": manifest["published_files"],
            }
        )
        (self.repo / "provenance/B_Stats_Site/initial.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        from scripts.publish.index_generator import generate_indexes

        generate_indexes(self.repo)
        _git(self.repo, "init", "--quiet")
        _git(self.repo, "config", "user.email", "test@example.com")
        _git(self.repo, "config", "user.name", "Test")

    def _prepare_source(self):
        manifest = json.loads(
            (self.repo / "provenance/B_Stats_Site/initial.json").read_text(encoding="utf-8")
        )
        source_root = self.checkout / "work-records"
        for item in manifest["published_files"]:
            if item["path"].startswith("md/") and not item["path"].split("/", 1)[1].startswith("work_record_"):
                continue
            source_path = self.repo / "projects/B_Stats_Site" / item["path"]
            target = source_root / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target)
        for record in manifest["records"]:
            metadata = record["metadata"]
            target = source_root / "metadata" / f"{record['basename']}.yml"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "\n".join(
                    (
                        "schema_version: 1",
                        f"title: {json.dumps(metadata['title'], ensure_ascii=False)}",
                        f"date: {metadata['date']}",
                        f"project_id: {metadata['project_id']}",
                        "tags: []",
                        f"publish: {'true' if metadata['publish'] else 'false'}",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
        for html_file in source_root.glob("work_record_*.html"):
            html_file.write_text(
                "<!doctype html><html lang=\"ja\"><head><title>Record</title></head>"
                "<body><h1>Record</h1></body></html>\n",
                encoding="utf-8",
            )
        _git(self.checkout, "init", "--quiet")
        _git(self.checkout, "config", "user.email", "test@example.com")
        _git(self.checkout, "config", "user.name", "Test")
        _git(self.checkout, "add", ".")
        _git(self.checkout, "commit", "--quiet", "-m", "baseline")
        _git(self.checkout, "branch", "-M", "main")
        self.source_baseline = _git(self.checkout, "rev-parse", "HEAD")
        manifest["source"]["commit_sha"] = self.source_baseline
        (self.repo / "provenance/B_Stats_Site/initial.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "--quiet", "-m", "fixture baseline")

        source_root.mkdir(parents=True, exist_ok=True)
        (source_root / "md/work_record_011.md").write_text("# New record\n", encoding="utf-8")
        (source_root / "metadata/work_record_011.yml").write_text(
            "schema_version: 1\n"
            "title: New record\n"
            "date: 2026-08-20\n"
            "project_id: B_Stats_Site\n"
            "tags: []\n"
            "publish: true\n",
            encoding="utf-8",
        )
        (source_root / "work_record_011.html").write_text(
            "<!doctype html><html lang=\"ja\"><head><title>New</title></head>"
            "<body><h1>New record</h1></body></html>\n",
            encoding="utf-8",
        )
        _git(self.checkout, "add", ".")
        _git(self.checkout, "commit", "--quiet", "-m", "new record")
        self.source_head = _git(self.checkout, "rev-parse", "HEAD")

    def create_acceptance(self, basename: str) -> Path:
        output = self.root / f"acceptance-{basename}"
        run_acceptance(
            registry_path=self.repo / "config/sources.json",
            project_id="B_Stats_Site",
            source_commit_sha=self.source_head,
            target_basename=basename,
            source_checkout=self.checkout,
            branch_ref="refs/heads/main",
            provenance_root=self.repo / "provenance",
            output_dir=output,
            allow_enabled=True,
        )
        return output / "acceptance.json"

    def apply(self, acceptance: Path, publication_id: str, operation: str, *, notify: bool = False):
        return apply_verified_payload(
            acceptance_path=acceptance,
            source_checkout=self.checkout,
            repository_root=self.repo,
            registry_path=self.repo / "config/sources.json",
            provenance_root=self.repo / "provenance",
            publication_id=publication_id,
            accepted_at="2026-08-20T02:00:00Z",
            operation=operation,
            expected_main_sha=_git(self.repo, "rev-parse", "HEAD"),
            source_branch_ref="refs/heads/main",
            notify=notify,
        )


class _RenderedFixture:
    def __init__(self, root: Path):
        self.root = root
        self.repo = root / "repo"
        self.checkout = root / "source"
        self._prepare_repository()
        self._prepare_source()

    def _prepare_repository(self):
        (self.repo / "config").mkdir(parents=True)
        (self.repo / "projects/tech_article_nortification").mkdir(parents=True)
        (self.repo / "provenance/tech_article_nortification").mkdir(parents=True)
        registry = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))
        for source in registry["sources"]:
            if source["project_id"] == "tech_article_nortification":
                source["enabled"] = True
        (self.repo / "config/sources.json").write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        shutil.copy2(ROOT / "projects/progress-index.css", self.repo / "projects/progress-index.css")
        manifest = build_manifest(
            publication_id="bootstrap-tech-article",
            project_id="tech_article_nortification",
            source_repository="tj-999-comp/tech_article_nortification",
            source_ref="refs/heads/main",
            source_commit_sha="a" * 40,
            public_base_path="/sandbox-pages/projects/tech_article_nortification/",
            accepted_at="2026-08-20T00:00:00Z",
            operation="create",
            metadata_by_basename={},
            source_files=[],
            published_files=[],
            notify=False,
        )
        (self.repo / "provenance/tech_article_nortification/initial.json").write_text(
            serialize_manifest(manifest), encoding="utf-8"
        )
        from scripts.publish.index_generator import generate_indexes

        generate_indexes(self.repo)
        _git(self.repo, "init", "--quiet")
        _git(self.repo, "config", "user.email", "test@example.com")
        _git(self.repo, "config", "user.name", "Test")
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "--quiet", "-m", "baseline")

    def _prepare_source(self):
        source_root = self.checkout / "work-records"
        source_root.mkdir(parents=True)
        _git(self.checkout, "init", "--quiet")
        _git(self.checkout, "config", "user.email", "test@example.com")
        _git(self.checkout, "config", "user.name", "Test")
        (self.checkout / "seed").write_text("seed\n", encoding="utf-8")
        _git(self.checkout, "add", "seed")
        _git(self.checkout, "commit", "--quiet", "-m", "seed")
        self.previous_source_head = _git(self.checkout, "rev-parse", "HEAD")
        (source_root / "md").mkdir()
        (source_root / "metadata").mkdir()
        (source_root / "md/work_record_001.md").write_text(
            "# Source title\n\n## 概要\n\nRenderer content.\n", encoding="utf-8"
        )
        (source_root / "metadata/work_record_001.yml").write_text(
            "schema_version: 1\n"
            "title: Rendered record\n"
            "date: 2026-08-28\n"
            "project_id: tech_article_nortification\n"
            "tags: []\n"
            "publish: true\n",
            encoding="utf-8",
        )
        _git(self.checkout, "add", "work-records")
        _git(self.checkout, "commit", "--quiet", "-m", "record")
        self.source_head = _git(self.checkout, "rev-parse", "HEAD")
        _git(self.checkout, "branch", "-M", "main")
        manifest_path = self.repo / "provenance/tech_article_nortification/initial.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["source"]["commit_sha"] = self.previous_source_head
        manifest_path.write_text(serialize_manifest(manifest), encoding="utf-8")
        _git(self.repo, "add", "provenance/tech_article_nortification/initial.json")
        _git(self.repo, "commit", "--quiet", "-m", "pin source")

    def create_acceptance(self):
        output = self.root / "acceptance"
        run_acceptance(
            registry_path=self.repo / "config/sources.json",
            project_id="tech_article_nortification",
            source_commit_sha=self.source_head,
            target_basename="work_record_001",
            source_checkout=self.checkout,
            branch_ref="refs/heads/main",
            provenance_root=self.repo / "provenance",
            output_dir=output,
            allow_enabled=True,
        )
        return output / "acceptance.json"

    def apply(self, acceptance: Path):
        return apply_verified_payload(
            acceptance_path=acceptance,
            source_checkout=self.checkout,
            repository_root=self.repo,
            registry_path=self.repo / "config/sources.json",
            provenance_root=self.repo / "provenance",
            publication_id="pub-001",
            accepted_at="2026-08-28T00:00:00Z",
            operation="create",
            expected_main_sha=_git(self.repo, "rev-parse", "HEAD"),
            source_branch_ref="refs/heads/main",
        )


def _git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _latest_manifest_path() -> Path:
    manifests = sorted((ROOT / "provenance/B_Stats_Site").glob("*.json"))
    return max(
        manifests,
        key=lambda path: (
            json.loads(path.read_text(encoding="utf-8"))["accepted_at"],
            json.loads(path.read_text(encoding="utf-8"))["publication_id"],
        ),
    )


if __name__ == "__main__":
    unittest.main()
