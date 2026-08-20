"""Generate deterministic project and global progress indexes from provenance."""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Mapping

from scripts.publish.provenance import load_manifest


PROJECT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
RECORD_BASENAME_RE = re.compile(r"work_record_(\d{3})")


class IndexGeneratorError(ValueError):
    """Raised when provenance cannot produce a safe deterministic index."""


@dataclass(frozen=True)
class IndexRecord:
    project_id: str
    basename: str
    title: str
    record_date: str
    tags: tuple[str, ...]

    @property
    def number(self) -> int:
        match = RECORD_BASENAME_RE.fullmatch(self.basename)
        if match is None:
            raise IndexGeneratorError(f"invalid record basename: {self.basename}")
        return int(match.group(1))


def load_current_manifests(provenance_root: Path) -> list[dict]:
    """Load the latest validated manifest for each project directory."""

    if not provenance_root.is_dir():
        raise IndexGeneratorError(f"provenance directory does not exist: {provenance_root}")
    manifests: list[dict] = []
    for project_directory in sorted(path for path in provenance_root.iterdir() if path.is_dir()):
        candidates = []
        for path in sorted(project_directory.glob("*.json")):
            manifest = load_manifest(str(path))
            if manifest["project_id"] != project_directory.name:
                raise IndexGeneratorError(
                    f"manifest project_id does not match directory: {path}"
                )
            candidates.append((manifest["accepted_at"], manifest["publication_id"], manifest))
        if candidates:
            manifests.append(max(candidates, key=lambda item: (item[0], item[1]))[2])
    if not manifests:
        raise IndexGeneratorError("no provenance manifests found")
    project_ids = [manifest["project_id"] for manifest in manifests]
    if len(project_ids) != len(set(project_ids)):
        raise IndexGeneratorError("duplicate project manifest")
    return sorted(manifests, key=lambda item: item["project_id"])


def records_from_manifest(manifest: Mapping[str, object]) -> list[IndexRecord]:
    project_id = str(manifest["project_id"])
    if PROJECT_ID_RE.fullmatch(project_id) is None:
        raise IndexGeneratorError(f"project_id is not URL-safe: {project_id}")
    records = []
    for record in manifest["records"]:  # type: ignore[index]
        metadata = record["metadata"]
        if metadata["publish"] is not True:
            continue
        basename = str(record["basename"])
        if RECORD_BASENAME_RE.fullmatch(basename) is None:
            raise IndexGeneratorError(f"invalid record basename: {basename}")
        record_date = str(metadata["date"])
        date.fromisoformat(record_date)
        records.append(
            IndexRecord(
                project_id=project_id,
                basename=basename,
                title=str(metadata["title"]),
                record_date=record_date,
                tags=tuple(str(tag) for tag in metadata["tags"]),
            )
        )
    return _sort_records(records)


def render_project_index(manifest: Mapping[str, object]) -> str:
    project_id = str(manifest["project_id"])
    records = records_from_manifest(manifest)
    return _render_document(
        title=f"{project_id} — 作業記録",
        stylesheet="../progress-index.css",
        eyebrow="Project progress",
        heading=project_id,
        summary=f"公開中の作業記録 {len(records)}件",
        navigation=(
            ("全project", "../index.html"),
            ("サイトトップ", "../../index.html"),
        ),
        content=_render_record_list(records, heading_level=2, href_prefix="./"),
    )


