from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.publish.sync_dry_run import SyncDryRunError, run_noop_dry_run


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))["sources"][0]


class SyncDryRunTests(unittest.TestCase):
    def test_existing_project_is_a_noop_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest_path, manifest = _write_bootstrap_manifest(Path(temp))
            before = manifest_path.read_bytes()
            source_root = Path(temp) / "source"
            source_tree = source_root / "work-records"
            published_root = Path(temp) / "published"
            _copy_tree(ROOT / "projects/B_Stats_Site", published_root)
            _copy_tree(ROOT / "projects/B_Stats_Site", source_tree, exclude={"index.html"})
            result = run_noop_dry_run(
                source_root=source_root,
                published_root=published_root,
                manifest_path=manifest_path,
                source=REGISTRY,
            )
            self.assertEqual(before, manifest_path.read_bytes())
        self.assertTrue(result.is_noop)
        self.assertEqual(result.source_file_count, len(manifest["published_files"]))
        self.assertEqual(result.published_file_count, len(manifest["published_files"]))

    def test_published_extra_file_stops_before_any_sync(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest_path, _ = _write_bootstrap_manifest(Path(temp))
            source_root = Path(temp) / "source"
            _copy_tree(
                ROOT / "projects/B_Stats_Site",
                source_root / "work-records",
                exclude={"index.html"},
            )
            published_root = Path(temp) / "published"
            _copy_tree(ROOT / "projects/B_Stats_Site", published_root)
            (published_root / "unexpected.txt").write_text("do not overwrite", encoding="utf-8")
            with self.assertRaisesRegex(SyncDryRunError, "published inventory.*extra=unexpected.txt"):
                run_noop_dry_run(
                    source_root=source_root,
                    published_root=published_root,
                    manifest_path=manifest_path,
                    source=REGISTRY,
                )

    def test_source_change_stops_before_published_comparison(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest_path, _ = _write_bootstrap_manifest(Path(temp))
            source_root = Path(temp) / "source"
            _copy_tree(
                ROOT / "projects/B_Stats_Site",
                source_root / "work-records",
                exclude={"index.html"},
            )
            (source_root / "work-records/README.md").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(SyncDryRunError, "source inventory.*changed=README.md"):
                run_noop_dry_run(
                    source_root=source_root,
                    published_root=ROOT / "projects/B_Stats_Site",
                    manifest_path=manifest_path,
                    source=REGISTRY,
                )


def _copy_tree(source: Path, destination: Path, exclude: set[str] | None = None) -> None:
    excluded = exclude or set()
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if relative.as_posix() in excluded:
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())


def _latest_manifest_path() -> Path:
    manifests = sorted((ROOT / "provenance/B_Stats_Site").glob("*.json"))
    return max(
        manifests,
        key=lambda path: (
            json.loads(path.read_text(encoding="utf-8"))["accepted_at"],
            json.loads(path.read_text(encoding="utf-8"))["publication_id"],
        ),
    )


def _write_bootstrap_manifest(root: Path) -> tuple[Path, dict]:
    manifest = json.loads(_latest_manifest_path().read_text(encoding="utf-8"))
    manifest.update(
        {
            "accepted_at": "2026-08-20T00:00:00Z",
            "notify": False,
            "operation": "create",
            "publication_id": "bootstrap-20260820-b-stats-site",
            "source_files": manifest["published_files"],
        }
    )
    path = root / "initial.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path, manifest
