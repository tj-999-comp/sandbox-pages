"""Load and validate the Repository A source registry.

The registry is deliberately data-only.  Values from a source repository are
never interpreted as commands or used to construct an arbitrary destination.
"""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPOSITORY_ROOT / "config" / "sources.json"

SUPPORTED_SCHEMA_VERSION = 1
SUPPORTED_HTML_MODES = frozenset({"source_html", "a_rendered"})
SUPPORTED_GENERATOR_IDS = frozenset({"b-stats-work-record-v1"})

_PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_REF_RE = re.compile(r"^refs/heads/[A-Za-z0-9._/-]+$")

_REGISTRY_FIELDS = frozenset({"schema_version", "sources"})
_SOURCE_FIELDS = frozenset(
    {
        "project_id",
        "source_repository",
        "source_ref",
        "source_directory",
        "metadata_directory",
        "destination_directory",
        "public_base_path",
        "support_files",
        "generator_id",
        "html_mode",
        "enabled",
        "limits",
    }
)
_LIMIT_FIELDS = frozenset(
    {"max_files", "max_file_size_bytes", "max_total_size_bytes"}
)
_REQUIRED_SOURCE_FIELDS = _SOURCE_FIELDS
_REQUIRED_LIMIT_FIELDS = _LIMIT_FIELDS


class SourceRegistryError(ValueError):
    """Raised when a source registry does not satisfy the registry contract."""


def load_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    """Read *path*, validate it, and return a deterministic normalized copy."""

    registry_path = Path(path)
    try:
        with registry_path.open(encoding="utf-8") as stream:
            data = json.load(stream)
    except FileNotFoundError as exc:
        raise SourceRegistryError(f"registry file not found: {registry_path}") from exc
    except json.JSONDecodeError as exc:
        raise SourceRegistryError(f"registry is not valid JSON: {registry_path}") from exc
    return validate_registry(data)


def validate_registry(data: Any) -> dict[str, Any]:
    """Validate registry data and return a stable, detached representation."""

    _require_mapping(data, "registry")
    _reject_unknown(data, _REGISTRY_FIELDS, "registry")
    _require_exact_keys(data, _REGISTRY_FIELDS, "registry")
    _require_int(data["schema_version"], "registry.schema_version")
    if data["schema_version"] != SUPPORTED_SCHEMA_VERSION:
        raise SourceRegistryError(
            f"registry.schema_version must be {SUPPORTED_SCHEMA_VERSION}"
        )
    if not isinstance(data["sources"], list):
        raise SourceRegistryError("registry.sources must be an array")

    normalized_sources = []
    project_ids: set[str] = set()
    for index, source in enumerate(data["sources"]):
        normalized = _validate_source(source, index)
        project_id = normalized["project_id"]
        if project_id in project_ids:
            raise SourceRegistryError(f"duplicate project_id: {project_id}")
        project_ids.add(project_id)
        normalized_sources.append(normalized)

    # Sort by the stable identifier, and copy all mutable containers so callers
    # cannot accidentally alter the object that was validated.
    normalized_sources.sort(key=lambda item: item["project_id"])
    return {
        "schema_version": SUPPORTED_SCHEMA_VERSION,
        "sources": normalized_sources,
    }