def render_global_index(manifests: Iterable[Mapping[str, object]]) -> str:
    manifest_list = sorted(manifests, key=lambda item: str(item["project_id"]))
    all_records = _sort_records(
        record
        for manifest in manifest_list
        for record in records_from_manifest(manifest)
    )
    project_links = "".join(
        '<li><a href="./{project}/index.html">{project}</a><span>{count}件</span></li>'.format(
            project=html.escape(str(manifest["project_id"]), quote=True),
            count=len(records_from_manifest(manifest)),
        )
        for manifest in manifest_list
    )
    content = (
        '<section class="project-summary" aria-labelledby="project-list-heading">'
        '<h2 id="project-list-heading">Projects</h2>'
        f'<ul class="project-list">{project_links}</ul>'
        '</section>'
        '<section class="records" aria-labelledby="latest-records-heading">'
        '<h2 id="latest-records-heading">すべての作業記録</h2>'
        f'{_render_record_list(all_records, heading_level=3, href_prefix="./", global_page=True)}'
        '</section>'
    )
    return _render_document(
        title="Project progress — Portfolio Lab",
        stylesheet="./progress-index.css",
        eyebrow="Portfolio Lab",
        heading="Project progress",
        summary=f"{len(manifest_list)} project・公開中の作業記録 {len(all_records)}件",
        navigation=(("サイトトップ", "../index.html"),),
        content=content,
    )


def generate_indexes(repository_root: Path, check: bool = False) -> tuple[Path, ...]:
    manifests = load_current_manifests(repository_root / "provenance")
    outputs: dict[Path, str] = {
        repository_root / "projects" / "index.html": render_global_index(manifests)
    }
    for manifest in manifests:
        project_id = str(manifest["project_id"])
        outputs[repository_root / "projects" / project_id / "index.html"] = render_project_index(manifest)

    stale = []
    for path, content in outputs.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if stale:
        relative = ", ".join(str(path.relative_to(repository_root)) for path in stale)
        raise IndexGeneratorError(f"generated indexes are stale: {relative}")
    return tuple(sorted(outputs))


def _sort_records(records: Iterable[IndexRecord]) -> list[IndexRecord]:
    return sorted(
        records,
        key=lambda item: (-date.fromisoformat(item.record_date).toordinal(), item.project_id.casefold(), -item.number),
    )


def _render_record_list(
    records: Iterable[IndexRecord],
    *,
    heading_level: int,
    href_prefix: str,
    global_page: bool = False,
) -> str:
    items = []
    for record in records:
        href = (
            f"{href_prefix}{record.project_id}/{record.basename}.html"
            if global_page
            else f"{href_prefix}{record.basename}.html"
        )
        tags = "".join(f"<li>{html.escape(tag)}</li>" for tag in record.tags)
        tags_markup = f'<ul class="tag-list" aria-label="Tags">{tags}</ul>' if tags else ""
        project_markup = (
            f'<span class="record-project">{html.escape(record.project_id)}</span>'
            if global_page
            else ""
        )
        items.append(
            '<li class="record-item"><article>'
            '<p class="record-meta">'
            f'<time datetime="{record.record_date}">{record.record_date}</time>'
            f'{project_markup}<span>{record.basename}</span></p>'
            f'<h{heading_level}><a href="{html.escape(href, quote=True)}">'
            f'{html.escape(record.title)}</a></h{heading_level}>'
            f'{tags_markup}</article></li>'
        )
    return f'<ol class="record-list">{"".join(items)}</ol>'


def _render_document(
    *,
    title: str,
    stylesheet: str,
    eyebrow: str,
    heading: str,
    summary: str,
    navigation: tuple[tuple[str, str], ...],
    content: str,
) -> str:
    nav_links = "".join(
        f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for label, href in navigation
    )
    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{html.escape(stylesheet, quote=True)}">
</head>
<body>
  <a class="skip-link" href="#content">本文へ移動</a>
  <header class="page-header">
    <div class="page-header__inner">
      <p class="eyebrow">{html.escape(eyebrow)}</p>
      <h1>{html.escape(heading)}</h1>
      <p class="summary">{html.escape(summary)}</p>
      <nav aria-label="ページリンク">{nav_links}</nav>
    </div>
  </header>
  <main id="content">
    {content}
  </main>
  <footer><p>Metadata source: validated provenance manifest</p></footer>
</body>
</html>
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        outputs = generate_indexes(args.root.resolve(), check=args.check)
    except (IndexGeneratorError, ValueError) as exc:
        parser.exit(1, f"index generation failed: {exc}\n")
    action = "checked" if args.check else "generated"
    for path in outputs:
        print(f"{action}: {path.relative_to(args.root.resolve())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
