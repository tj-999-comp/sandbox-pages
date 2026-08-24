import unittest
from unittest.mock import Mock

from scripts.publish.slack_notification import (
    NotificationInput,
    SlackNotificationError,
    build_payload,
    send_slack_notification,
    should_notify,
    verify_public_url,
)


class _Response:
    def __init__(self, status: int):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def getcode(self):
        return self.status


class SlackNotificationTests(unittest.TestCase):
    def setUp(self):
        self.notification = NotificationInput(
            project_id="B_Stats_Site",
            target_basename="work_record_037",
            publication_id="accept-123-B_Stats_Site-work_record_037",
            public_url="https://tj-999-comp.github.io/sandbox-pages/projects/B_Stats_Site/work_record_037.html",
        )

    def test_only_non_noop_create_with_notify_flag_is_eligible(self):
        self.assertTrue(should_notify(operation="create", no_op=False, notify=True, publication_id="pub", public_url="https://example.com"))
        self.assertFalse(should_notify(operation="update", no_op=False, notify=True, publication_id="pub", public_url="https://example.com"))
        self.assertFalse(should_notify(operation="create", no_op=True, notify=True, publication_id="pub", public_url="https://example.com"))
        self.assertFalse(should_notify(operation="create", no_op=False, notify=False, publication_id="pub", public_url="https://example.com"))

    def test_payload_contains_identity_and_url_only(self):
        payload = build_payload(self.notification)
        self.assertIn(self.notification.publication_id, payload["text"])
        self.assertIn(self.notification.public_url, payload["text"])
        self.assertNotIn("SLACK_WEBHOOK_URL", payload["text"])

    def test_public_url_verification_retries_until_success(self):
        opener = Mock(side_effect=[OSError("not ready"), _Response(200)])
        sleeper = Mock()
        verify_public_url(
            self.notification.public_url,
            attempts=3,
            delay_seconds=0,
            opener=opener,
            sleeper=sleeper,
        )
        self.assertEqual(opener.call_count, 2)
        sleeper.assert_called_once_with(0)

    def test_public_url_verification_is_bounded(self):
        opener = Mock(side_effect=OSError("not ready"))
        with self.assertRaisesRegex(SlackNotificationError, "did not become available"):
            verify_public_url(
                self.notification.public_url,
                attempts=2,
                delay_seconds=0,
                opener=opener,
                sleeper=Mock(),
            )
        self.assertEqual(opener.call_count, 2)

    def test_send_uses_json_payload_and_does_not_log_secret(self):
        opener = Mock(return_value=_Response(200))
        send_slack_notification(
            "https://hooks.slack.com/services/test/webhook",
            self.notification,
            opener=opener,
        )
        request = opener.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertIn(self.notification.publication_id.encode(), request.data)


if __name__ == "__main__":
    unittest.main()
