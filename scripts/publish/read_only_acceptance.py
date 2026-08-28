"""Run the read-only source acceptance dry-run for Repository A.

The workflow owns the checkout and never executes code from the source
repository.  This module only reads the checked-out files and runs validators
owned by Repository A.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .acceptance_files import AcceptanceFileError, validate_source_tree
from .content_safety import ContentSafetyError, validate_source_html_tree
from .metadata_schema import MetadataSchemaError, load_metadata
from .provenance import ProvenanceError, load_manifest
from .rendered_renderer import RenderedRendererError, render_work_record
from .source_registry import SourceRegistryError, load_registry


COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
TARGET_BASENAME_RE = re.compile(r"^work_record_[0-9]{3}$")


class ReadOnlyAcceptanceError(ValueError):
    """Raised when a source cannot pass the read-only acceptance contract."""


def resolve_source(
    *,
    registry_path: str | Path,
    project_id: str,
    source_commit_sha: str,
    target_basename: str,
    allow_enabled: bool = False,
) -> dict[str, Any]:
    """Resolve and validate workflow inputs using only A's registry."""

    _validate_inputs(project_id, source_commit_sha, target_basename)
    try:
        registry = load_registry(registry_path)
    except SourceRegistryError as exc:
        raise ReadOnlyAcceptanceError(str(exc)) from exc
    sources = {source["project_id"]: source for source in registry["sources"]}
    if project_id not in sources:
        raise ReadOnlyAcceptanceError(f"project_id is not registered: {project_id}")
    source = dict(sources[project_id])
    # The default remains the Issue #17 dry-run gate.  The full publish
    # workflow opts in explicitly after the source has passed activation.
    if source["enabled"] is not False and not allow_enabled:
        raise ReadOnlyAcceptanceError(
            f"read-only acceptance requires enabled:false: {project_id}"
        )
    return source


def run_acceptance(
    *,
    registry_path: str | Path,
    project_id: str,
    source_commit_sha: str,
    target_basename: str,
    source_checkout: str | Path,
    branch_ref: str,
    provenance_root: str | Path,
    output_dir: str | Path,
    allow_enabled: bool = False,
) -> dict[str, Any]:
    """Validate a fixed source commit and write deterministic dry-run output."""

    source = resolve_source(
        registry_path=registry_path,
        project_id=project_id,
        source_commit_sha=source_commit_sha,
        target_basename=target_basename,
        allow_enabled=allow_enabled,
    )
    checkout = Path(source_checkout)
    source_root = checkout / Path(source["source_directory"])
    if not source_root.is_dir():
        raise ReadOnlyAcceptanceError(
            f"registered source directory does not exist: {source['source_directory']}"
        )
    _verify_fixed_commit(checkout, source_commit_sha, branch_ref)
    previous_manifest = _load_previous_manifest(provenance_root, project_id)
    previous_source = previous_manifest["source"]
    if (
        previous_source["repository"] != source["source_repository"]
        or previous_source["ref"] != source["source_ref"]
    ):
        raise ReadOnlyAcceptanceError(
            "previous acceptance source does not match the registered repository/ref"
        )
    previous_sha = previous_source["commit_sha"]
    if not COMMIT_SHA_RE.fullmatch(previous_sha):
        raise ReadOnlyAcceptanceError("previous acceptance SHA must be a full lowercase SHA")
    if not _is_ancestor(checkout, previous_sha, source_commit_sha):
        raise ReadOnlyAcceptanceError(
            "source commit is older than the previous accepted source commit"
        )

    try:
        accepted = validate_source_tree(source_root, source)
    except AcceptanceFileError as exc:
        raise ReadOnlyAcceptanceError(f"A-03 acceptance file validation failed: {exc}") from exc

    validator_results = {"acceptance_files": "passed"}
    if source["html_mode"] == "source_html":
        try:
            validate_source_html_tree(source_root, source)
        except ContentSafetyError as exc:
            raise ReadOnlyAcceptanceError(f"A-04 content safety validation failed: {exc}") from exc
        validator_results["content_safety"] = "passed"

    metadata_path = source_root / _metadata_relative_path(source, target_basename)
    try:
        metadata = load_metadata(
            metadata_path,
            expected_basename=target_basename,
            registered_project_ids={project_id},
        )
    except MetadataSchemaError as exc:
        raise ReadOnlyAcceptanceError(f"A-02 metadata validation failed: {exc}") from exc
    validator_results["metadata"] = "passed"

    if source["html_mode"] == "a_rendered":
        try:
            render_work_record(
                source_root / "md" / f"{target_basename}.md",
                metadata,
                expected_project_id=project_id,
            )
        except RenderedRendererError as exc:
            raise ReadOnlyAcceptanceError(f"A-04 renderer validation failed: {exc}") from exc
        validator_results["renderer"] = "passed"

    if target_basename not in accepted.record_basenames:
        raise ReadOnlyAcceptanceError(
            f"target basename is not present in accepted source: {target_basename}"
        )
    selected_paths = _selected_paths(source, target_basename)
    inventory = [
        {
            "path": item.path,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
        }
        for item in accepted.files
    ]
    target_inventory = [item for item in inventory if item["path"] in selected_paths]
    if set(item["path"] for item in target_inventory) != selected_paths:
        missing = sorted(selected_paths - {item["path"] for item in target_inventory})
        raise ReadOnlyAcceptanceError(
            "target file set is incomplete: " + ", ".join(missing)
        )

    result = {
        "dry_run": True,
        "apply": False,
        "enabled": source["enabled"],
        "project_id": project_id,
        "source": {
            "repository": source["source_repository"],
            "ref": source["source_ref"],
            "commit_sha": source_commit_sha,
        },
        "previous_acceptance": {
            "publication_id": previous_manifest["publication_id"],
            "commit_sha": previous_sha,
        },
        "destination": {
            "directory": source["destination_directory"],
            "public_base_path": source["public_base_path"],
        },
        "generator_id": source["generator_id"],
        "target_basename": target_basename,
        "html_mode": source["html_mode"],
        "inventory": inventory,
        "target_inventory": target_inventory,
        "metadata": metadata,
        "validators": validator_results,
    }
    output_path = Path(output_dir) / "acceptance.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def _validate_inputs(project_id: str, source_commit_sha: str, target_basename: str) -> None:
    if not isinstance(project_id, str) or not project_id:
        raise ReadOnlyAcceptanceError("project_id is required")
    if not COMMIT_SHA_RE.fullmatch(source_commit_sha):
        raise ReadOnlyAcceptanceError("source_commit_sha must be a full lowercase SHA")
    if not TARGET_BASENAME_RE.fullmatch(target_basename):
        raise ReadOnlyAcceptanceError(
            "target_basename must match work_record_001 through work_record_999"
        )
    number = int(target_basename.rsplit("_", 1)[1])
    if not 1 <= number <= 999:
        raise ReadOnlyAcceptanceError("target_basename number must be between 001 and 999")


