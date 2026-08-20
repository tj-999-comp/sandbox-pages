import json
import tempfile
import unittest
from pathlib import Path

from scripts.publish.sync_dry_run import SyncDryRunError, run_noop_dry_run


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))["sources"][0]


class SyncDryRunTests(unittest.TestCase):
    def test_existing_project_is_a_noop_without_writes(self):
        before = (ROOT / "provenance/B_Stats_Site/initial.json").read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            source_root = Path(temp) / "source"
            source_tree = source_root / "work-records"
            published_root = Path(temp) / "published"
            _copy_tree(ROOT / "projects/B_Stats_Site", published_root)
            _copy_tree(ROOT / "projects/B_Stats_Site", source_tree)
            result = run_noop_dry_run(
                source_root=source_root,
                published_root=published_root,
                manifest_path=ROOT / "provenance/B_Stats_Site/initial.json",
                source=REGISTRY,
            )
        self.assertTrue(result.is_noop)
        self.assertEqual(result.source_file_count, 25)
        self.assertEqual(result.published_file_count, 25)
        self.assertEqual(before, (ROOT / "provenance/B_Stats_Site/initial.json").read_bytes())

    def test_published_extra_file_stops_before_any_sync(self):
        with tempfile.TemporaryDirectory() as temp:
            source_root = Path(temp) / "source"
            _copy_tree(ROOT / "projects/B_Stats_Site", source_root / "work-records")
            published_root = Path(temp) / "published"
            _copy_tree(ROOT / "projects/B_Stats_Site", published_root)
            (published_root / "unexpected.txt").write_text("do not overwrite", encoding="utf-8")
            with self.assertRaisesRegex(SyncDryRunError, "published inventory.*extra=unexpected.txt"):
                run_noop_dry_run(
                    source_root=source_root,
                    published_root=published_root,
                    manifest_path=ROOT / "provenance/B_Stats_Site/initial.json",
                    source=REGISTRY,
                )

    def test_source_change_stops_before_published_comparison(self):
        with tempfile.TemporaryDirectory() as temp:
            source_root = Path(temp) / "source"
            _copy_tree(ROOT / "projects/B_Stats_Site", source_root / "work-records")
            (source_root / "work-records/README.md").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(SyncDryRunError, "source inventory.*changed=README.md"):
                run_noop_dry_run(
                    source_root=source_root,
                    published_root=ROOT / "projects/B_Stats_Site",
                    manifest_path=ROOT / "provenance/B_Stats_Site/initial.json",
                    source=REGISTRY,
                )


def _copy_tree(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
