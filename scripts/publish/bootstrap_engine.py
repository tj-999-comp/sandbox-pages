"""Plan and apply a fixed historical record backfill."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from .acceptance_files import AcceptedFile, AcceptanceFileError, validate_source_tree
from .content_safety import ContentSafetyError, validate_source_html_tree
from .index_generator import generate_indexes, load_current_manifests, render_global_index, render_project_index
from .metadata_schema import MetadataSchemaError, load_metadata, validate_metadata
from .provenance import ProvenanceError, ProvenanceDriftError, assert_no_drift, build_manifest, inspect_drift, load_manifest, serialize_manifest
from .record_navigation import build_record_navigation, update_record_navigation
from .rendered_renderer import RenderedRendererError, render_work_record
from .source_registry import SourceRegistryError, load_registry


TARGET_RE = re.compile(r"^work_record_[0-9]{3}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class BootstrapError(ValueError):
    """Raised when a historical backfill cannot be safely planned or applied."""


@dataclass(frozen=True)
class BootstrapResult:
    project_id: str
    source_commit_sha: str
    publication_id: str
    operation: str
    no_op: bool
    notify: bool
    target_basenames: tuple[str, ...]
    changed_paths: tuple[str, ...]
    manifest_path: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "source_commit_sha": self.source_commit_sha,
            "publication_id": self.publication_id,
            "operation": self.operation,
            "no_op": self.no_op,
            "notify": self.notify,
            "target_basenames": list(self.target_basenames),
            "changed_paths": list(self.changed_paths),
            "manifest_path": self.manifest_path,
        }


def parse_target_basenames(value: str | Iterable[str]) -> tuple[str, ...]:
    """Normalize a comma-separated or iterable target list."""

    if isinstance(value, str):
        values = [item.strip() for item in value.split(",") if item.strip()]
    else:
        values = list(value)
    if not values or any(not isinstance(item, str) or TARGET_RE.fullmatch(item) is None for item in values):
        raise BootstrapError("target_basenames must contain work_record_001 through work_record_999")
    normalized = tuple(sorted(set(values), key=lambda item: int(item[-3:])))
    if len(normalized) != len(values):
        raise BootstrapError("target_basenames must not contain duplicates")
    return normalized


def run_bootstrap(
    *,
    repository_root: str | Path,
    registry_path: str | Path,
    provenance_root: str | Path,
    source_checkout: str | Path,
    project_id: str,
    source_commit_sha: str,
    target_basenames: str | Iterable[str],
    publication_id: str,
    accepted_at: str,
    source_branch_ref: str | None = None,
    expected_main_sha: str | None = None,
    dry_run: bool = False,
    notify: bool = False,
) -> BootstrapResult:
    """Validate, plan, or apply all fixed targets in one audited operation."""

    root = Path(repository_root).resolve()
    provenance_path = Path(provenance_root).resolve()
    checkout = Path(source_checkout).resolve()
    if provenance_path != root / "provenance":
        raise BootstrapError("provenance_root must be Repository A's provenance directory")
    if not SHA_RE.fullmatch(source_commit_sha):
        raise BootstrapError("source_commit_sha must be a full lowercase SHA")
    targets = parse_target_basenames(target_basenames)
    registry = load_registry(registry_path)
    source = next((item for item in registry["sources"] if item["project_id"] == project_id), None)
    if source is None:
        raise BootstrapError(f"project_id is not registered: {project_id}")
    if source["enabled"] is not True:
        raise BootstrapError("bootstrap requires an enabled source")
    if not checkout.is_dir() or checkout.is_symlink():
        raise BootstrapError("source checkout must be a regular directory")
    _assert_clean_worktree(root)
    _assert_expected_head(root, expected_main_sha)

    source_root = checkout / PurePosixPath(source["source_directory"])
    if not source_root.is_dir():
        raise BootstrapError(f"registered source directory does not exist: {source['source_directory']}")
    _assert_source_commit(checkout, source_commit_sha, source_branch_ref)
    try:
        accepted = validate_source_tree(source_root, source)
    except AcceptanceFileError as exc:
        raise BootstrapError(f"source inventory validation failed: {exc}") from exc
    if source["html_mode"] == "source_html":
        try:
            validate_source_html_tree(source_root, source)
        except ContentSafetyError as exc:
            raise BootstrapError(f"source HTML safety validation failed: {exc}") from exc

    previous = _latest_manifest(provenance_path, project_id)
    _assert_previous_source(previous, source, source_commit_sha, checkout)
    destination = root / PurePosixPath(source["destination_directory"])
    try:
        assert_no_drift(previous, _inventory_directory(destination, ignored_paths={"index.html"}))
    except ProvenanceDriftError as exc:
        raise BootstrapError(str(exc)) from exc
    try:
        generate_indexes(root, check=True)
    except (OSError, ProvenanceError, ValueError) as exc:
        raise BootstrapError(f"current generated indexes are stale: {exc}") from exc

    metadata_by_basename = _load_all_metadata(source_root, source, accepted.record_basenames, project_id)
    publishable = {basename for basename, metadata in metadata_by_basename.items() if metadata["publish"] is True}
    previous_records = {record["basename"]: record["metadata"] for record in previous["records"]}
    missing_publishable = publishable - set(previous_records)
    new_targets = set(targets) - set(previous_records)
    if missing_publishable != new_targets:
        missing = ",".join(sorted(missing_publishable - new_targets)) or "none"
        unexpected = ",".join(sorted(new_targets - missing_publishable)) or "none"
        raise BootstrapError(
            "target set must cover every unpublished publish:true record; "
            f"missing_targets={missing}; already_or_nonpublish={unexpected}"
        )
    for basename in targets:
        if basename not in metadata_by_basename:
            raise BootstrapError(f"target basename is not present in source: {basename}")
        if metadata_by_basename[basename] != previous_records.get(basename, metadata_by_basename[basename]):
            raise BootstrapError(f"existing published metadata differs from source: {basename}")

    desired_records = dict(previous_records)
    desired_records.update({basename: metadata_by_basename[basename] for basename in targets})
    navigation_manifests = [item for item in load_current_manifests(provenance_path) if item["project_id"] != project_id]
    navigation_manifests.append(
        {
            "project_id": project_id,
            "records": [
                {"basename": basename, "metadata": metadata}
                for basename, metadata in desired_records.items()
            ],
        }
    )

    with tempfile.TemporaryDirectory(prefix="sandbox-pages-bootstrap-") as temp_dir:
        staged_destination = Path(temp_dir) / "destination"
        _copy_regular_tree(destination, staged_destination)
        for source_path in _support_paths(source):
            _copy_one_regular_file(source_root / source_path, staged_destination / source_path, source_path)
        for basename in targets:
            for source_path in _record_public_paths(source, basename):
                _copy_one_regular_file(source_root / source_path, staged_destination / source_path, source_path)
            navigation = build_record_navigation(navigation_manifests, project_id=project_id, basename=basename)
            html_path = staged_destination / f"{basename}.html"
            if source["html_mode"] == "a_rendered":
                try:
                    html_path.write_text(
                        render_work_record(
                            source_root / "md" / f"{basename}.md",
                            metadata_by_basename[basename],
                            expected_project_id=project_id,
                            navigation=navigation,
                        ),
                        encoding="utf-8",
                    )
                except RenderedRendererError as exc:
                    raise BootstrapError(f"renderer failed: {basename}: {exc}") from exc

        for basename in desired_records:
            html_path = staged_destination / f"{basename}.html"
            if not html_path.is_file():
                raise BootstrapError(f"published record HTML is missing: {basename}")
            navigation = build_record_navigation(navigation_manifests, project_id=project_id, basename=basename)
            html_path.write_text(
                update_record_navigation(html_path.read_text(encoding="utf-8"), navigation),
                encoding="utf-8",
            )

        final_published = _inventory_directory(staged_destination, ignored_paths={"index.html"})
        operation = "update" if previous_records else "create"
        manifest = build_manifest(
            publication_id=publication_id,
            project_id=project_id,
            source_repository=source["source_repository"],
            source_ref=source["source_ref"],
            source_commit_sha=source_commit_sha,
            public_base_path=source["public_base_path"],
            accepted_at=accepted_at,
            operation=operation,
            metadata_by_basename=desired_records,
            source_files=accepted.files,
            published_files=final_published,
            notify=notify,
        )
        if _is_content_noop(previous, manifest):
            return BootstrapResult(project_id, source_commit_sha, publication_id, operation, True, False, targets, (), None)

        manifests = [item for item in load_current_manifests(provenance_path) if item["project_id"] != project_id]
        manifests.append(manifest)
        rendered_indexes = {
            Path("projects/index.html"): render_global_index(manifests),
            Path(source["destination_directory"]) / "index.html": render_project_index(manifest),
        }
        manifest_relative = Path("provenance") / project_id / f"{publication_id}.json"
        destination_prefix = PurePosixPath(source["destination_directory"])
        changed_paths_set = {
            str(destination_prefix / item.path)
            for item in final_published
            if _files_differ(staged_destination / item.path, destination / item.path)
        }
        changed_paths_set.update(
            path.as_posix()
            for path, content in rendered_indexes.items()
            if _content_differs(root / path, content)
        )
        manifest_text = serialize_manifest(manifest)
        if _content_differs(root / manifest_relative, manifest_text):
            changed_paths_set.add(manifest_relative.as_posix())
        changed_paths = tuple(sorted(changed_paths_set))
        expected_paths = set(changed_paths)
        if dry_run:
            return BootstrapResult(project_id, source_commit_sha, publication_id, operation, False, notify, targets, changed_paths, manifest_relative.as_posix())

        _copy_regular_tree(staged_destination, destination)
        manifest_path = root / manifest_relative
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(serialize_manifest(manifest), encoding="utf-8")
        for relative, content in rendered_indexes.items():
            output = root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")

    _assert_allowed_worktree_changes(root, expected_paths)
    _verify_applied_state(root, destination, manifest, source["destination_directory"])
    return BootstrapResult(
        project_id, source_commit_sha, publication_id, operation, False, notify, targets,
        tuple(sorted(_git_status_paths(root))), manifest_relative.as_posix(),
    )


def _load_all_metadata(source_root: Path, source: Mapping[str, Any], basenames: Iterable[str], project_id: str) -> dict[str, dict[str, Any]]:
    relative_directory = PurePosixPath(source["metadata_directory"]).relative_to(PurePosixPath(source["source_directory"]))
    result = {}
    for basename in basenames:
        try:
            result[basename] = load_metadata(
                source_root / relative_directory / f"{basename}.yml",
                expected_basename=basename,
                registered_project_ids={project_id},
            )
        except (OSError, MetadataSchemaError) as exc:
            raise BootstrapError(f"source metadata cannot be validated: {basename}") from exc
    return result


def _assert_previous_source(previous: Mapping[str, Any], source: Mapping[str, Any], commit_sha: str, checkout: Path) -> None:
    if previous["source"]["repository"] != source["source_repository"] or previous["source"]["ref"] != source["source_ref"]:
        raise BootstrapError("previous provenance source does not match registry")
    previous_sha = previous["source"]["commit_sha"]
    if previous_sha != commit_sha and not _is_ancestor(checkout, previous_sha, commit_sha):
        raise BootstrapError("bootstrap source commit is older than the previous accepted source commit")


def _record_public_paths(source: Mapping[str, Any], basename: str) -> tuple[str, ...]:
    paths = [f"md/{basename}.md"]
    if source["html_mode"] == "source_html":
        paths.append(f"{basename}.html")
    return tuple(paths)


def _support_paths(source: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(source["support_files"]))


def _latest_manifest(provenance_root: Path, project_id: str) -> dict[str, Any]:
    project_root = provenance_root / project_id
    if not project_root.is_dir():
        raise BootstrapError(f"provenance directory does not exist: {project_root}")
    candidates = []
    for path in sorted(project_root.glob("*.json")):
        try:
            manifest = load_manifest(path)
        except ProvenanceError as exc:
            raise BootstrapError(f"invalid previous provenance: {path}") from exc
        if manifest["project_id"] != project_id:
            raise BootstrapError(f"provenance project_id does not match directory: {path}")
        candidates.append((manifest["accepted_at"], manifest["publication_id"], manifest))
    if not candidates:
        raise BootstrapError(f"no previous provenance manifest: {project_id}")
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def _is_content_noop(previous: Mapping[str, Any], planned: Mapping[str, Any]) -> bool:
    comparable = ("project_id", "source", "public_base_path", "source_files", "published_files", "records")
    return all(previous[field] == planned[field] for field in comparable)


def _assert_source_commit(checkout: Path, commit_sha: str, branch_ref: str | None) -> None:
    if _git(checkout, "rev-parse", "HEAD") != commit_sha:
        raise BootstrapError("source checkout does not match source_commit_sha")
    if branch_ref and not _is_ancestor(checkout, commit_sha, _git(checkout, "rev-parse", "--verify", f"{branch_ref}^{{commit}}")):
        raise BootstrapError("source commit is not an ancestor of the registered source branch")


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, descendant], check=False, capture_output=True)
    return completed.returncode == 0


def _inventory_directory(root: Path, *, ignored_paths: set[str] | None = None) -> list[AcceptedFile]:
    if not root.exists() or not root.is_dir() or root.is_symlink():
        raise BootstrapError(f"published root must be a regular directory: {root}")
    ignored = ignored_paths or set()
    result = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative in ignored:
            continue
        if path.is_symlink():
            raise BootstrapError(f"published tree contains a symlink: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise BootstrapError(f"published tree contains a non-regular file: {relative}")
        result.append(AcceptedFile(relative, path.stat().st_size, _sha256(path)))
    return result


def _copy_regular_tree(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        target = destination / path.relative_to(source)
        if path.is_symlink():
            raise BootstrapError(f"symlink is not accepted: {path}")
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        else:
            raise BootstrapError(f"non-regular file is not accepted: {path}")


def _copy_one_regular_file(source: Path, destination: Path, relative: str) -> None:
    if not source.is_file() or source.is_symlink():
        raise BootstrapError(f"source target is not a regular file: {relative}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _files_differ(source: Path, destination: Path) -> bool:
    if not destination.is_file():
        return True
    return source.read_bytes() != destination.read_bytes()


def _content_differs(path: Path, content: str) -> bool:
    return not path.is_file() or path.read_text(encoding="utf-8") != content


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(root), *args], check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise BootstrapError(f"git verification failed: {completed.stderr.strip() or 'unknown error'}")
    return completed.stdout.strip()


def _git_status_paths(root: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise BootstrapError(f"git status failed: {completed.stderr.strip() or 'unknown error'}")
    output = completed.stdout
    paths = set()
    for line in output.splitlines():
        if len(line) < 4 or " -> " in line:
            raise BootstrapError("automatic rename handling is not allowed")
        paths.add(PurePosixPath(line[3:]).as_posix())
    return paths


def _assert_clean_worktree(root: Path) -> None:
    paths = _git_status_paths(root)
    if paths:
        raise BootstrapError("Repository A worktree must be clean before bootstrap: " + ", ".join(sorted(paths)))


def _assert_expected_head(root: Path, expected_main_sha: str | None) -> None:
    if expected_main_sha and _git(root, "rev-parse", "HEAD") != expected_main_sha:
        raise BootstrapError("Repository A main is no longer the expected commit")


def _assert_allowed_worktree_changes(root: Path, expected_paths: set[str]) -> None:
    unexpected = sorted(_git_status_paths(root) - expected_paths)
    if unexpected:
        raise BootstrapError("bootstrap created changes outside the allowed scope: " + ", ".join(unexpected))


def _verify_applied_state(root: Path, destination: Path, manifest: Mapping[str, Any], _destination_directory: str) -> None:
    loaded = load_manifest(root / "provenance" / str(manifest["project_id"]) / f"{manifest['publication_id']}.json")
    if loaded != manifest:
        raise BootstrapError("written provenance manifest does not match the planned manifest")
    report = inspect_drift(loaded, _inventory_directory(destination, ignored_paths={"index.html"}))
    if not report.clean:
        raise BootstrapError("applied project files differ from new provenance manifest")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--provenance-root", type=Path, required=True)
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--source-commit-sha", required=True)
    parser.add_argument("--target-basenames", required=True)
    parser.add_argument("--publication-id", required=True)
    parser.add_argument("--accepted-at", required=True)
    parser.add_argument("--source-branch-ref")
    parser.add_argument("--expected-main-sha")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_bootstrap(
            repository_root=args.repository_root,
            registry_path=args.registry,
            provenance_root=args.provenance_root,
            source_checkout=args.source_checkout,
            project_id=args.project_id,
            source_commit_sha=args.source_commit_sha,
            target_basenames=args.target_basenames,
            publication_id=args.publication_id,
            accepted_at=args.accepted_at,
            source_branch_ref=args.source_branch_ref,
            expected_main_sha=args.expected_main_sha,
            dry_run=args.dry_run,
            notify=args.notify,
        )
    except (BootstrapError, OSError, SourceRegistryError, ProvenanceError) as exc:
        parser.exit(1, f"bootstrap failed: {exc}\n")
    print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
