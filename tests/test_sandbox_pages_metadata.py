import unittest
from pathlib import Path

from scripts.publish.metadata_schema import load_registered_metadata


ROOT = Path(__file__).resolve().parents[1]


class SandboxPagesMetadataTests(unittest.TestCase):
    def test_every_work_record_has_matching_public_metadata(self):
        markdown_paths = sorted((ROOT / "work-records" / "md").glob("work_record_*.md"))
        metadata_paths = sorted((ROOT / "work-records" / "metadata").glob("work_record_*.yml"))
        html_paths = sorted((ROOT / "work-records").glob("work_record_*.html"))

        self.assertEqual(
            {path.stem for path in markdown_paths},
            {path.stem for path in metadata_paths},
        )
        self.assertEqual(
            {path.stem for path in markdown_paths},
            {path.stem for path in html_paths},
        )

        for markdown_path in markdown_paths:
            with self.subTest(record=markdown_path.stem):
                lines = markdown_path.read_text(encoding="utf-8").splitlines()
                title = next(line for line in lines if line.startswith("# 作業記録")).split(": ", 1)[1]
                record_date = next(line for line in lines if line.startswith("作成日:")).split(":", 1)[1].strip()
                metadata = load_registered_metadata(
                    ROOT / "work-records" / "metadata" / f"{markdown_path.stem}.yml",
                    expected_basename=markdown_path.stem,
                )
                self.assertEqual(metadata["title"], title)
                self.assertEqual(metadata["date"], record_date)
                self.assertEqual(metadata["project_id"], "sandbox_pages")
                self.assertEqual(metadata["tags"], [])
                self.assertTrue(metadata["publish"])


if __name__ == "__main__":
    unittest.main()
