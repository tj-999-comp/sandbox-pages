"""Validate the file set accepted from a registered source repository.

This module is intentionally independent from source-side validation.  A
source repository may perform a preflight check, but Repository A derives and
rechecks the accepted file set from its own source registry before publishing.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .metadata_schema import RECORD_BASENAME_RE


RECORD_MD_RE = re.compile(r"^work_record_[0-9]{3}\.md$")
RECORD_METADATA_RE = re.compile(r"^work_record_[0-9]{3}\.yml$")
RECORD_HTML_RE = re.compile(r"^work_record_[0-9]{3}\.html$")
ALLOWED_RECORD_DIRS = frozenset({"md", "metadata"})


class AcceptanceFileError(ValueError):
    """Raised when a source tree is outside the registered acceptance scope."""


@dataclass(frozen=True)
class AcceptedFile:
    """A deterministic digest entry for one accepted regular file."""

    path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class AcceptedSource:
    """The validated source inventory used by later acceptance steps."""

    project_id: str
    html_mode: str
    files: tuple[AcceptedFile, ...]
    record_basenames: tuple[str, ...]


def validate_source_tree(source_root: str | Path, source: Mapping[str, Any]) -> AcceptedSource:
    """Validate and inventory a registered source directory.

    Only the registered support files and the record file layouts described by
    ``html_mode`` are accepted.  The returned paths are source-relative POSIX
    paths sorted deterministically, with SHA-256 digests for later provenance.
    """

    root = Path(source_root)
    if not root.is_dir() or root.is_symlink():
        raise AcceptanceFileError("source root must be a regular directory")

    project_id = _required_string(source, "project_id")
    html_mode = _required_string(source, "html_mode")
    if html_mode not in {"source_html", "a_rendered"}:
        raise AcceptanceFileError(f"unsupported html_mode: {html_mode}")

    source_directory = _relative_registered_path(source, "source_directory")
    metadata_directory = _relative_registered_path(source, "metadata_directory")
    if not _is_descendant(metadata_directory, source_directory):
        raise AcceptanceFileError("metadata_directory must be inside source_directory")
    source_parts = PurePosixPath(source_directory).parts
    metadata_parts = PurePosixPath(metadata_directory).parts
    metadata_relative = metadata_parts[len(source_parts):]
    if not metadata_relative or metadata_relative[0] not in ALLOWED_RECORD_DIRS:
        raise AcceptanceFileError("metadata_directory must be the registered metadata directory")

    support_files = source.get("support_files")
    if not isinstance(support_files, list) or any(
        not isinstance(path, str) or not _is_single_file_name(path) for path in support_files
    ):
        raise AcceptanceFileError("support_files must contain registered file names")
    support_paths = {PurePosixPath(path).as_posix() for path in support_files}
    ignored_files = source.get("ignored_files")
    if not isinstance(ignored_files, list) or any(
        not isinstance(path, str) or not path or "\\" in path
        or PurePosixPath(path).is_absolute()
        or any(part in {"", ".", ".."} for part in PurePosixPath(path).parts)
        for path in ignored_files
    ):
        raise AcceptanceFileError("ignored_files must contain normalized relative paths")
    ignored_paths = {PurePosixPath(path).as_posix() for path in ignored_files}
    if support_paths & ignored_paths:
        raise AcceptanceFileError("support_files and ignored_files must not overlap")
    allowed_directories = {"md", "/".join(metadata_relative)}

    limits = source.get("limits")
    if not isinstance(limits, Mapping):
        raise AcceptanceFileError("source limits are required")
    max_files = _positive_int(limits, "max_files")
    max_file_size = _positive_int(limits, "max_file_size_bytes")
    max_total_size = _positive_int(limits, "max_total_size_bytes")

    discovered: list[tuple[str, Path]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        relative_posix = relative.as_posix()
        if path.is_symlink():
            raise AcceptanceFileError(f"symlink is not accepted: {relative_posix}")
        if path.is_dir():
            if relative_posix not in allowed_directories:
                raise AcceptanceFileError(f"directory is not registered: {relative_posix}")
            continue
        if not path.is_file():
            raise AcceptanceFileError(f"non-regular file is not accepted: {relative_posix}")
        if relative_posix in ignored_paths:
            continue
        discovered.append((relative_posix, path))

    if len(discovered) > max_files:
        raise AcceptanceFileError(f"file count exceeds limit: {len(discovered)} > {max_files}")

    allowed_paths: set[str] = set(support_paths)
    record_files: dict[str, set[str]] = {}
    for relative_posix, _ in discovered:
        path = PurePosixPath(relative_posix)
        parts = path.parts
        if relative_posix in support_paths:
            continue
        if len(parts) == 2 and parts[0] == "md" and RECORD_MD_RE.fullmatch(parts[1]):
            record_files.setdefault(parts[1][:-3], set()).add("md")
            allowed_paths.add(relative_posix)
            continue
        if (
            len(parts) == len(metadata_relative) + 1
            and parts[: len(metadata_relative)] == metadata_relative
            and RECORD_METADATA_RE.fullmatch(parts[-1])
        ):
            record_files.setdefault(parts[-1][:-4], set()).add("metadata")
            allowed_paths.add(relative_posix)
            continue
        if html_mode == "source_html" and len(parts) == 1 and RECORD_HTML_RE.fullmatch(parts[0]):
            record_files.setdefault(parts[0][:-5], set()).add("html")
            allowed_paths.add(relative_posix)
            continue
        raise AcceptanceFileError(f"path or file type is not registered: {relative_posix}")

    if not record_files:
        raise AcceptanceFileError("at least one numbered work record is required")

    for basename, kinds in sorted(record_files.items()):
        if not RECORD_BASENAME_RE.fullmatch(basename):
            raise AcceptanceFileError(f"invalid record basename: {basename}")
        required = {"md", "metadata"}
        if html_mode == "source_html":
            required.add("html")
        if kinds != required:
            missing = sorted(required - kinds)
            extra = sorted(kinds - required)
            details = []
            if missing:
                details.append(f"missing {','.join(missing)}")
            if extra:
                details.append(f"unexpected {','.join(extra)}")
            raise AcceptanceFileError(f"record {basename} has incomplete files ({'; '.join(details)})")

    if set(relative for relative, _ in discovered) != allowed_paths:
        raise AcceptanceFileError("source tree contains files outside the accepted set")

    accepted: list[AcceptedFile] = []
    total_size = 0
    for relative_posix, path in discovered:
        size = path.stat().st_size
        if size > max_file_size:
            raise AcceptanceFileError(
                f"file exceeds size limit: {relative_posix} ({size} > {max_file_size})"
            )
        total_size += size
        accepted.append(AcceptedFile(relative_posix, size, _sha256(path)))
    if total_size > max_total_size:
        raise AcceptanceFileError(f"total size exceeds limit: {total_size} > {max_total_size}")

    accepted.sort(key=lambda item: item.path)
    return AcceptedSource(
        project_id=project_id,
        html_mode=html_mode,
        files=tuple(accepted),
        record_basenames=tuple(sorted(record_files)),
    )


def _required_string(source: Mapping[str, Any], field: str) -> str:
    value = source.get(field)
    if not isinstance(value, str) or not value:
        raise AcceptanceFileError(f"source.{field} is required")
    return value


def _relative_registered_path(source: Mapping[str, Any], field: str) -> str:
    value = _required_string(source, field)
    if value == ".":
        return value
    path = PurePosixPath(value)
    if path.is_absolute() or "\\" in value or any(part in {"", ".", ".."} for part in path.parts):
        raise AcceptanceFileError(f"source.{field} is not a normalized relative path")
    return path.as_posix()


def _is_descendant(path: str, parent: str) -> bool:
    path_parts = PurePosixPath(path).parts
    parent_parts = PurePosixPath(parent).parts
    return len(path_parts) > len(parent_parts) and path_parts[: len(parent_parts)] == parent_parts


def _is_single_file_name(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        bool(value)
        and "\\" not in value
        and not path.is_absolute()
        and len(path.parts) == 1
        and path.parts[0] not in {".", ".."}
    )


def _positive_int(mapping: Mapping[str, Any], field: str) -> int:
    value = mapping.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise AcceptanceFileError(f"source.limits.{field} must be a positive integer")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
