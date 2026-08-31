"""Safely apply one validated source acceptance payload to Repository A."""

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
from typing import Any, Callable, Mapping

from .acceptance_files import AcceptedFile, AcceptanceFileError, validate_source_tree
from .index_generator import load_current_manifests, render_global_index, render_project_index
from .metadata_schema import MetadataSchemaError, load_metadata, validate_metadata
from .rendered_renderer import RenderedRendererError, render_work_record
from .provenance import (
    ProvenanceDriftError,
    ProvenanceError,
    assert_no_drift,
    build_manifest,
    inspect_drift,
    load_manifest,
    serialize_manifest,
)
from .source_registry import SourceRegistryError, load_registry


class ApplyEngineError(ValueError):
    """Raised when an acceptance payload cannot be applied safely."""


class ApplyConflictError(ApplyEngineError):
    """Raised when the Repository A main commit changed during preparation."""


@dataclass(frozen=True)
class ApplyResult:
    """Summary of a completed apply or an intentionally skipped no-op."""

    project_id: str
    operation: str
    publication_id: str
    no_op: bool
    notify: bool
    changed_paths: tuple[str, ...]
    manifest_path: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "operation": self.operation,
            "publication_id": self.publication_id,
            "no_op": self.no_op,
            "notify": self.notify,
            "changed_paths": list(self.changed_paths),
            "manifest_path": self.manifest_path,
        }


ACCEPTANCE_FIELDS = frozenset(
    {
        "dry_run",
        "apply",
        "enabled",
        "project_id",
        "source",
        "previous_acceptance",
        "destination",
        "generator_id",
        "target_basename",
        "html_mode",
        "inventory",
        "target_inventory",
        "metadata",
        "validators",
    }
)
FILE_FIELDS = frozenset({"path", "size_bytes", "sha256"})
REQUEST_COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUEST_BASENAME_RE = re.compile(r"^work_record_[0-9]{3}$")