def _validate_source(source: Any, index: int) -> dict[str, Any]:
    label = f"sources[{index}]"
    _require_mapping(source, label)
    _reject_unknown(source, _SOURCE_FIELDS, label)
    _require_exact_keys(source, _REQUIRED_SOURCE_FIELDS, label)

    project_id = source["project_id"]
    if not isinstance(project_id, str) or not _PROJECT_ID_RE.fullmatch(project_id):
        raise SourceRegistryError(f"{label}.project_id is invalid")

    repository = source["source_repository"]
    if not isinstance(repository, str) or not _REPOSITORY_RE.fullmatch(repository):
        raise SourceRegistryError(f"{label}.source_repository is invalid")

    source_ref = source["source_ref"]
    if (
        not isinstance(source_ref, str)
        or "\\" in source_ref
        or ".." in source_ref
        or not _REF_RE.fullmatch(source_ref)
    ):
        raise SourceRegistryError(f"{label}.source_ref is invalid")

    source_directory = _validate_relative_path(source["source_directory"], f"{label}.source_directory")
    metadata_directory = _validate_relative_path(
        source["metadata_directory"], f"{label}.metadata_directory"
    )
    destination_directory = _validate_destination_path(
        source["destination_directory"], project_id, f"{label}.destination_directory"
    )
    public_base_path = _validate_public_base_path(
        source["public_base_path"], project_id, f"{label}.public_base_path"
    )
    if not _is_descendant(metadata_directory, source_directory):
        raise SourceRegistryError(
            f"{label}.metadata_directory must be inside source_directory"
        )

    support_files = source["support_files"]
    if not isinstance(support_files, list) or not support_files:
        raise SourceRegistryError(f"{label}.support_files must be a non-empty array")
    normalized_support_files = []
    seen_support_files: set[str] = set()
    for file_index, support_file in enumerate(support_files):
        support_label = f"{label}.support_files[{file_index}]"
        normalized_file = _validate_relative_path(support_file, support_label)
        if "/" in normalized_file:
            raise SourceRegistryError(f"{support_label} must be a file name")
        if normalized_file in seen_support_files:
            raise SourceRegistryError(f"duplicate support file: {normalized_file}")
        seen_support_files.add(normalized_file)
        normalized_support_files.append(normalized_file)

    generator_id = source["generator_id"]
    if (
        not isinstance(generator_id, str)
        or generator_id not in SUPPORTED_GENERATOR_IDS
    ):
        raise SourceRegistryError(f"{label}.generator_id is not supported")
    html_mode = source["html_mode"]
    if not isinstance(html_mode, str) or html_mode not in SUPPORTED_HTML_MODES:
        raise SourceRegistryError(f"{label}.html_mode is not supported")
    if not isinstance(source["enabled"], bool):
        raise SourceRegistryError(f"{label}.enabled must be boolean")

    limits = _validate_limits(source["limits"], label)
    return {
        "project_id": project_id,
        "source_repository": repository,
        "source_ref": source_ref,
        "source_directory": source_directory,
        "metadata_directory": metadata_directory,
        "destination_directory": destination_directory,
        "public_base_path": public_base_path,
        "support_files": sorted(normalized_support_files),
        "generator_id": generator_id,
        "html_mode": html_mode,
        "enabled": source["enabled"],
        "limits": limits,
    }


def _validate_limits(limits: Any, label: str) -> dict[str, int]:
    limits_label = f"{label}.limits"
    _require_mapping(limits, limits_label)
    _reject_unknown(limits, _LIMIT_FIELDS, limits_label)
    _require_exact_keys(limits, _REQUIRED_LIMIT_FIELDS, limits_label)
    result: dict[str, int] = {}
    for field in sorted(_LIMIT_FIELDS):
        value = limits[field]
        _require_int(value, f"{limits_label}.{field}")
        if value <= 0:
            raise SourceRegistryError(f"{limits_label}.{field} must be positive")
        result[field] = value
    if result["max_total_size_bytes"] < result["max_file_size_bytes"]:
        raise SourceRegistryError(
            f"{limits_label}.max_total_size_bytes must be at least max_file_size_bytes"
        )
    return {field: result[field] for field in sorted(result)}


def _validate_relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise SourceRegistryError(f"{label} must be a relative POSIX path")
    # Inspect the raw path before PurePosixPath normalizes away traversal
    # segments.  A value such as ``work-records/../private`` must not become
    # indistinguishable from the already-normalized ``private`` path.
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise SourceRegistryError(f"{label} must be a normalized relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise SourceRegistryError(f"{label} must not escape its project")
    return path.as_posix()


def _validate_destination_path(value: Any, project_id: str, label: str) -> str:
    normalized = _validate_relative_path(value, label)
    expected_prefix = PurePosixPath("projects") / project_id
    path = PurePosixPath(normalized)
    if len(path.parts) != 2 or path != expected_prefix:
        raise SourceRegistryError(f"{label} must be projects/{project_id}")
    return normalized


def _validate_public_base_path(value: Any, project_id: str, label: str) -> str:
    if not isinstance(value, str) or "\\" in value or not value.startswith("/"):
        raise SourceRegistryError(f"{label} must be an absolute URL path")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts[1:]):
        raise SourceRegistryError(f"{label} must not contain traversal")
    expected = f"/sandbox-pages/projects/{project_id}/"
    if value != expected:
        raise SourceRegistryError(f"{label} must be {expected}")
    return value


def _is_descendant(path: str, parent: str) -> bool:
    path_parts = PurePosixPath(path).parts
    parent_parts = PurePosixPath(parent).parts
    return len(path_parts) > len(parent_parts) and path_parts[: len(parent_parts)] == parent_parts


def _require_mapping(value: Any, label: str) -> None:
    if not isinstance(value, Mapping):
        raise SourceRegistryError(f"{label} must be an object")


def _require_int(value: Any, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SourceRegistryError(f"{label} must be an integer")


def _reject_unknown(value: Mapping[str, Any], allowed: frozenset[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise SourceRegistryError(f"{label} has unknown field(s): {', '.join(unknown)}")


def _require_exact_keys(value: Mapping[str, Any], required: frozenset[str], label: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise SourceRegistryError(f"{label} is missing field(s): {', '.join(missing)}")
