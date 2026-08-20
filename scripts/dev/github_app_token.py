"""Issue a short-lived GitHub App installation token from macOS Keychain."""

from __future__ import annotations

import argparse
import base64
import binascii
import getpass
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import jwt


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "github_app.json"
GITHUB_API = "https://api.github.com"


class GitHubAppError(RuntimeError):
    """Raised when App authentication or token issuance fails."""


def issue_installation_token(
    *,
    app_id: int,
    client_id: str,
    repository: str,
    keychain_service: str,
    keychain_account: str | None = None,
) -> dict[str, Any]:
    """Discover the repository installation and issue a fresh token."""

    account = keychain_account or getpass.getuser()
    private_key = _read_keychain_secret(account, keychain_service)
    now = int(time.time())
    claims = {
        "iat": now - 60,
        "exp": now + 540,
        # GitHub accepts the App's client ID for JWT identity.  Keeping app_id
        # in the config documents the registration while client_id is used for
        # the current authentication flow.
        "iss": client_id,
    }
    app_jwt = jwt.encode(claims, private_key, algorithm="RS256")
    installation = _github_json(
        f"/repos/{repository}/installation",
        method="GET",
        authorization=app_jwt,
    )
    installation_id = installation.get("id")
    if not isinstance(installation_id, int):
        raise GitHubAppError("repository installation response did not include an id")
    token_response = _github_json(
        f"/app/installations/{installation_id}/access_tokens",
        method="POST",
        authorization=app_jwt,
    )
    token = token_response.get("token")
    expires_at = token_response.get("expires_at")
    if not isinstance(token, str) or not token:
        raise GitHubAppError("installation token response did not include a token")
    return {
        "app_id": app_id,
        "repository": repository,
        "installation_id": installation_id,
        "expires_at": expires_at,
        "token": token,
    }


def _read_keychain_secret(account: str, service: str) -> str:
    try:
        completed = subprocess.run(
            ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GitHubAppError(
            f"cannot read Keychain item service={service!r} account={account!r}"
        ) from exc
    secret = completed.stdout.strip()
    if not secret.startswith("-----BEGIN"):
        try:
            decoded = base64.b64decode(secret, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise GitHubAppError("Keychain item does not contain a PEM private key") from exc
        secret = decoded.strip()
    if not secret.startswith("-----BEGIN") or "PRIVATE KEY-----" not in secret:
        raise GitHubAppError("Keychain item does not contain a PEM private key")
    return secret


def _github_json(path: str, *, method: str, authorization: str) -> dict[str, Any]:
    request = urllib.request.Request(
        GITHUB_API + path,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {authorization}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        detail = getattr(exc, "read", lambda: b"")()
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        raise GitHubAppError(f"GitHub API request failed: {path}: {detail or exc}") from exc
    if not isinstance(payload, dict):
        raise GitHubAppError(f"GitHub API response was not an object: {path}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--account", default=None, help="Keychain account; defaults to the macOS user")
    parser.add_argument("--print-token", action="store_true", help="print the short-lived token")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        result = issue_installation_token(
            app_id=int(config["app_id"]),
            client_id=config["client_id"],
            repository=config["repository"],
            keychain_service=config["keychain_service"],
            keychain_account=args.account,
        )
    except (OSError, KeyError, TypeError, ValueError, GitHubAppError) as exc:
        parser.exit(1, f"GitHub App token issuance failed: {exc}\n")
    if args.print_token:
        print(result["token"])
    else:
        safe_result = {key: value for key, value in result.items() if key != "token"}
        print(json.dumps(safe_result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
