import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.dev.github_app_token import (
    GitHubAppError,
    _classify_keychain_failure,
    _read_keychain_secret,
    diagnose_keychain_item,
)


class GitHubAppTokenTests(unittest.TestCase):
    def test_keychain_failure_classification_is_safe(self):
        self.assertEqual(_classify_keychain_failure("The specified item could not be found"), "not_found")
        self.assertEqual(_classify_keychain_failure("User interaction is not allowed"), "access_denied")
        self.assertEqual(_classify_keychain_failure("One or more parameters were not valid"), "keychain_search_invalid")
        self.assertEqual(_classify_keychain_failure("unexpected failure"), "security_command_failed")

    @patch("scripts.dev.github_app_token._keychain_candidates", return_value=(Path("/tmp/login.keychain-db"),))
    @patch("scripts.dev.github_app_token.subprocess.run")
    def test_missing_item_reports_service_and_account_without_secret(self, run, _candidates):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=44,
            stdout="",
            stderr="The specified item could not be found in the keychain.",
        )
        with self.assertRaisesRegex(
            RuntimeError,
            r"Keychain item not found: service='service' account='account'",
        ) as context:
            _read_keychain_secret("account", "service")
        self.assertNotIn("PRIVATE KEY", str(context.exception))

    @patch("scripts.dev.github_app_token._read_keychain_secret", side_effect=GitHubAppError(
        "Keychain item not found: service='service' account='account'; add the existing GitHub App PEM to the macOS login keychain"
    ))
    def test_diagnose_returns_missing_status_without_secret(self, _read):
        result = diagnose_keychain_item(account="account", service="service")
        self.assertEqual(result["status"], "missing")
        self.assertNotIn("PRIVATE KEY", result["message"])


if __name__ == "__main__":
    unittest.main()
