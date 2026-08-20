"""Read-only no-op synchronization checks for registered projects."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from .acceptance_files import AcceptedFile
from .provenance import ProvenanceError, load_manifest
from .source_registry import load_registry


class SyncDryRunError(ValueError):
    """Raised when a no-op synchronization precondition is not met."""


@dataclass(frozen=True)
class SyncDryRunResult:
    project_id: str
    operation: str
    source_file_count: int
    published_file_count: int
    changes: tuple[str, ...]
    notify: bool

    @property
    def is_noop(self) -> bool:
        return not self.changes and self.operation == "noop"

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "operation": self.operation,
            "source_file_count": self.source_file_count,
            "published_file_count": self.published_file_count,
            "changes": list(self.changes),
            "notify": self.notify,
        }


def run_noop_dry_run(
    *,
    source_root: str | Path,
    published_root: str | Path,
    manifest_path: str | Path,
    source: Mapping[str, Any],
) -> SyncDryRunResult:
    """Validate source and published trees without modifying either tree.

    A successful result is ``operation=noop`` only when both inventories match
    the manifest exactly.  The operation deliberately rejects a non-bootstrap
    operation or a notification request: this command cannot publish, deploy,
    or notify.
    """

    manifest = load_manifest(manifest_path)
    project_id = source.get("project_id")
    if project_id != manifest["project_id"]:
        raise SyncDryRunError("source project_id does not match manifest")
    if manifest["operation"] != "create":
        raise SyncDryRunError("no-op bootstrap dry-run requires manifest.operation=create")
    if manifest["notify"]:
        raise SyncDryRunError("bootstrap dry-run must not notify")

    source_path = Path(source_root) / PurePosixPath(source["source_directory"])
    # The bootstrap baseline predates source-side metadata files.  The dry-run
    # therefore inventories the registered source directory and compares it
    # to the already accepted manifest; the full source validator remains the
    # gate for a future publish after the source migration.
    accepted = _inventory_directory(source_path)
    expected_source = _file_map(manifest["source_files"])
    actual_source = _file_map(accepted)
    _assert_inventory_match("source", expected_source, actual_source)

    # Project index files are derived and owned by repository A. They are
    # verified by index_generator --check instead of the source publication
    # manifest, which intentionally tracks only accepted project payloads.
    actual_published = _file_map(
        _inventory_directory(Path(published_root), ignored_paths={"index.html"})
    )
    expected_published = _file_map(manifest["published_files"])
    _assert_inventory_match("published", expected_published, actual_published)

    return SyncDryRunResult(
        project_id=project_id,
        operation="noop",
        source_file_count=len(actual_source),
        published_file_count=len(actual_published),
        changes=(),
        notify=False,
    )


def _inventory_directory(
    root: Path, *, ignored_paths: set[str] | None = None
) -> list[AcceptedFile]:
    if not root.is_dir() or root.is_symlink():
        raise SyncDryRunError(f"published root must be a regular directory: {root}")
    files: list[AcceptedFile] = []
    ignored = ignored_paths or set()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise SyncDryRunError(f"published tree contains a symlink: {relative}")
        if path.is_dir():
            continue
        if relative in ignored:
            continue
        if not path.is_file():
            raise SyncDryRunError(f"published tree contains a non-regular file: {relative}")
        files.append(AcceptedFile(relative, path.stat().st_size, _sha256(path)))
    return files


def _file_map(files: Iterable[AcceptedFile | Mapping[str, Any]]) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for item in files:
        if isinstance(item, AcceptedFile):
            path, size, digest = item.path, item.size_bytes, item.sha256
        else:
            path, size, digest = item["path"], item["size_bytes"], item["sha256"]
        result[path] = (size, digest)
    return result


def _assert_inventory_match(label: str, expected: Mapping[str, tuple[int, str]], actual: Mapping[str, tuple[int, str]]) -> None:
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path])
    if missing or extra or changed:
        details = []
        if missing:
            details.append(f"missing={','.join(missing)}")
        if extra:
            details.append(f"extra={','.join(extra)}")
        if changed:
            details.append(f"changed={','.join(changed)}")
        raise SyncDryRunError(f"{label} inventory differs from manifest: {'; '.join(details)}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="source repository root")
    parser.add_argument("--published-root", type=Path, required=True, help="published project directory")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    registry = load_registry(args.registry) if args.registry else load_registry()
    sources = {item["project_id"]: item for item in registry["sources"]}
    if args.project not in sources:
        parser.error(f"unknown project: {args.project}")
    try:
        result = run_noop_dry_run(
            source_root=args.source_root,
            published_root=args.published_root,
            manifest_path=args.manifest,
            source=sources[args.project],
        )
    except (OSError, ProvenanceError, SyncDryRunError) as exc:
        parser.exit(1, f"sync dry-run failed: {exc}\n")
    print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
