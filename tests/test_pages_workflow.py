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
        self.assertIn("should_deploy:", workflow)
        self.assertIn("github.event_name != 'workflow_call' || inputs.should_deploy == true", workflow)
        self.assertIn("github.event_name == 'workflow_call' && inputs.should_deploy != true", workflow)
        self.assertIn("Complete no-op without deploying", workflow)
        self.assertIn("No new publication; skipping Pages deploy", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("SLACK_WEBHOOK_URL", workflow)

    def test_validation_workflow_is_read_only(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("python3 -m scripts.publish.index_generator --check", workflow)

    def test_source_acceptance_commits_and_deploys_only_validated_changes(self):
        workflow = (ROOT / ".github/workflows/accept-source.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("\n  pull_request:", workflow)
        self.assertNotIn("\n  repository_dispatch:", workflow)
        self.assertNotIn("\n  schedule:", workflow)
        for input_name in ("project_id", "source_commit_sha", "target_basename"):
            self.assertIn(f"      {input_name}:", workflow)
        self.assertIn("permissions: {}", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("contents: write", workflow)
        before_notification = workflow.split("\n  notify:\n", 1)[0]
        self.assertNotIn("secrets.", before_notification)
        self.assertIn('"$GITHUB_REF" != "refs/heads/main"', workflow)
        self.assertIn("token: ${{ github.token }}", workflow)
        self.assertIn("actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093", workflow)
        self.assertIn("python3 -m scripts.publish.apply_engine", workflow)
        self.assertIn('PYTHONDONTWRITEBYTECODE: "1"', workflow)
        self.assertIn("--allow-enabled", workflow)
        self.assertIn("source is disabled; validation completed without apply", workflow)
        self.assertIn("--operation auto", workflow)
        self.assertIn("git push origin HEAD:refs/heads/main", workflow)
        self.assertIn("for retry in 0 1", workflow)
        self.assertIn("main advanced during apply; rechecking and retrying once", workflow)
        self.assertIn("uses: ./.github/workflows/deploy-pages.yml", workflow)
        self.assertIn("commit_sha: ${{ needs.apply.outputs.commit_sha }}", workflow)
        self.assertIn("should_deploy: ${{ needs.apply.outputs.no_op != 'true' }}", workflow)
        deploy_block = workflow.split("\n  deploy:\n", 1)[1].split("\n  notify:\n", 1)[0]
        self.assertNotIn("\n    if:", deploy_block)
        self.assertIn("--notify", workflow)
        self.assertIn("operation: ${{ steps.apply.outputs.operation }}", workflow)
        self.assertIn("publication_id: ${{ steps.apply.outputs.publication_id }}", workflow)
        self.assertIn("notify: ${{ steps.apply.outputs.notify }}", workflow)
        self.assertIn("needs: [apply, deploy]", workflow)
        self.assertIn("needs.apply.outputs.operation == 'create'", workflow)
        self.assertIn("needs.apply.outputs.no_op != 'true'", workflow)
        self.assertIn("needs.apply.outputs.notify == 'true'", workflow)
        self.assertIn("SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}", workflow)
        self.assertIn("python3 -m scripts.publish.slack_notification verify-url", workflow)
        self.assertIn("python3 -m scripts.publish.slack_notification send", workflow)
        self.assertIn("group: pages-production-main", workflow)
        self.assertNotIn("rsync --delete", workflow)
        acceptance = (ROOT / "scripts/publish/read_only_acceptance.py").read_text(encoding="utf-8")
        self.assertIn('"merge-base", "--is-ancestor"', acceptance)
        self.assertIn("dry_run", acceptance)
        self.assertIn("allow_enabled: bool = False", acceptance)

    def test_apply_cli_can_infer_create_or_update_from_provenance(self):
        apply_engine = (ROOT / "scripts/publish/apply_engine.py").read_text(encoding="utf-8")
        self.assertIn('choices=("auto", "create", "update")', apply_engine)
        self.assertIn("def infer_operation", apply_engine)


if __name__ == "__main__":
    unittest.main()