def apply_verified_payload(
    *,
    acceptance_path: str | Path,
    source_checkout: str | Path,
    repository_root: str | Path,
    registry_path: str | Path,
    provenance_root: str | Path,
    publication_id: str,
    accepted_at: str,
    operation: str,
    expected_main_sha: str | None = None,
    source_branch_ref: str | None = None,
    notify: bool = False,
) -> ApplyResult:
    """Apply a single target record after rechecking every acceptance digest.

    The function requires a clean Repository A worktree and an existing latest
    provenance manifest.  It never deletes or renames files.  All validation,
    drift checks, index rendering, and manifest serialization happen before
    the first write to the repository tree.
    """

    root = Path(repository_root).resolve()
    source_checkout_path = Path(source_checkout).resolve()
    provenance_path = Path(provenance_root).resolve()
    _assert_isolated_source_checkout(root, source_checkout_path)
    if provenance_path != root / "provenance":
        raise ApplyEngineError("provenance_root must be Repository A's provenance directory")
    registry = load_registry(registry_path)
    payload = _load_acceptance(acceptance_path)
    sources = {source["project_id"]: source for source in registry["sources"]}
    project_id = payload["project_id"]
    source = sources.get(project_id)
    if source is None:
        raise ApplyEngineError(f"project_id is not registered: {project_id}")
    _validate_payload_against_source(payload, source)

    _assert_clean_worktree(root)
    _assert_expected_head(root, expected_main_sha)
    source_root = source_checkout_path / PurePosixPath(source["source_directory"])
    source_commit = payload["source"]["commit_sha"]
    _assert_source_commit(source_checkout_path, source_commit, source_branch_ref)
    _assert_payload_inventory(payload, source_root, source)

    previous = _latest_manifest(Path(provenance_root), project_id)
    if previous["source"]["repository"] != payload["source"]["repository"]:
        raise ApplyEngineError("acceptance source repository differs from previous provenance")
    if previous["source"]["ref"] != payload["source"]["ref"]:
        raise ApplyEngineError("acceptance source ref differs from previous provenance")
    previous_acceptance = payload["previous_acceptance"]
    if not isinstance(previous_acceptance, Mapping):
        raise ApplyEngineError("acceptance.previous_acceptance must be an object")
    if (
        previous_acceptance.get("publication_id") != previous["publication_id"]
        or previous_acceptance.get("commit_sha") != previous["source"]["commit_sha"]
    ):
        raise ApplyEngineError("acceptance previous provenance does not match current provenance")

    destination = root / PurePosixPath(source["destination_directory"])
    current_published = _inventory_directory(destination, ignored_paths={"index.html"})
    try:
        assert_no_drift(previous, current_published)
    except ProvenanceDriftError as exc:
        raise ApplyEngineError(str(exc)) from exc

    # A drifted derived index is also unsafe: the new index must be based on a
    # known-good current manifest before the new manifest is introduced.
    try:
        from .index_generator import generate_indexes

        generate_indexes(root, check=True)
    except (OSError, ProvenanceError, ValueError) as exc:
        raise ApplyEngineError(f"current generated indexes are stale: {exc}") from exc

    target_basename = payload["target_basename"]
    metadata = _validated_payload_metadata(
        payload, project_id, target_basename, source_root, source
    )
    previous_records = {record["basename"]: record["metadata"] for record in previous["records"]}
    if operation == "create" and target_basename in previous_records:
        raise ApplyEngineError(f"create would overwrite existing record: {target_basename}")
    if operation == "update" and target_basename not in previous_records:
        raise ApplyEngineError(f"update target does not exist: {target_basename}")
    if operation not in {"create", "update"}:
        raise ApplyEngineError("apply engine only supports create and update")
    if metadata["publish"] is not True:
        raise ApplyEngineError("publish:false requires the audited withdrawal workflow")

    metadata_by_basename = dict(previous_records)
    metadata_by_basename[target_basename] = metadata

    with tempfile.TemporaryDirectory(prefix="sandbox-pages-apply-") as temp_dir:
        staged_destination = Path(temp_dir) / "destination"
        _copy_regular_tree(destination, staged_destination)
        for source_path in _target_public_paths(payload, source):
            relative = PurePosixPath(source_path)
            source_file = source_root / relative
            target_file = staged_destination / relative
            _copy_one_regular_file(source_file, target_file, source_path)

        if source["html_mode"] == "a_rendered":
            try:
                rendered_html = render_work_record(
                    source_root / "md" / f"{target_basename}.md",
                    metadata,
                    expected_project_id=project_id,
                )
            except RenderedRendererError as exc:
                raise ApplyEngineError(f"a_rendered renderer failed: {exc}") from exc
            (staged_destination / f"{target_basename}.html").write_text(
                rendered_html, encoding="utf-8"
            )

        final_published = _inventory_directory(staged_destination, ignored_paths={"index.html"})
        notification_target = notify and operation == "create"
        manifest = build_manifest(
            publication_id=publication_id,
            project_id=project_id,
            source_repository=payload["source"]["repository"],
            source_ref=payload["source"]["ref"],
            source_commit_sha=source_commit,
            public_base_path=payload["destination"]["public_base_path"],
            accepted_at=accepted_at,
            operation=operation,
            metadata_by_basename=metadata_by_basename,
            source_files=_payload_files(payload["inventory"]),
            published_files=final_published,
            notify=notification_target,
        )

        if _is_content_noop(previous, manifest):
            return ApplyResult(
                project_id=project_id,
                operation=operation,
                publication_id=publication_id,
                no_op=True,
                notify=False,
                changed_paths=(),
                manifest_path=None,
            )

        manifests = [item for item in load_current_manifests(Path(provenance_root)) if item["project_id"] != project_id]
        manifests.append(manifest)
        rendered_indexes = {
            Path("projects/index.html"): render_global_index(manifests),
            Path(source["destination_directory"]) / "index.html": render_project_index(manifest),
        }
        manifest_relative = Path("provenance") / project_id / f"{publication_id}.json"
        expected_paths = {
            str(PurePosixPath(source["destination_directory"]) / PurePosixPath(item.path))
            for item in final_published
        }
        expected_paths.update(str(path.as_posix()) for path in rendered_indexes)
        expected_paths.add(manifest_relative.as_posix())

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
    changed_paths = tuple(sorted(_git_status_paths(root)))
    return ApplyResult(
        project_id=project_id,
        operation=operation,
        publication_id=publication_id,
        no_op=False,
        notify=notification_target,
        changed_paths=changed_paths,
        manifest_path=manifest_relative.as_posix(),
    )


