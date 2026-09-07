import hashlib
import json
import unittest
from pathlib import Path

from scripts.publish.provenance import inspect_drift, load_manifest
from scripts.publish.source_registry import load_registry


ROOT = Path(__file__).resolve().parents[1]


class PublishedProvenanceIntegrityTests(unittest.TestCase):
    def test_registered_projects_match_their_latest_provenance(self):
        registry = load_registry(ROOT / "config/sources.json")

        for source in registry["sources"]:
            project_id = source["project_id"]
            provenance_directory = ROOT / "provenance" / project_id
            manifest_paths = sorted(provenance_directory.glob("*.json"))
            self.assertTrue(manifest_paths, f"no provenance manifest for {project_id}")

            manifests = [load_manifest(path) for path in manifest_paths]
            latest = max(
                manifests,
                key=lambda manifest: (manifest["accepted_at"], manifest["publication_id"]),
            )
            destination = ROOT / source["destination_directory"]
            current_files = []
            for path in sorted(destination.rglob("*")):
                if not path.is_file() or path.name == "index.html":
                    continue
                content = path.read_bytes()
                current_files.append(
                    {
                        "path": path.relative_to(destination).as_posix(),
                        "size_bytes": len(content),
                        "sha256": hashlib.sha256(content).hexdigest(),
                    }
                )

            drift = inspect_drift(latest, current_files)
            self.assertTrue(
                drift.clean,
                f"{project_id} provenance drift: "
                + json.dumps(
                    {
                        "missing": drift.missing,
                        "extra": drift.extra,
                        "changed": drift.changed,
                    },
                    ensure_ascii=False,
                ),
            )


if __name__ == "__main__":
    unittest.main()
