import unittest
import tempfile
from pathlib import Path

from scripts.publish.bootstrap_engine import BootstrapError, run_bootstrap
from tests.test_apply_engine import _RenderedFixture, _git


class BootstrapEngineTests(unittest.TestCase):
    def test_bootstrap_applies_all_targets_and_repeated_input_is_noop(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _RenderedFixture(Path(temp_dir))
            result = run_bootstrap(
                repository_root=fixture.repo,
                registry_path=fixture.repo / "config/sources.json",
                provenance_root=fixture.repo / "provenance",
                source_checkout=fixture.checkout,
                project_id="tech_article_nortification",
                source_commit_sha=fixture.source_head,
                target_basenames="work_record_001",
                publication_id="bootstrap-test",
                accepted_at="2026-09-07T00:00:00Z",
                source_branch_ref="refs/heads/main",
                expected_main_sha=_git(fixture.repo, "rev-parse", "HEAD"),
            )
            self.assertFalse(result.no_op)
            self.assertFalse(result.notify)
            self.assertEqual(result.operation, "create")
            self.assertEqual(result.target_basenames, ("work_record_001",))
            _git(fixture.repo, "add", ".")
            _git(fixture.repo, "commit", "--quiet", "-m", "bootstrap")

            repeated = run_bootstrap(
                repository_root=fixture.repo,
                registry_path=fixture.repo / "config/sources.json",
                provenance_root=fixture.repo / "provenance",
                source_checkout=fixture.checkout,
                project_id="tech_article_nortification",
                source_commit_sha=fixture.source_head,
                target_basenames=["work_record_001"],
                publication_id="bootstrap-test-repeat",
                accepted_at="2026-09-07T00:01:00Z",
                source_branch_ref="refs/heads/main",
                expected_main_sha=_git(fixture.repo, "rev-parse", "HEAD"),
            )
            self.assertTrue(repeated.no_op)
            self.assertEqual(repeated.changed_paths, ())

    def test_bootstrap_requires_exact_unpublished_publishable_target_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = _RenderedFixture(Path(temp_dir))
            with self.assertRaisesRegex(BootstrapError, "target set must cover"):
                run_bootstrap(
                    repository_root=fixture.repo,
                    registry_path=fixture.repo / "config/sources.json",
                    provenance_root=fixture.repo / "provenance",
                    source_checkout=fixture.checkout,
                    project_id="tech_article_nortification",
                    source_commit_sha=fixture.source_head,
                    target_basenames="work_record_002",
                    publication_id="bootstrap-invalid-target",
                    accepted_at="2026-09-07T00:00:00Z",
                    source_branch_ref="refs/heads/main",
                    expected_main_sha=_git(fixture.repo, "rev-parse", "HEAD"),
                )


if __name__ == "__main__":
    unittest.main()