def apply_with_bounded_retry(
    *,
    initial_main_sha: str,
    current_main_sha: Callable[[], str],
    attempt: Callable[[str, int], ApplyResult],
    max_retries: int = 1,
) -> ApplyResult:
    """Retry preparation once when main advances before an apply attempt.

    ``attempt`` must prepare the working tree from the supplied latest SHA and
    pass that SHA to :func:`apply_verified_payload`.  The default cap is one
    retry; a second conflict fails instead of overwriting another project.
    """

    if max_retries < 0:
        raise ApplyEngineError("max_retries must not be negative")
    expected = initial_main_sha
    for retry in range(max_retries + 1):
        observed = current_main_sha()
        if observed != expected:
            if retry >= max_retries:
                raise ApplyConflictError("Repository A main advanced during apply preparation")
            expected = observed
            continue
        try:
            result = attempt(expected, retry)
        except ApplyConflictError:
            if retry >= max_retries:
                raise
            expected = current_main_sha()
            continue
        if current_main_sha() == expected:
            return result
        if retry >= max_retries:
            raise ApplyConflictError("Repository A main advanced after apply preparation")
        expected = current_main_sha()
    raise ApplyConflictError("apply retry limit exceeded")


def infer_operation(*, acceptance_path: str | Path, provenance_root: str | Path) -> str:
    """Infer create/update from the latest manifest without trusting source input."""

    payload = _load_acceptance(acceptance_path)
    previous = _latest_manifest(Path(provenance_root), payload["project_id"])
    basenames = {record["basename"] for record in previous["records"]}
    return "update" if payload["target_basename"] in basenames else "create"


