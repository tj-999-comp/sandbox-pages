"""Verify a published URL and send a safe Slack notification."""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class SlackNotificationError(RuntimeError):
    """Raised when URL verification or Slack delivery fails."""


@dataclass(frozen=True)
class NotificationInput:
    project_id: str
    target_basename: str
    title: str
    publication_id: str
    public_url: str


def should_notify(*, operation: str, no_op: bool, notify: bool, publication_id: str, public_url: str) -> bool:
    """Return whether a completed apply is eligible for the initial notification policy."""

    return (
        operation == "create"
        and not no_op
        and notify
        and bool(publication_id)
        and bool(public_url)
    )


def build_payload(notification: NotificationInput) -> dict[str, str]:
    """Build a compact payload without including secrets or source internals."""

    return {
        "text": (
            f"公開完了: {notification.title}\n"
            f"プロジェクト: {notification.project_id}\n"
            f"対象: {notification.target_basename}\n"
            f"publication_id: {notification.publication_id}\n"
            f"公開URL: {notification.public_url}"
        )
    }


def resolve_public_url(site_url: str, record_path: str) -> str:
    """Combine the Pages origin with the manifest's absolute record path."""

    site = urlparse(site_url)
    record = urlparse(record_path)
    if site.scheme != "https" or not site.netloc:
        raise SlackNotificationError("Pages site URL must be an HTTPS URL")
    if (
        record.scheme
        or record.netloc
        or not record.path.startswith("/")
        or record.params
        or record.query
        or record.fragment
    ):
        raise SlackNotificationError("record public URL must be an absolute site path")
    return f"{site.scheme}://{site.netloc}{record.path}"


def verify_public_url(
    public_url: str,
    *,
    attempts: int = 5,
    timeout_seconds: float = 10,
    delay_seconds: float = 10,
    opener: Callable[..., object] = urlopen,
    sleeper: Callable[[float], None] = time.sleep,
) -> None:
    """Wait for a successful public URL response with a bounded retry."""

    _require_https_url(public_url, "public URL")
    if attempts < 1:
        raise SlackNotificationError("URL verification attempts must be positive")
    last_error = "no response"
    for attempt in range(attempts):
        try:
            request = Request(public_url, method="GET")
            with opener(request, timeout=timeout_seconds) as response:
                status = getattr(response, "status", None)
                if status is None:
                    status = response.getcode()
                if 200 <= status < 400:
                    return
                last_error = f"HTTP status {status}"
        except (HTTPError, URLError, OSError) as exc:
            last_error = exc.__class__.__name__
        if attempt + 1 < attempts:
            sleeper(delay_seconds)
    raise SlackNotificationError(f"public URL did not become available: {last_error}")


def send_slack_notification(
    webhook_url: str,
    notification: NotificationInput,
    *,
    timeout_seconds: float = 10,
    opener: Callable[..., object] = urlopen,
) -> None:
    """Send one webhook request without exposing the webhook URL in errors."""

    _require_https_url(webhook_url, "Slack webhook URL")
    payload = json.dumps(build_payload(notification), ensure_ascii=False).encode("utf-8")
    request = Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener(request, timeout=timeout_seconds) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            if not 200 <= status < 300:
                raise SlackNotificationError(f"Slack webhook returned HTTP status {status}")
    except SlackNotificationError:
        raise
    except (HTTPError, URLError, OSError) as exc:
        raise SlackNotificationError(f"Slack webhook request failed: {exc.__class__.__name__}") from exc


def _require_https_url(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise SlackNotificationError(f"{label} must be an HTTPS URL")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify-url")
    verify.add_argument("--url", required=True)
    verify.add_argument("--attempts", type=int, default=5)
    verify.add_argument("--delay-seconds", type=float, default=10)

    resolve = subparsers.add_parser("resolve-url")
    resolve.add_argument("--site-url", required=True)
    resolve.add_argument("--record-path", required=True)

    send = subparsers.add_parser("send")
    send.add_argument("--webhook-env", default="SLACK_WEBHOOK_URL")
    send.add_argument("--project-id", required=True)
    send.add_argument("--target-basename", required=True)
    send.add_argument("--title", required=True)
    send.add_argument("--publication-id", required=True)
    send.add_argument("--public-url", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "resolve-url":
            print(resolve_public_url(args.site_url, args.record_path))
        elif args.command == "verify-url":
            verify_public_url(args.url, attempts=args.attempts, delay_seconds=args.delay_seconds)
        else:
            webhook_url = os.environ.get(args.webhook_env, "")
            if not webhook_url:
                raise SlackNotificationError(f"required environment variable is missing: {args.webhook_env}")
            send_slack_notification(
                webhook_url,
                NotificationInput(
                    project_id=args.project_id,
                    target_basename=args.target_basename,
                    title=args.title,
                    publication_id=args.publication_id,
                    public_url=args.public_url,
                ),
            )
    except SlackNotificationError as exc:
        parser.exit(1, f"notification failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
