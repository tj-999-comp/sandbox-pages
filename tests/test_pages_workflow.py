import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PagesWorkflowTests(unittest.TestCase):
    def test_pages_workflow_pins_actions_and_fixed_sha_guards(self):
        workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
        for reference in (
            "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803",
            "actions/upload-pages-artifact@7b1f4a764d45c48632c6b24a0339c27f5614fb0b",
            "actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
        ):
            self.assertIn(reference, workflow)
        self.assertEqual(workflow.count("git ls-remote --exit-code origin refs/heads/main"), 2)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("SLACK_WEBHOOK_URL", workflow)

    def test_validation_workflow_is_read_only(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("python3 -m scripts.publish.index_generator --check", workflow)


if __name__ == "__main__":
    unittest.main()
