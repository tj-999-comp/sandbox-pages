"""Deterministic provenance manifests and published-file drift checks."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

from .acceptance_files import AcceptedFile
from .metadata_schema import MetadataSchemaError, validate_metadata


SUPPORTED_SCHEMA_VERSION = 1
OPERATIONS = frozenset({"create", "update", "withdraw"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")
PUBLICATION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REF_RE = re.compile(r"^refs/heads/[A-Za-z0-9._/-]+$")

MANIFEST_FIELDS = frozenset(
    {
        "schema_version", "publication_id", "project_id", "source", "operation",
        "accepted_at", "public_base_path", "source_files", "published_files", "records", "notify",
    }
)
SOURCE_FIELDS = frozenset({"repository", "ref", "commit_sha"})
FILE_FIELDS = frozenset({"path", "size_bytes", "sha256"})
RECORD_FIELDS = frozenset({"basename", "public_url", "metadata", "metadata_sha256"})


class ProvenanceError(ValueError):
    """Raised when a provenance manifest is invalid."""


class ProvenanceDriftError(ProvenanceError):
    """Raised when the current public files differ from the manifest."""


@dataclass(frozen=True)
class DriftReport:
    """Differences between the expected and current public file digests."""

    missing: tuple[str, ...]
    extra: tuple[str, ...]
    changed: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not (self.missing or self.extra or self.changed)


def build_manifest(
    *,
    publication_id: str,
    project_id: str,
    source_repository: str,
    source_ref: str,
    source_commit_sha: str,
    public_base_path: str,
    accepted_at: str,
    operation: str,
    metadata_by_basename: Mapping[str, Mapping[str, Any]],
    source_files: Iterable[AcceptedFile | Mapping[str, Any]],
    published_files: Iterable[AcceptedFile | Mapping[str, Any]],
    notify: bool,
) -> dict[str, Any]:
    """Build and validate a normalized provenance manifest."""

    normalized_metadata: dict[str, dict[str, Any]] = {}
    for basename, metadata in metadata_by_basename.items():
        if not isinstance(basename, str):
            raise ProvenanceError("record basename must be a string")
        try:
            normalized_metadata[basename] = validate_metadata(
                metadata, expected_basename=basename, registered_project_ids={project_id}
            )
        except MetadataSchemaError as exc:
            raise ProvenanceError(f"invalid metadata for {basename}: {exc}") from exc

    normalized_source_files = _normalize_files(source_files, "source_files")
    normalized_published_files = _normalize_files(published_files, "published_files")

    records = []
    for basename in sorted(normalized_metadata):
        metadata = normalized_metadata[basename]
        records.append(
            {
                "basename": basename,
                "public_url": _record_url(public_base_path, basename),
                "metadata": metadata,
                "metadata_sha256": _json_sha256(metadata),
            }
        )

    manifest = {
        "schema_version": SUPPORTED_SCHEMA_VERSION,
        "publication_id": publication_id,
        "project_id": project_id,
        "source": {
            "repository": source_repository,
            "ref": source_ref,
            "commit_sha": source_commit_sha,
        },
        "operation": operation,
        "accepted_at": accepted_at,
        "public_base_path": public_base_path,
        "source_files": normalized_source_files,
        "published_files": normalized_published_files,
        "records": records,
        "notify": notify,
    }
    return validate_manifest(manifest)


def validate_manifest(manifest: Any) -> dict[str, Any]:
    """Validate a manifest and return a detached, deterministically ordered copy."""

    if not isinstance(manifest, Mapping):
        raise ProvenanceError("manifest must be an object")
    _require_exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if manifest["schema_version"] != SUPPORTED_SCHEMA_VERSION:
        raise ProvenanceError(f"manifest.schema_version must be {SUPPORTED_SCHEMA_VERSION}")
    publication_id = manifest["publication_id"]
    if not isinstance(publication_id, str) or not PUBLICATION_ID_RE.fullmatch(publication_id):
        raise ProvenanceError("manifest.publication_id is invalid")
    project_id = manifest["project_id"]
    if not isinstance(project_id, str) or not project_id:
        raise ProvenanceError("manifest.project_id is invalid")

    source = manifest["source"]
    if not isinstance(source, Mapping):
        raise ProvenanceError("manifest.source must be an object")
    _require_exact_keys(source, SOURCE_FIELDS, "manifest.source")
    repository = source["repository"]
    source_ref = source["ref"]
    commit_sha = source["commit_sha"]
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        raise ProvenanceError("manifest.source.repository is invalid")
    if not isinstance(source_ref, str) or not REF_RE.fullmatch(source_ref):
        raise ProvenanceError("manifest.source.ref is invalid")
    if not isinstance(commit_sha, str) or not COMMIT_SHA_RE.fullmatch(commit_sha.lower()):
        raise ProvenanceError("manifest.source.commit_sha is invalid")

    operation = manifest["operation"]
    if operation not in OPERATIONS:
        raise ProvenanceError(f"manifest.operation is invalid: {operation}")
    accepted_at = _normalize_timestamp(manifest["accepted_at"])
    public_base_path = manifest["public_base_path"]
    expected_base = f"/sandbox-pages/projects/{project_id}/"
    if public_base_path != expected_base:
        raise ProvenanceError(f"manifest.public_base_path must be {expected_base}")
    if not isinstance(manifest["notify"], bool):
        raise ProvenanceError("manifest.notify must be boolean")

    source_files = _normalize_files(manifest["source_files"], "manifest.source_files")
    published_files = _normalize_files(manifest["published_files"], "manifest.published_files")

    records = _normalize_records(manifest["records"], project_id, public_base_path)
    return {
        "schema_version": SUPPORTED_SCHEMA_VERSION,
        "publication_id": publication_id,
        "project_id": project_id,
        "source": {
            "repository": repository,
            "ref": source_ref,
            "commit_sha": commit_sha.lower(),
        },
        "operation": operation,
        "accepted_at": accepted_at,
        "public_base_path": public_base_path,
        "source_files": source_files,
        "published_files": published_files,
        "records": records,
        "notify": manifest["notify"],
    }


def serialize_manifest(manifest: Mapping[str, Any]) -> str:
    """Serialize a validated manifest deterministically as UTF-8 JSON text."""

    normalized = validate_manifest(manifest)
    return json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def load_manifest(path: str) -> dict[str, Any]:
    """Load and validate a JSON manifest from disk."""

    try:
        with open(path, encoding="utf-8") as stream:
            data = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceError(f"manifest cannot be loaded: {path}") from exc
    return validate_manifest(data)


def inspect_drift(manifest: Mapping[str, Any], current_files: Iterable[AcceptedFile | Mapping[str, Any]]) -> DriftReport:
    """Compare current published files with the manifest without modifying either."""

    normalized = validate_manifest(manifest)
    expected = {item["path"]: item["sha256"] for item in normalized["published_files"]}
    actual_items = _normalize_files(current_files, "current_files")
    actual = {item["path"]: item["sha256"] for item in actual_items}
    missing = tuple(sorted(set(expected) - set(actual)))
    extra = tuple(sorted(set(actual) - set(expected)))
    changed = tuple(sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path]))
    return DriftReport(missing=missing, extra=extra, changed=changed)


def assert_no_drift(manifest: Mapping[str, Any], current_files: Iterable[AcceptedFile | Mapping[str, Any]]) -> None:
    """Raise instead of overwriting when published files drift from the manifest."""

    report = inspect_drift(manifest, current_files)
    if not report.clean:
        details = []
        if report.missing:
            details.append(f"missing={','.join(report.missing)}")
        if report.extra:
            details.append(f"extra={','.join(report.extra)}")
        if report.changed:
            details.append(f"changed={','.join(report.changed)}")
        raise ProvenanceDriftError("published files differ from provenance manifest: " + "; ".join(details))


def _normalize_files(files: Iterable[AcceptedFile | Mapping[str, Any]], label: str) -> list[dict[str, Any]]:
    if isinstance(files, (str, bytes)):
        raise ProvenanceError(f"{label} must be an array of files")
    try:
        values = list(files)
    except TypeError as exc:
        raise ProvenanceError(f"{label} must be an array of files") from exc
    normalized = []
    seen: set[str] = set()
    for file in values:
        if isinstance(file, AcceptedFile):
            path, size_bytes, sha256 = file.path, file.size_bytes, file.sha256
        elif isinstance(file, Mapping):
            _require_exact_keys(file, FILE_FIELDS, f"{label} entry")
            path, size_bytes, sha256 = file["path"], file["size_bytes"], file["sha256"]
        else:
            raise ProvenanceError(f"{label} entries must be file objects")
        if not isinstance(path, str) or not path or "\\" in path:
            raise ProvenanceError(f"{label} path is invalid")
        posix_path = PurePosixPath(path)
        if posix_path.is_absolute() or any(part in {"", ".", ".."} for part in posix_path.parts):
            raise ProvenanceError(f"{label} path must be normalized and relative: {path}")
        if path in seen:
            raise ProvenanceError(f"duplicate {label} path: {path}")
        if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 0:
            raise ProvenanceError(f"{label} size_bytes is invalid: {path}")
        if not isinstance(sha256, str) or not SHA256_RE.fullmatch(sha256.lower()):
            raise ProvenanceError(f"{label} sha256 is invalid: {path}")
        seen.add(path)
        normalized.append({"path": posix_path.as_posix(), "size_bytes": size_bytes, "sha256": sha256.lower()})
    return sorted(normalized, key=lambda item: item["path"])


def _normalize_records(records: Any, project_id: str, public_base_path: str) -> list[dict[str, Any]]:
    if not isinstance(records, list):
        raise ProvenanceError("manifest.records must be an array")
    normalized = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, Mapping):
            raise ProvenanceError("manifest.records entries must be objects")
        _require_exact_keys(record, RECORD_FIELDS, "manifest.records entry")
        basename = record["basename"]
        if not isinstance(basename, str) or not re.fullmatch(r"work_record_[0-9]{3}", basename):
            raise ProvenanceError(f"record basename is invalid: {basename}")
        if basename in seen:
            raise ProvenanceError(f"duplicate record basename: {basename}")
        public_url = record["public_url"]
        expected_url = _record_url(public_base_path, basename)
        if public_url != expected_url:
            raise ProvenanceError(f"record public_url is invalid: {basename}")
        try:
            metadata = validate_metadata(
                record["metadata"], expected_basename=basename, registered_project_ids={project_id}
            )
        except MetadataSchemaError as exc:
            raise ProvenanceError(f"invalid record metadata: {basename}") from exc
        metadata_sha256 = record["metadata_sha256"]
        if metadata_sha256 != _json_sha256(metadata):
            raise ProvenanceError(f"metadata digest mismatch: {basename}")
        seen.add(basename)
        normalized.append(
            {
                "basename": basename,
                "public_url": public_url,
                "metadata": metadata,
                "metadata_sha256": metadata_sha256.lower(),
            }
        )
    return sorted(normalized, key=lambda item: item["basename"])


def _record_url(public_base_path: str, basename: str) -> str:
    if not isinstance(public_base_path, str) or not public_base_path.endswith("/"):
        raise ProvenanceError("public_base_path must end with /")
    return f"{public_base_path}{basename}.html"


def _json_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _normalize_timestamp(value: Any) -> str:
    if not isinstance(value, str):
        raise ProvenanceError("manifest.accepted_at must be an ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProvenanceError("manifest.accepted_at must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ProvenanceError("manifest.accepted_at must include a timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_exact_keys(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    unknown = sorted(set(value) - expected)
    missing = sorted(expected - set(value))
    if unknown:
        raise ProvenanceError(f"{label} has unknown field(s): {', '.join(unknown)}")
    if missing:
        raise ProvenanceError(f"{label} is missing field(s): {', '.join(missing)}")