def _verify_fixed_commit(checkout: Path, source_commit_sha: str, branch_ref: str) -> None:
    if not branch_ref.startswith(("refs/remotes/", "refs/heads/")):
        raise ReadOnlyAcceptanceError("branch_ref must be a branch ref")
    commit = _git(checkout, "rev-parse", "--verify", f"{source_commit_sha}^{{commit}}")
    branch_tip = _git(checkout, "rev-parse", "--verify", f"{branch_ref}^{{commit}}")
    if commit.lower() != source_commit_sha:
        raise ReadOnlyAcceptanceError("checked out commit does not match source_commit_sha")
    if not _is_ancestor(checkout, source_commit_sha, branch_tip):
        raise ReadOnlyAcceptanceError(
            "source commit is not an ancestor of the registered source branch"
        )


def _is_ancestor(checkout: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(checkout), "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def _load_previous_manifest(provenance_root: str | Path, project_id: str) -> dict[str, Any]:
    project_root = Path(provenance_root) / project_id
    if not project_root.is_dir():
        raise ReadOnlyAcceptanceError(
            f"provenance directory does not exist: {project_root}"
        )
    candidates = []
    for path in sorted(project_root.glob("*.json")):
        try:
            manifest = load_manifest(path)
        except ProvenanceError as exc:
            raise ReadOnlyAcceptanceError(f"invalid previous provenance: {path}") from exc
        if manifest["project_id"] != project_id:
            raise ReadOnlyAcceptanceError(
                f"provenance project_id does not match directory: {path}"
            )
        candidates.append((manifest["accepted_at"], manifest["publication_id"], manifest))
    if not candidates:
        raise ReadOnlyAcceptanceError(f"no previous provenance manifest: {project_id}")
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def _git(checkout: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(checkout), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ReadOnlyAcceptanceError(
            f"source git verification failed: {completed.stderr.strip() or 'unknown error'}"
        )
    return completed.stdout.strip()


def _metadata_relative_path(source: Mapping[str, Any], basename: str) -> str:
    relative_directory = PurePosixPath(source["metadata_directory"]).relative_to(
        PurePosixPath(source["source_directory"])
    )
    return (relative_directory / f"{basename}.yml").as_posix()


def _selected_paths(source: Mapping[str, Any], basename: str) -> set[str]:
    metadata_path = _metadata_relative_path(source, basename)
    paths = set(source["support_files"])
    paths.add(f"md/{basename}.md")
    paths.add(metadata_path)
    if source["html_mode"] == "source_html":
        paths.add(f"{basename}.html")
    return paths


def _write_resolved_outputs(source: Mapping[str, Any]) -> None:
    output_file = Path(os.environ["GITHUB_OUTPUT"])
    values = {
        "source_repository": source["source_repository"],
        "source_ref": source["source_ref"],
        "source_directory": source["source_directory"],
        "source_branch": source["source_ref"].removeprefix("refs/heads/"),
    }
    with output_file.open("a", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--registry", type=Path, required=True)
    resolve_parser.add_argument("--project-id", required=True)
    resolve_parser.add_argument("--source-commit-sha", required=True)
    resolve_parser.add_argument("--target-basename", required=True)
    resolve_parser.add_argument("--allow-enabled", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--registry", type=Path, required=True)
    run_parser.add_argument("--project-id", required=True)
    run_parser.add_argument("--source-commit-sha", required=True)
    run_parser.add_argument("--target-basename", required=True)
    run_parser.add_argument("--source-checkout", type=Path, required=True)
    run_parser.add_argument("--branch-ref", required=True)
    run_parser.add_argument("--provenance-root", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--allow-enabled", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "resolve":
            source = resolve_source(
                registry_path=args.registry,
                project_id=args.project_id,
                source_commit_sha=args.source_commit_sha,
                target_basename=args.target_basename,
                allow_enabled=args.allow_enabled,
            )
            _write_resolved_outputs(source)
            return 0
        result = run_acceptance(
            registry_path=args.registry,
            project_id=args.project_id,
            source_commit_sha=args.source_commit_sha,
            target_basename=args.target_basename,
            source_checkout=args.source_checkout,
            branch_ref=args.branch_ref,
            provenance_root=args.provenance_root,
            output_dir=args.output_dir,
            allow_enabled=args.allow_enabled,
        )
    except (OSError, ReadOnlyAcceptanceError) as exc:
        parser.exit(1, f"read-only acceptance failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