def _load_acceptance(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ApplyEngineError(f"acceptance payload cannot be loaded: {path}") from exc
    if not isinstance(data, Mapping):
        raise ApplyEngineError("acceptance payload must be an object")
    unknown = sorted(set(data) - ACCEPTANCE_FIELDS)
    missing = sorted(ACCEPTANCE_FIELDS - set(data))
    if unknown or missing:
        details = []
        if unknown:
            details.append("unknown=" + ",".join(unknown))
        if missing:
            details.append("missing=" + ",".join(missing))
        raise ApplyEngineError("acceptance payload fields are invalid: " + "; ".join(details))
    if data["dry_run"] is not True or data["apply"] is not False:
        raise ApplyEngineError("payload must be produced by the read-only acceptance workflow")
    if not isinstance(data["enabled"], bool):
        raise ApplyEngineError("acceptance.enabled must be boolean")
    return dict(data)


def _validate_payload_against_source(payload: Mapping[str, Any], source: Mapping[str, Any]) -> None:
    if payload["project_id"] != source["project_id"]:
        raise ApplyEngineError("acceptance project_id does not match registry")
    source_payload = payload["source"]
    if not isinstance(source_payload, Mapping):
        raise ApplyEngineError("acceptance.source must be an object")
    if source_payload.get("repository") != source["source_repository"]:
        raise ApplyEngineError("acceptance source repository does not match registry")
    if source_payload.get("ref") != source["source_ref"]:
        raise ApplyEngineError("acceptance source ref does not match registry")
    commit_sha = source_payload.get("commit_sha")
    if not isinstance(commit_sha, str) or not REQUEST_COMMIT_SHA_RE.fullmatch(commit_sha):
        raise ApplyEngineError("acceptance source commit_sha must be a full lowercase SHA")
    target_basename = payload.get("target_basename")
    if not isinstance(target_basename, str) or not REQUEST_BASENAME_RE.fullmatch(target_basename):
        raise ApplyEngineError(
            "acceptance target_basename must match work_record_001 through work_record_999"
        )
    if not 1 <= int(target_basename.rsplit("_", 1)[1]) <= 999:
        raise ApplyEngineError("acceptance target_basename number must be between 001 and 999")
    destination = payload["destination"]
    if not isinstance(destination, Mapping):
        raise ApplyEngineError("acceptance.destination must be an object")
    if destination.get("directory") != source["destination_directory"]:
        raise ApplyEngineError("acceptance destination directory does not match registry")
    if destination.get("public_base_path") != source["public_base_path"]:
        raise ApplyEngineError("acceptance public base path does not match registry")
    if payload["generator_id"] != source["generator_id"] or payload["html_mode"] != source["html_mode"]:
        raise ApplyEngineError("acceptance generator or html mode does not match registry")
    if not isinstance(payload["validators"], Mapping) or any(value != "passed" for value in payload["validators"].values()):
        raise ApplyEngineError("acceptance validators must all be passed")
    if source["html_mode"] == "a_rendered" and payload["validators"].get("renderer") != "passed":
        raise ApplyEngineError("a_rendered acceptance must pass the A-owned renderer")


def _assert_payload_inventory(payload: Mapping[str, Any], source_root: Path, source: Mapping[str, Any]) -> None:
    try:
        accepted = validate_source_tree(source_root, source)
    except AcceptanceFileError as exc:
        raise ApplyEngineError(f"source inventory validation failed: {exc}") from exc
    actual = _file_map(accepted.files)
    expected = _file_map(_payload_files(payload["inventory"]))
    if actual != expected:
        raise ApplyEngineError("acceptance inventory digest no longer matches source checkout")
    target_paths = {item["path"] for item in payload["target_inventory"]}
    expected_target = _selected_paths(source, payload["target_basename"])
    if target_paths != expected_target:
        raise ApplyEngineError("acceptance target inventory is outside the registered target set")
    actual_target = {path: actual[path] for path in target_paths if path in actual}
    expected_payload_target = _file_map(_payload_files(payload["target_inventory"]))
    if actual_target != expected_payload_target:
        raise ApplyEngineError("acceptance target digest no longer matches source checkout")


def _validated_payload_metadata(
    payload: Mapping[str, Any],
    project_id: str,
    basename: str,
    source_root: Path,
    source: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        metadata = validate_metadata(
            payload["metadata"], expected_basename=basename, registered_project_ids={project_id}
        )
    except MetadataSchemaError as exc:
        raise ApplyEngineError(f"acceptance metadata is invalid: {exc}") from exc
    metadata_relative = PurePosixPath(source["metadata_directory"]).relative_to(
        PurePosixPath(source["source_directory"])
    )
    try:
        actual = load_metadata(
            source_root / metadata_relative / f"{basename}.yml",
            expected_basename=basename,
            registered_project_ids={project_id},
        )
    except (OSError, MetadataSchemaError) as exc:
        raise ApplyEngineError(f"source metadata cannot be revalidated: {basename}") from exc
    if actual != metadata:
        raise ApplyEngineError("acceptance metadata no longer matches source checkout")
    return metadata


def _selected_paths(source: Mapping[str, Any], basename: str) -> set[str]:
    source_directory = PurePosixPath(source["source_directory"])
    metadata_directory = PurePosixPath(source["metadata_directory"])
    relative_metadata = metadata_directory.relative_to(source_directory)
    paths = set(source["support_files"])
    paths.add(f"md/{basename}.md")
    paths.add((relative_metadata / f"{basename}.yml").as_posix())
    if source["html_mode"] == "source_html":
        paths.add(f"{basename}.html")
    return paths


def _target_public_paths(payload: Mapping[str, Any], source: Mapping[str, Any]) -> tuple[str, ...]:
    metadata_directory = PurePosixPath(source["metadata_directory"]).relative_to(
        PurePosixPath(source["source_directory"])
    )
    metadata_prefix = metadata_directory.as_posix() + "/"
    paths = []
    for item in payload["target_inventory"]:
        path = item["path"]
        if path == metadata_prefix or path.startswith(metadata_prefix):
            if path == (metadata_directory / f"{payload['target_basename']}.yml").as_posix():
                continue
            raise ApplyEngineError(f"target path is outside metadata contract: {path}")
        paths.append(path)
    return tuple(sorted(paths))


def _payload_files(items: Any) -> tuple[AcceptedFile, ...]:
    if not isinstance(items, list):
        raise ApplyEngineError("acceptance inventory must be an array")
    result = []
    for item in items:
        if not isinstance(item, Mapping) or set(item) != FILE_FIELDS:
            raise ApplyEngineError("acceptance inventory entries are invalid")
        path = item["path"]
        if not isinstance(path, str) or not path or "\\" in path:
            raise ApplyEngineError("acceptance inventory path is invalid")
        posix = PurePosixPath(path)
        if posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts):
            raise ApplyEngineError(f"acceptance inventory path is not normalized: {path}")
        size = item["size_bytes"]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ApplyEngineError(f"acceptance inventory size is invalid: {path}")
        digest = item["sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or digest != digest.lower() or any(character not in "0123456789abcdef" for character in digest):
            raise ApplyEngineError(f"acceptance inventory digest is invalid: {path}")
        result.append(AcceptedFile(posix.as_posix(), size, digest))
    if len({item.path for item in result}) != len(result):
        raise ApplyEngineError("acceptance inventory contains duplicate paths")
    return tuple(sorted(result, key=lambda item: item.path))


def _latest_manifest(provenance_root: Path, project_id: str) -> dict[str, Any]:
    project_root = provenance_root / project_id
    if not project_root.is_dir():
        raise ApplyEngineError(f"provenance directory does not exist: {project_root}")
    candidates = []
    for path in sorted(project_root.glob("*.json")):
        try:
            manifest = load_manifest(path)
        except ProvenanceError as exc:
            raise ApplyEngineError(f"invalid previous provenance: {path}") from exc
        if manifest["project_id"] != project_id:
            raise ApplyEngineError(f"provenance project_id does not match directory: {path}")
        candidates.append((manifest["accepted_at"], manifest["publication_id"], manifest))
    if not candidates:
        raise ApplyEngineError(f"no previous provenance manifest: {project_id}")
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def _is_content_noop(previous: Mapping[str, Any], planned: Mapping[str, Any]) -> bool:
    comparable = ("project_id", "source", "public_base_path", "source_files", "published_files", "records")
    return all(previous[field] == planned[field] for field in comparable)


def _inventory_directory(root: Path, *, ignored_paths: set[str] | None = None) -> list[AcceptedFile]:
    if not root.exists():
        return []
    if not root.is_dir() or root.is_symlink():
        raise ApplyEngineError(f"published root must be a regular directory: {root}")
    ignored = ignored_paths or set()
    files = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative in ignored:
            continue
        if path.is_symlink():
            raise ApplyEngineError(f"published tree contains a symlink: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ApplyEngineError(f"published tree contains a non-regular file: {relative}")
        files.append(AcceptedFile(relative, path.stat().st_size, _sha256(path)))
    return files


def _file_map(files: tuple[AcceptedFile, ...] | list[AcceptedFile]) -> dict[str, tuple[int, str]]:
    return {item.path: (item.size_bytes, item.sha256) for item in files}


def _copy_regular_tree(source: Path, destination: Path) -> None:
    if source.exists():
        if not source.is_dir() or source.is_symlink():
            raise ApplyEngineError(f"tree must be a regular directory: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_symlink():
            raise ApplyEngineError(f"symlink is not accepted: {relative.as_posix()}")
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        else:
            raise ApplyEngineError(f"non-regular file is not accepted: {relative.as_posix()}")


def _copy_one_regular_file(source: Path, destination: Path, relative: str) -> None:
    if not source.is_file() or source.is_symlink():
        raise ApplyEngineError(f"source target is not a regular file: {relative}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_clean_worktree(root: Path) -> None:
    paths = _git_status_paths(root)
    if paths:
        raise ApplyEngineError("Repository A worktree must be clean before apply: " + ", ".join(sorted(paths)))


def _assert_isolated_source_checkout(root: Path, source_checkout: Path) -> None:
    """Reject source inputs that overlap Repository A's worktree.

    A same-repository source is valid only when it is a separate checkout. An
    overlapping path could make source files look like publish outputs and
    would defeat the apply engine's bounded-write contract.
    """

    try:
        source_checkout.relative_to(root)
        overlaps = True
    except ValueError:
        overlaps = False
    if not overlaps:
        try:
            root.relative_to(source_checkout)
            overlaps = True
        except ValueError:
            pass
    if overlaps:
        raise ApplyEngineError("source checkout must be isolated from Repository A worktree")


def _assert_expected_head(root: Path, expected_main_sha: str | None) -> None:
    if expected_main_sha is None:
        return
    if len(expected_main_sha) != 40 or expected_main_sha != expected_main_sha.lower() or any(character not in "0123456789abcdef" for character in expected_main_sha):
        raise ApplyEngineError("expected_main_sha must be a full lowercase SHA")
    actual = _git(root, "rev-parse", "HEAD")
    if actual != expected_main_sha:
        raise ApplyConflictError("Repository A main is no longer the expected commit")


def _assert_source_commit(checkout: Path, commit_sha: str, branch_ref: str | None) -> None:
    actual = _git(checkout, "rev-parse", "HEAD")
    if actual != commit_sha:
        raise ApplyEngineError("source checkout does not match acceptance commit")
    if branch_ref:
        branch_tip = _git(checkout, "rev-parse", "--verify", f"{branch_ref}^{{commit}}")
        completed = subprocess.run(
            ["git", "-C", str(checkout), "merge-base", "--is-ancestor", commit_sha, branch_tip],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise ApplyEngineError("source acceptance commit is not an ancestor of the registered branch")


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args], check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        raise ApplyEngineError(f"git verification failed: {completed.stderr.strip() or 'unknown error'}")
    return completed.stdout.strip()


def _git_status_paths(root: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ApplyEngineError(f"git status failed: {completed.stderr.strip() or 'unknown error'}")
    paths = set()
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            raise ApplyEngineError("git status returned an invalid entry")
        path = line[3:]
        if " -> " in path:
            raise ApplyEngineError("automatic rename handling is not allowed")
        paths.add(PurePosixPath(path).as_posix())
    return paths


def _assert_allowed_worktree_changes(root: Path, expected_paths: set[str]) -> None:
    actual = _git_status_paths(root)
    unexpected = sorted(actual - expected_paths)
    if unexpected:
        raise ApplyEngineError("apply created changes outside the allowed scope: " + ", ".join(unexpected))


def _verify_applied_state(root: Path, destination: Path, manifest: Mapping[str, Any], destination_directory: str) -> None:
    loaded = load_manifest(root / "provenance" / str(manifest["project_id"]) / f"{manifest['publication_id']}.json")
    if loaded != manifest:
        raise ApplyEngineError("written provenance manifest does not match the planned manifest")
    current = _inventory_directory(destination, ignored_paths={"index.html"})
    report = inspect_drift(loaded, current)
    if not report.clean:
        raise ApplyEngineError("applied project files differ from new provenance manifest")
    del destination_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--provenance-root", type=Path, default=None)
    parser.add_argument("--publication-id", required=True)
    parser.add_argument("--accepted-at", required=True)
    parser.add_argument(
        "--operation", choices=("auto", "create", "update"), default="auto"
    )
    parser.add_argument("--expected-main-sha")
    parser.add_argument("--source-branch-ref")
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    registry = args.registry or root / "config/sources.json"
    provenance = args.provenance_root or root / "provenance"
    try:
        operation = args.operation
        if operation == "auto":
            operation = infer_operation(
                acceptance_path=args.acceptance,
                provenance_root=provenance,
            )
        result = apply_verified_payload(
            acceptance_path=args.acceptance,
            source_checkout=args.source_checkout,
            repository_root=root,
            registry_path=registry,
            provenance_root=provenance,
            publication_id=args.publication_id,
            accepted_at=args.accepted_at,
            operation=operation,
            expected_main_sha=args.expected_main_sha,
            source_branch_ref=args.source_branch_ref,
            notify=args.notify,
        )
    except (ApplyEngineError, OSError, ProvenanceError, SourceRegistryError) as exc:
        parser.exit(1, f"apply failed: {exc}\n")
    print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
