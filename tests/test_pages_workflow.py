import unittest
from pathlib import Path

from scripts.publish.source_registry import load_registry


ROOT = Path(__file__).resolve().parents[1]


class PagesWorkflowTests(unittest.TestCase):
    def test_same_repository_source_uses_an_isolated_fixed_checkout(self):
        source = next(
            item
            for item in load_registry(ROOT / "config/sources.json")["sources"]
            if item["project_id"] == "sandbox_pages"
        )
        workflow = (ROOT / ".github/workflows/accept-source.yml").read_text(encoding="utf-8")
        self.assertEqual(source["source_repository"], "tj-999-comp/sandbox-pages")
        self.assertEqual(source["source_ref"], "refs/heads/main")
        self.assertIn("path: _source", workflow)
        self.assertIn('mv _source "$RUNNER_TEMP/source"', workflow)
        self.assertIn(
            "source checkout must be isolated from Repository A worktree",
            (ROOT / "scripts/publish/apply_engine.py").read_text(encoding="utf-8"),
        )

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
        self.assertNotIn("no_op:", workflow)
        workflow_call = workflow.split("\n  workflow_call:\n", 1)[1].split("\n    outputs:\n", 1)[0]
        self.assertIn("required: true", workflow_call)
        self.assertNotIn("concurrency:", workflow)
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
        self.assertIn("name: Verify isolated source checkout", workflow)
        self.assertEqual(workflow.count("name: Verify isolated source checkout"), 2)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("source checkout contains persisted credentials", workflow)
        self.assertIn("actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093", workflow)
        self.assertIn("name: Bind acceptance payload to dispatch inputs", workflow)
        self.assertIn(".project_id == $project_id", workflow)
        self.assertIn(".source.commit_sha == $source_commit_sha", workflow)
        self.assertIn(".target_basename == $target_basename", workflow)
        self.assertIn("python3 -m scripts.publish.apply_engine", workflow)
        self.assertIn('PYTHONDONTWRITEBYTECODE: "1"', workflow)
        self.assertIn("--allow-enabled", workflow)
        self.assertIn("source is disabled; validation completed without apply", workflow)
        self.assertIn("--operation auto", workflow)
        self.assertIn("git push origin HEAD:refs/heads/main", workflow)
        self.assertIn("for retry in 0 1", workflow)
        self.assertIn("main advanced during apply; rechecking and retrying once", workflow)
        self.assertIn("uses: ./.github/workflows/deploy-pages.yml", workflow)
        self.assertIn("if: ${{ needs.apply.result == 'success' && needs.apply.outputs.no_op != 'true' }}", workflow)
        self.assertIn("commit_sha: ${{ needs.apply.outputs.commit_sha }}", workflow)
        deploy_block = workflow.split("\n  deploy:\n", 1)[1].split("\n  notify:\n", 1)[0]
        self.assertIn("\n    if:", deploy_block)
        self.assertIn("--notify", workflow)
        self.assertIn("operation: ${{ steps.apply.outputs.operation }}", workflow)
        self.assertIn("publication_id: ${{ steps.apply.outputs.publication_id }}", workflow)
        self.assertIn("notify: ${{ steps.apply.outputs.notify }}", workflow)
        self.assertIn("needs: [apply, deploy]", workflow)
        self.assertIn("needs.apply.outputs.operation == 'create'", workflow)
        self.assertIn("needs.apply.outputs.no_op != 'true'", workflow)
        self.assertIn("needs.apply.outputs.notify == 'true'", workflow)
        self.assertIn("SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}", workflow)
        self.assertIn("name: Checkout Repository A", workflow)
        notify_block = workflow.split("\n  notify:\n", 1)[1]
        self.assertIn("ref: ${{ needs.apply.outputs.commit_sha }}", notify_block)
        self.assertIn("name: Resolve published record", notify_block)
        self.assertIn('manifest=\"provenance/$PROJECT_ID/$PUBLICATION_ID.json\"', notify_block)
        self.assertIn("SITE_URL: ${{ needs.deploy.outputs.page_url }}", notify_block)
        self.assertIn("slack_notification resolve-url", notify_block)
        self.assertIn("record_json", notify_block)
        self.assertIn('--title \"$TITLE\"', notify_block)
        self.assertNotIn("PUBLIC_URL: ${{ needs.deploy.outputs.page_url }}", notify_block)
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

    def test_withdrawal_workflow_requires_preview_sha_and_has_no_slack_path(self):
        workflow = (ROOT / ".github/workflows/withdraw.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        for input_name in (
            "project_id",
            "target_basename",
            "mode",
            "expected_main_sha",
            "expected_publication_id",
            "confirmation",
        ):
            self.assertIn(f"      {input_name}:", workflow)
        self.assertIn("permissions: {}", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("--expected-main-sha", workflow)
        self.assertIn("--expected-publication-id", workflow)
        self.assertIn('test "$CONFIRMATION" = "WITHDRAW"', workflow)
        self.assertIn("python3 -m scripts.publish.withdraw_engine", workflow)
        self.assertIn("git push origin HEAD:refs/heads/main", workflow)
        self.assertIn("uses: ./.github/workflows/deploy-pages.yml", workflow)
        self.assertIn("group: pages-production-main", workflow)
        self.assertNotIn("SLACK", workflow)
        self.assertNotIn("rsync --delete", workflow)

    def test_notification_retry_is_fixed_commit_create_only_and_has_no_pages_write(self):
        workflow = (ROOT / ".github/workflows/notify-publication.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        for input_name in ("project_id", "target_basename", "publication_id", "commit_sha"):
            self.assertIn(f"      {input_name}:", workflow)
        self.assertIn("permissions: {}", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("pages: write", workflow)
        self.assertNotIn("id-token: write", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("ref: ${{ inputs.commit_sha }}", workflow)
        self.assertIn("test \"$(git rev-parse HEAD)\" = \"$COMMIT_SHA\"", workflow)
        self.assertIn('.operation == "create"', workflow)
        self.assertIn('.notify == true', workflow)
        self.assertIn("slack_notification verify-url", workflow)
        self.assertIn("slack_notification send", workflow)
        self.assertNotIn("accept-source.yml", workflow)


if __name__ == "__main__":
    unittest.main()
