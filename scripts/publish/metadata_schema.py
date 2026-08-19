"""Validate and normalize work-record metadata from a source repository.

The publish pipeline owns this contract. This module intentionally accepts a
small YAML subset so the validator has no third-party runtime dependency.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping

from .source_registry import load_registry

SUPPORTED_SCHEMA_VERSION = 1
METADATA_FIELDS = frozenset({"schema_version", "title", "date", "project_id", "tags", "publish"})
RECORD_BASENAME_RE = re.compile(r"^work_record_(?P<number>[0-9]{3})$")
RECORD_FILENAME_RE = re.compile(r"^(work_record_[0-9]{3})\.(md|yml|html)$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class MetadataSchemaError(ValueError):
    """Raised when work-record metadata does not satisfy the publish contract."""


def load_metadata(path: str | Path, *, expected_basename: str | None = None,
                  registered_project_ids: set[str] | frozenset[str] | None = None) -> dict[str, Any]:
    """Load a YAML metadata file and return its deterministic normalized form."""
    metadata_path = Path(path)
    try:
        text = metadata_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise MetadataSchemaError(f"metadata file not found: {metadata_path}") from exc
    try:
        data = _parse_yaml_document(text)
    except ValueError as exc:
        raise MetadataSchemaError(f"metadata is not valid YAML: {metadata_path}") from exc
    return validate_metadata(data, expected_basename=expected_basename or metadata_path.stem,
                             registered_project_ids=registered_project_ids)


def load_registered_metadata(path: str | Path, *, registry_path: str | Path | None = None,
                             expected_basename: str | None = None) -> dict[str, Any]:
    """Load metadata while checking its project against the source registry."""
    registry = load_registry(registry_path) if registry_path is not None else load_registry()
    project_ids = frozenset(source["project_id"] for source in registry["sources"])
    return load_metadata(path, expected_basename=expected_basename,
                         registered_project_ids=project_ids)


def validate_metadata(data: Any, *, expected_basename: str | None = None,
                      registered_project_ids: set[str] | frozenset[str] | None = None) -> dict[str, Any]:
    """Validate metadata and return a detached, stable representation."""
    if not isinstance(data, Mapping):
        raise MetadataSchemaError("metadata must be an object")
    unknown = sorted(set(data) - METADATA_FIELDS)
    if unknown:
        raise MetadataSchemaError(f"metadata has unknown field(s): {', '.join(unknown)}")
    missing = sorted(METADATA_FIELDS - set(data))
    if missing:
        raise MetadataSchemaError(f"metadata is missing field(s): {', '.join(missing)}")

    _validate_basename(expected_basename)
    schema_version = data["schema_version"]
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise MetadataSchemaError("metadata.schema_version must be an integer")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise MetadataSchemaError(f"metadata.schema_version must be {SUPPORTED_SCHEMA_VERSION}")

    title = data["title"]
    if not isinstance(title, str) or not title.strip():
        raise MetadataSchemaError("metadata.title must be a non-empty string")
    normalized_title = title.strip()

    record_date = data["date"]
    if not isinstance(record_date, str) or not DATE_RE.fullmatch(record_date):
        raise MetadataSchemaError("metadata.date must be an ISO date string")
    try:
        normalized_date = date.fromisoformat(record_date).isoformat()
    except ValueError as exc:
        raise MetadataSchemaError("metadata.date must be a real YYYY-MM-DD date") from exc

    project_id = data["project_id"]
    if not isinstance(project_id, str) or not project_id:
        raise MetadataSchemaError("metadata.project_id must be a non-empty string")
    if registered_project_ids is not None and project_id not in registered_project_ids:
        raise MetadataSchemaError(f"metadata.project_id is not registered: {project_id}")

    tags = data["tags"]
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise MetadataSchemaError("metadata.tags must be an array of strings")
    normalized_tags = sorted(tags)

    publish = data["publish"]
    if not isinstance(publish, bool):
        raise MetadataSchemaError("metadata.publish must be boolean")

    return {"schema_version": SUPPORTED_SCHEMA_VERSION, "title": normalized_title,
            "date": normalized_date, "project_id": project_id, "tags": normalized_tags,
            "publish": publish}


def is_publish_candidate(metadata: Mapping[str, Any] | None) -> bool:
    """Return whether validated metadata may enter publish/update selection."""
    return metadata is not None and metadata.get("publish") is True


def validate_record_filenames(filenames: Iterable[str]) -> str:
    """Validate record filenames and return their shared, case-sensitive basename."""
    basenames = []
    for filename in filenames:
        if not isinstance(filename, str):
            raise MetadataSchemaError("record filename must be a string")
        match = RECORD_FILENAME_RE.fullmatch(filename)
        if not match:
            raise MetadataSchemaError(f"record filename is invalid: {filename}")
        basename = match.group(1)
        _validate_basename(basename)
        basenames.append(basename)
    if not basenames:
        raise MetadataSchemaError("at least one record filename is required")
    if len(set(basenames)) != 1:
        raise MetadataSchemaError("record files must use the same basename with matching case")
    return basenames[0]


def _validate_basename(basename: str | None) -> None:
    if basename is None or not RECORD_BASENAME_RE.fullmatch(basename):
        raise MetadataSchemaError("record basename must match work_record_001 through work_record_999")
    number = int(basename.rsplit("_", 1)[1])
    if not 1 <= number <= 999:
        raise MetadataSchemaError("record basename number must be between 001 and 999")


def _parse_yaml_document(text: str) -> Any:
    """Parse the contract's mapping/list YAML subset without unsafe evaluation."""
    lines = []
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if "\t" in raw_line[:indent]:
            raise ValueError("tabs are not supported for indentation")
        content = _strip_comment(raw_line[indent:]).rstrip()
        if content:
            lines.append((indent, content))
    if not lines or lines[0][0] != 0:
        raise ValueError("document must start with an indented mapping")
    value, next_index = _parse_block(lines, 0, lines[0][0])
    if next_index != len(lines):
        raise ValueError("unexpected indentation")
    return value


def _parse_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    is_list = lines[index][1].startswith("- ") or lines[index][1] == "-"
    result: Any = [] if is_list else {}
    while index < len(lines) and lines[index][0] == indent:
        content = lines[index][1]
        if is_list:
            if not content.startswith("-") or (len(content) > 1 and content[1] != " "):
                raise ValueError("mixed mapping and list")
            result.append(_parse_scalar(content[1:].strip()))
            index += 1
            continue
        if ":" not in content:
            raise ValueError("mapping entry must contain a colon")
        key, raw_value = content.split(":", 1)
        if not key or key.strip() != key or key in result:
            raise ValueError("invalid or duplicate mapping key")
        raw_value = raw_value.strip()
        index += 1
        if raw_value:
            result[key] = _parse_scalar(raw_value)
            continue
        if index >= len(lines) or lines[index][0] <= indent:
            raise ValueError("mapping value is missing")
        result[key], index = _parse_block(lines, index, lines[index][0])
    return result, index


def _parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_parse_scalar(item.strip()) for item in inner.split(",")]
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return json.loads(value)
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def _strip_comment(value: str) -> str:
    quoted = None
    for index, character in enumerate(value):
        if character in {'"', "'"}:
            quoted = None if quoted == character else character if quoted is None else quoted
        elif character == "#" and quoted is None and (index == 0 or value[index - 1].isspace()):
            return value[:index]
    return value
