"""Plan and apply one explicit, audited public work-record withdrawal."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .apply_engine import (
    ApplyConflictError,
    ApplyEngineError,
    _assert_allowed_worktree_changes,
    _assert_clean_worktree,
    _assert_expected_head,
    _git,
    _git_status_paths,
    _inventory_directory,
)
from .index_generator import generate_indexes, load_current_manifests, render_global_index, render_project_index
from .provenance import (
    ProvenanceError,
    assert_no_drift,
    build_manifest,
    load_manifest,
    serialize_manifest,
)
from .source_registry import SourceRegistryError, load_registry


class WithdrawalError(ApplyEngineError):
    """Raised when an explicit withdrawal cannot be safely applied."""


RECORD_BASENAME_RE = re.compile(r"^work_record_(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})$")
PUBLICATION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
def plan_withdrawal(
    *,
    repository_root: str | Path,
    registry_path: str | Path,
    provenance_root: str | Path,
    project_id: str,
    target_basename: str,
    withdrawal_id: str,
    expected_main_sha: str | None = None,
    expected_publication_id: str | None = None,
) -> dict[str, Any]:
    """Return a read-only withdrawal plan after validating current state."""

    root, source, previous, destination, removed_paths = _validate_request(
        repository_root=repository_root,
        registry_path=registry_path,
        provenance_root=provenance_root,
        project_id=project_id,
        target_basename=target_basename,
        withdrawal_id=withdrawal_id,
        expected_main_sha=expected_main_sha,
        expected_publication_id=expected_publication_id,
    )
    del source
    _assert_current_indexes(root)
    current_sha = _git(root, "rev-parse", "HEAD")
    return {
        "project_id": project_id,
        "target_basename": target_basename,
        "withdrawal_id": withdrawal_id,
        "expected_main_sha": current_sha,
        "previous_publication_id": previous["publication_id"],
        "removed_paths": removed_paths,
        "destination_directory": str(destination.relative_to(root).as_posix()),
        "remaining_record_count": len(previous["records"]) - 1,
        "operation": "withdraw",
        "notify": False,
        "no_op": False,
    }


def apply_withdrawal(
    *,
    repository_root: str | Path,
    registry_path: str | Path,
    provenance_root: str | Path,
    project_id: str,
    target_basename: str,
    withdrawal_id: str,
    expected_main_sha: str,
    expected_publication_id: str,
    confirmation: str,
    accepted_at: str | None = None,
) -> dict[str, Any]:
    """Remove only the named record and write its withdrawal provenance."""

    if confirmation != "WITHDRAW":
        raise WithdrawalError("confirmation must be exactly WITHDRAW")
    root, source, previous, destination, removed_paths = _validate_request(
        repository_root=repository_root,
        registry_path=registry_path,
        provenance_root=provenance_root,
        project_id=project_id,
        target_basename=target_basename,
        withdrawal_id=withdrawal_id,
        expected_main_sha=expected_main_sha,
        expected_publication_id=expected_publication_id,
    )
    _assert_current_indexes(root)

    previous_records = {
        record["basename"]: record["metadata"]
        for record in previous["records"]
        if record["basename"] != target_basename
    }
    destination_relative = PurePosixPath(destination.relative_to(root).as_posix())
    removed_set = {
        PurePosixPath(path).relative_to(destination_relative).as_posix()
        for path in removed_paths
    }
    published_files = [
        item for item in previous["published_files"] if item["path"] not in removed_set
    ]
    manifest = build_manifest(
        publication_id=withdrawal_id,
        project_id=project_id,
        source_repository=previous["source"]["repository"],
        source_ref=previous["source"]["ref"],
        source_commit_sha=previous["source"]["commit_sha"],
        public_base_path=previous["public_base_path"],
        accepted_at=accepted_at or _now_utc(),
        operation="withdraw",
        metadata_by_basename=previous_records,
        source_files=previous["source_files"],
        published_files=published_files,
        notify=False,
    )

    manifests = [
        item
        for item in load_current_manifests(root / "provenance")
        if item["project_id"] != project_id
    ]
    manifests.append(manifest)
    rendered_indexes = {
        Path("projects/index.html"): render_global_index(manifests),
        Path(source["destination_directory"]) / "index.html": render_project_index(manifest),
    }
    manifest_relative = Path("provenance") / project_id / f"{withdrawal_id}.json"
    expected_paths = set(removed_paths)
    expected_paths.update(path.as_posix() for path in rendered_indexes)
    expected_paths.add(manifest_relative.as_posix())

    for relative in removed_paths:
        path = root / PurePosixPath(relative)
        if not path.is_file() or path.is_symlink():
            raise WithdrawalError(f"withdrawal target is not a regular file: {relative}")
    for relative in removed_paths:
        (root / PurePosixPath(relative)).unlink()
    manifest_path = root / manifest_relative
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(serialize_manifest(manifest), encoding="utf-8")
    for relative, content in rendered_indexes.items():
        output = root / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")

    _assert_allowed_worktree_changes(root, expected_paths)
    _verify_withdrawal_state(
        root=root,
        destination=destination,
        manifest=manifest,
        target_basename=target_basename,
        removed_paths=removed_paths,
    )
    changed_paths = tuple(sorted(_git_status_paths(root)))
    return {
        "project_id": project_id,
        "target_basename": target_basename,
        "operation": "withdraw",
        "withdrawal_id": withdrawal_id,
        "previous_publication_id": previous["publication_id"],
        "no_op": False,
        "notify": False,
        "removed_paths": removed_paths,
        "changed_paths": list(changed_paths),
        "manifest_path": manifest_relative.as_posix(),
    }


def _validate_request(
    *,
    repository_root: str | Path,
    registry_path: str | Path,
    provenance_root: str | Path,
    project_id: str,
    target_basename: str,
    withdrawal_id: str,
    expected_main_sha: str | None,
    expected_publication_id: str | None,
) -> tuple[Path, Mapping[str, Any], dict[str, Any], Path, tuple[str, ...]]:
    root = Path(repository_root).resolve()
    provenance = Path(provenance_root).resolve()
    if provenance != root / "provenance":
        raise WithdrawalError("provenance_root must be Repository A's provenance directory")
    if not RECORD_BASENAME_RE.fullmatch(target_basename):
        raise WithdrawalError("target_basename must match work_record_### (001-999)")
    if not PUBLICATION_ID_RE.fullmatch(withdrawal_id):
        raise WithdrawalError("withdrawal_id is invalid")
    registry = load_registry(registry_path)
    source = next((item for item in registry["sources"] if item["project_id"] == project_id), None)
    if source is None:
        raise WithdrawalError(f"project_id is not registered: {project_id}")
    _assert_clean_worktree(root)
    _assert_expected_head(root, expected_main_sha)
    previous = _latest_manifest(provenance, project_id)
    if expected_publication_id is not None and previous["publication_id"] != expected_publication_id:
        raise WithdrawalError("latest provenance publication_id differs from expected preview")
    record_names = {record["basename"] for record in previous["records"]}
    if target_basename not in record_names:
        raise WithdrawalError(f"withdrawal target does not exist: {target_basename}")
    destination = root / PurePosixPath(source["destination_directory"])
    current_published = _inventory_directory(destination, ignored_paths={"index.html"})
    try:
        assert_no_drift(previous, current_published)
    except ProvenanceError as exc:
        raise WithdrawalError(f"published files differ from provenance: {exc}") from exc
    removed_paths = _target_paths(root, destination, target_basename, previous)
    return root, source, previous, destination, removed_paths


def _target_paths(
    root: Path, destination: Path, target_basename: str, previous: Mapping[str, Any]
) -> tuple[str, ...]:
    expected = {f"{target_basename}.html", f"md/{target_basename}.md"}
    published = {item["path"] for item in previous["published_files"]}
    if not expected <= published:
        missing = ", ".join(sorted(expected - published))
        raise WithdrawalError(f"provenance does not contain withdrawal target files: {missing}")
    paths = tuple(
        sorted(
            str(PurePosixPath(destination.relative_to(root).as_posix()) / relative)
            for relative in expected
        )
    )
    return paths


def _latest_manifest(provenance_root: Path, project_id: str) -> dict[str, Any]:
    project_root = provenance_root / project_id
    if not project_root.is_dir():
        raise WithdrawalError(f"provenance directory does not exist: {project_root}")
    candidates = []
    for path in sorted(project_root.glob("*.json")):
        try:
            manifest = load_manifest(path)
        except ProvenanceError as exc:
            raise WithdrawalError(f"invalid previous provenance: {path}") from exc
        if manifest["project_id"] != project_id:
            raise WithdrawalError(f"provenance project_id does not match directory: {path}")
        candidates.append((manifest["accepted_at"], manifest["publication_id"], manifest))
    if not candidates:
        raise WithdrawalError(f"no previous provenance manifest: {project_id}")
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def _assert_current_indexes(root: Path) -> None:
    try:
        generate_indexes(root, check=True)
    except (OSError, ProvenanceError, ValueError) as exc:
        raise WithdrawalError(f"current generated indexes are stale: {exc}") from exc


def _verify_withdrawal_state(
    *, root: Path, destination: Path, manifest: Mapping[str, Any], target_basename: str, removed_paths: tuple[str, ...]
) -> None:
    loaded = load_manifest(root / "provenance" / str(manifest["project_id"]) / f"{manifest['publication_id']}.json")
    if loaded != manifest:
        raise WithdrawalError("written withdrawal provenance does not match the planned manifest")
    current = _inventory_directory(destination, ignored_paths={"index.html"})
    try:
        assert_no_drift(loaded, current)
    except ProvenanceError as exc:
        raise WithdrawalError(f"withdrawn project files differ from provenance: {exc}") from exc
    if any((root / PurePosixPath(path)).exists() for path in removed_paths):
        raise WithdrawalError(f"withdrawal target still exists: {target_basename}")
    if any(record["basename"] == target_basename for record in loaded["records"]):
        raise WithdrawalError(f"withdrawal target remains in provenance: {target_basename}")
    _assert_current_indexes(root)


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repository-root", type=Path, default=Path.cwd())
    common.add_argument("--registry", type=Path, default=None)
    common.add_argument("--provenance-root", type=Path, default=None)
    common.add_argument("--project-id", required=True)
    common.add_argument("--target-basename", required=True)
    common.add_argument("--withdrawal-id", required=True)
    plan = subparsers.add_parser("plan", parents=[common])
    plan.add_argument("--expected-main-sha")
    plan.add_argument("--expected-publication-id")
    apply = subparsers.add_parser("apply", parents=[common])
    apply.add_argument("--expected-main-sha", required=True)
    apply.add_argument("--expected-publication-id", required=True)
    apply.add_argument("--confirmation", required=True)
    apply.add_argument("--accepted-at")
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    registry = args.registry or root / "config/sources.json"
    provenance = args.provenance_root or root / "provenance"
    try:
        if args.command == "plan":
            result = plan_withdrawal(
                repository_root=root,
                registry_path=registry,
                provenance_root=provenance,
                project_id=args.project_id,
                target_basename=args.target_basename,
                withdrawal_id=args.withdrawal_id,
                expected_main_sha=args.expected_main_sha,
                expected_publication_id=args.expected_publication_id,
            )
        else:
            result = apply_withdrawal(
                repository_root=root,
                registry_path=registry,
                provenance_root=provenance,
                project_id=args.project_id,
                target_basename=args.target_basename,
                withdrawal_id=args.withdrawal_id,
                expected_main_sha=args.expected_main_sha,
                expected_publication_id=args.expected_publication_id,
                confirmation=args.confirmation,
                accepted_at=args.accepted_at,
            )
    except (ApplyEngineError, ApplyConflictError, OSError, ProvenanceError, SourceRegistryError) as exc:
        parser.exit(1, f"withdrawal failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
