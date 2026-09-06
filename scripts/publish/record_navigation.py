"""Build deterministic navigation for published work-record pages."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, Mapping


RECORD_BASENAME_RE = re.compile(r"^work_record_(\d{3})$")


@dataclass(frozen=True)
class NavigationTarget:
    basename: str
    title: str
    href: str


@dataclass(frozen=True)
class RecordNavigation:
    project_id: str
    basename: str
    project_index_href: str
    global_index_href: str
    position: int
    total: int
    previous: NavigationTarget | None
    next: NavigationTarget | None


def build_record_navigation(
    manifests: Iterable[Mapping[str, Any]],
    *,
    project_id: str,
    basename: str,
) -> RecordNavigation:
    """Build page-local links from validated manifest records only."""

    grouped: dict[str, list[tuple[str, str, str]]] = {}
    for manifest in manifests:
        manifest_project = str(manifest["project_id"])
        records = grouped.setdefault(manifest_project, [])
        for record in manifest["records"]:
            if record["metadata"]["publish"] is not True:
                continue
            record_basename = str(record["basename"])
            match = RECORD_BASENAME_RE.fullmatch(record_basename)
            if match is None:
                raise ValueError(f"invalid published record basename: {record_basename}")
            records.append(
                (
                    record_basename,
                    str(record["metadata"]["title"]),
                    str(record["metadata"]["date"]),
                )
            )

    records = grouped.get(project_id, [])
    records.sort(key=lambda item: (-date.fromisoformat(item[2]).toordinal(), -int(item[0][-3:])))
    current_index = next(
        (index for index, item in enumerate(records) if item[0] == basename),
        None,
    )
    if current_index is None:
        raise ValueError(f"published record is not in the project manifest: {project_id}/{basename}")

    def target(index: int) -> NavigationTarget | None:
        if not 0 <= index < len(records):
            return None
        record_basename, title, _record_date = records[index]
        return NavigationTarget(record_basename, title, f"{record_basename}.html")

    return RecordNavigation(
        project_id=project_id,
        basename=basename,
        project_index_href="index.html",
        global_index_href="../index.html",
        position=current_index + 1,
        total=len(records),
        previous=target(current_index - 1),
        next=target(current_index + 1),
    )


def render_record_navigation(navigation: RecordNavigation) -> str:
    """Render a compact, keyboard-reachable navigation block."""

    def pager(label: str, target: NavigationTarget | None, direction: str) -> str:
        if target is None:
            return (
                f'<span class="record-navigation__pager-link record-navigation__pager-link--disabled" '
                f'aria-disabled="true">{label}</span>'
            )
        arrow = "←" if direction == "previous" else "→"
        return (
            f'<a class="record-navigation__pager-link" href="{html.escape(target.href, quote=True)}" '
            f'aria-label="{html.escape(label + "：" + target.title, quote=True)}">'
            f'{arrow} {label}<span>{html.escape(target.basename)}</span></a>'
        )

    return (
        '<nav class="record-navigation" aria-label="作業記録のナビゲーション">'
        '<div class="record-navigation__context">'
        f'<a href="{html.escape(navigation.project_index_href, quote=True)}">このproject</a>'
        f'<a href="{html.escape(navigation.global_index_href, quote=True)}">全project</a>'
        '</div>'
        '<div class="record-navigation__pager">'
        f'{pager("前の記録", navigation.previous, "previous")}'
        f'<span class="record-navigation__position">{navigation.position} / {navigation.total}</span>'
        f'{pager("次の記録", navigation.next, "next")}'
        '</div>'
        '</nav>'
    )


def decorate_record_html(document: str, navigation: RecordNavigation) -> str:
    """Add navigation to source_html output without changing record content."""

    if 'class="record-navigation"' in document:
        return document
    marker = render_record_navigation(navigation)
    match = re.search(r"(?m)^(?P<indent>[ \t]*)<main(?:\s|>)", document)
    if match is None:
        raise ValueError("record HTML does not contain a main element")
    indent = match.group("indent")
    return document[: match.start()] + f"{indent}{marker}\n" + document[match.start() :]


def update_record_navigation(document: str, navigation: RecordNavigation) -> str:
    """Replace only an existing navigation block, preserving record content."""

    without_navigation = re.sub(
        r'(?m)^[ \t]*<nav class="record-navigation" aria-label="作業記録のナビゲーション">.*?</nav>[ \t]*(?:\n|$)',
        "",
        document,
        count=1,
        flags=re.DOTALL,
    )
    return decorate_record_html(without_navigation, navigation)
