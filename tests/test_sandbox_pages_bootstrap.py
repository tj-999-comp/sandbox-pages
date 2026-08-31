import hashlib
import unittest
from pathlib import Path

from scripts.publish.acceptance_files import AcceptedFile
from scripts.publish.provenance import inspect_drift, load_manifest
from scripts.publish.source_registry import load_registry


ROOT = Path(__file__).resolve().parents[1]


class SandboxPagesBootstrapTests(unittest.TestCase):
    def test_initial_bootstrap_manifest_matches_public_tree(self):
        manifest = load_manifest(ROOT / "provenance/sandbox_pages/initial.json")
        source = next(
            item
            for item in load_registry(ROOT / "config/sources.json")["sources"]
            if item["project_id"] == "sandbox_pages"
        )
        public_root = ROOT / "projects/sandbox_pages"
        current_files = []
        for path in sorted(public_root.rglob("*")):
            if path.is_file() and path.name != "index.html":
                current_files.append(
                    AcceptedFile(
                        path.relative_to(public_root).as_posix(),
                        path.stat().st_size,
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
                )

        self.assertEqual(manifest["operation"], "create")
        self.assertFalse(manifest["notify"])
        self.assertEqual(manifest["source"]["repository"], source["source_repository"])
        self.assertEqual(manifest["source"]["ref"], source["source_ref"])
        self.assertEqual(
            manifest["source"]["commit_sha"],
            "d6c6b29f10844e2a2e52a9b0660b71aba6e5cf2e",
        )
        self.assertEqual(len(manifest["source_files"]), 213)
        self.assertEqual(len(manifest["published_files"]), 143)
        self.assertEqual(len(manifest["records"]), 70)
        self.assertTrue(all(record["metadata"]["publish"] for record in manifest["records"]))
        self.assertFalse(any(item["path"].startswith("metadata/") for item in manifest["published_files"]))
        repair_manifest = load_manifest(
            ROOT / "provenance/sandbox_pages/repair-20260831-work-record-005-links.json"
        )
        self.assertEqual(repair_manifest["operation"], "update")
        self.assertEqual(
            repair_manifest["source"]["commit_sha"],
            "63e8124d5017b0de204abdb270072d3efb1c984a",
        )
        self.assertEqual(len(repair_manifest["source_files"]), 216)
        self.assertEqual(len(repair_manifest["published_files"]), 143)
        self.assertEqual(len(repair_manifest["records"]), 70)
        self.assertFalse(repair_manifest["notify"])
        self.assertTrue(inspect_drift(repair_manifest, current_files).clean)
        self.assertIn("公開中の作業記録 70件", (public_root / "index.html").read_text(encoding="utf-8"))
        self.assertIn("sandbox_pages", (ROOT / "projects/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
