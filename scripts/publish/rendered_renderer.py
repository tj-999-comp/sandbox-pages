"""Render md-only work records into deterministic, safe static HTML."""

from __future__ import annotations

import html
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from .metadata_schema import MetadataSchemaError, validate_metadata


GENERATOR_ID = "a-rendered-work-record-v1"
RECORD_RE = re.compile(r"^work_record_(?P<number>[0-9]{3})\.md$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|(\d+)\.)\s+(.+?)\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")
DATE_RE = re.compile(r"^作成日:\s*\d{4}-\d{2}-\d{2}\s*$")


class RenderedRendererError(ValueError):
    """Raised when a work record cannot be rendered by the A-owned renderer."""


def render_work_record(
    markdown_path: str | Path,
    metadata: Mapping[str, Any],
    *,
    stylesheet: str = "../progress-index.css",
    expected_project_id: str | None = None,
) -> str:
    """Render one validated Markdown record using only deterministic inputs."""

    source = Path(markdown_path)
    match = RECORD_RE.fullmatch(source.name)
    if match is None:
        raise RenderedRendererError(f"expected work_record_###.md: {source}")
    basename = source.stem
    try:
        normalized = validate_metadata(
            metadata,
            expected_basename=basename,
            registered_project_ids={expected_project_id or str(metadata.get("project_id", ""))},
        )
    except MetadataSchemaError as exc:
        raise RenderedRendererError(f"metadata is invalid for {basename}: {exc}") from exc
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise RenderedRendererError(f"Markdown cannot be read: {source}") from exc

    body = _render_record_sections(_body_lines(lines), source)
    number = match.group("number")
    title = html.escape(normalized["title"])
    project_id = html.escape(normalized["project_id"])
    record_date = html.escape(normalized["date"], quote=True)
    stylesheet = _normalize_stylesheet(stylesheet)

    return f'''<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>{title} — 作業記録 {number}</title>
    <link rel="stylesheet" href="{html.escape(stylesheet, quote=True)}">
  </head>
  <body class="record-page">
    <div class="shell">
      <header class="topbar">
        <span class="wordmark">{project_id}</span>
      </header>
      <main>
        <header class="record-header">
          <p class="kicker">作業記録 {number} ・ {record_date}</p>
          <h1>{title}</h1>
          <dl class="record-meta">
            <div><dt>原本</dt><dd><code>md/{html.escape(basename)}.md</code></dd></div>
            <div><dt>状態</dt><dd>記録本文をHTML化</dd></div>
          </dl>
        </header>
        {body}
      </main>
      <footer>
        <span>{project_id} · 作業記録 {number}</span>
        <span><a href="md/{html.escape(basename)}.md">Markdown原本</a></span>
      </footer>
    </div>
  </body>
</html>
'''


def _body_lines(lines: list[str]) -> list[str]:
    if not lines:
        raise RenderedRendererError("Markdown is empty")
    first = HEADING_RE.fullmatch(lines[0])
    if first is None or len(first.group(1)) != 1:
        raise RenderedRendererError("first Markdown line must be an H1")
    body = lines[1:]
    while body and not body[0].strip():
        body.pop(0)
    if body and DATE_RE.fullmatch(body[0].strip()):
        body = body[1:]
    return body


def _render_record_sections(lines: list[str], source: Path) -> str:
    """Wrap H2-led Markdown sections in the shared record-page structure."""

    groups: list[tuple[str, list[str]]] = []
    preamble: list[str] = []
    current: tuple[str, list[str]] | None = None
    for line in lines:
        heading = HEADING_RE.fullmatch(line)
        if heading and len(heading.group(1)) == 2:
            current = (heading.group(2), [])
            groups.append(current)
        elif current is None:
            preamble.append(line)
        else:
            current[1].append(line)

    if not groups:
        groups = [("本文", preamble)]
    elif any(line.strip() for line in preamble):
        groups[0][1][:0] = preamble

    sections: list[str] = []
    for index, (heading, section_lines) in enumerate(groups, start=1):
        rendered_heading = _inline(heading, source)
        section_body = _render_markdown(section_lines, source)
        sections.append(
            f'<section class="record-section"><div class="section-intro">'
            f'<p class="section-label">{index:02d}　{rendered_heading}</p>'
            f'<h2>{rendered_heading}</h2></div>'
            f'<div class="section-content">{section_body}</div></section>'
        )
    return "\n".join(sections)


def _render_markdown(lines: list[str], source: Path) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(part.strip() for part in paragraph)
            output.append(f"<p>{_inline(text, source)}</p>")
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            language = stripped[3:].strip()
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            class_attr = f' class="language-{html.escape(language, quote=True)}"' if language else ""
            output.append(f"<pre><code{class_attr}>{html.escape(chr(10).join(code_lines))}</code></pre>")
            continue
        heading = HEADING_RE.fullmatch(line)
        if heading and len(heading.group(1)) >= 2:
            flush_paragraph()
            level = min(len(heading.group(1)), 4)
            output.append(f"<h{level}>{_inline(heading.group(2), source)}</h{level}>")
            index += 1
            continue
        if "|" in stripped and index + 1 < len(lines) and TABLE_SEPARATOR_RE.fullmatch(lines[index + 1]):
            flush_paragraph()
            table, index = _render_table(lines, index, source)
            output.append(table)
            continue
        if LIST_RE.fullmatch(line):
            flush_paragraph()
            rendered, index = _render_list(lines, index, source)
            output.append(rendered)
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip()[1:].strip())
                index += 1
            output.append(f"<blockquote><p>{_inline(' '.join(quote_lines), source)}</p></blockquote>")
            continue
        if stripped == "---":
            flush_paragraph()
            output.append("<hr>")
            index += 1
            continue
        paragraph.append(line)
        index += 1
    flush_paragraph()
    return "\n".join(output) or "<p>本文はありません。</p>"


def _render_table(lines: list[str], index: int, source: Path) -> tuple[str, int]:
    header = _table_cells(lines[index])
    index += 2
    rows: list[list[str]] = []
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        rows.append(_table_cells(lines[index]))
        index += 1
    output = ["<table><thead><tr>"]
    output.extend(f'<th scope="col">{_inline(cell, source)}</th>' for cell in header)
    output.append("</tr></thead><tbody>")
    for row in rows:
        output.append("<tr>")
        output.extend(f"<td>{_inline(cell, source)}</td>" for cell in row)
        output.append("</tr>")
    output.append("</tbody></table>")
    return "".join(output), index


def _render_list(lines: list[str], index: int, source: Path) -> tuple[str, int]:
    first = LIST_RE.fullmatch(lines[index])
    assert first is not None
    base_indent = len(first.group(1).replace("\t", "    "))
    tag = "ol" if first.group(3) else "ul"
    output = [f"<{tag}>"]
    while index < len(lines):
        match = LIST_RE.fullmatch(lines[index])
        if match is None:
            break
        indent = len(match.group(1).replace("\t", "    "))
        if indent < base_indent or indent > base_indent or ("ol" if match.group(3) else "ul") != tag:
            break
        content = match.group(4)
        if content.startswith(("[x] ", "[X] ")):
            content = f"完了：{content[4:]}"
        elif content.startswith("[ ] "):
            content = f"未完了：{content[4:]}"
        output.append(f"<li>{_inline(content, source)}</li>")
        index += 1
    output.append(f"</{tag}>")
    return "".join(output), index


def _table_cells(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    return [cell.strip() for cell in value.split("|")]


def _inline(value: str, source: Path) -> str:
    placeholders: list[str] = []

    def hold(fragment: str) -> str:
        placeholders.append(fragment)
        return f"\x00{len(placeholders) - 1}\x00"

    def link(match: re.Match[str]) -> str:
        label = _inline(match.group(1), source)
        href = _normalize_href(match.group(2), source)
        return hold(f'<a href="{html.escape(href, quote=True)}">{label}</a>')

    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, value)
    value = html.escape(value, quote=False)
    value = re.sub(r"`([^`]+)`", lambda match: hold(f"<code>{match.group(1)}</code>"), value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    for index, fragment in enumerate(placeholders):
        value = value.replace(f"\x00{index}\x00", fragment)
    return value


def _normalize_href(value: str, source: Path) -> str:
    if any(ord(char) < 0x20 for char in value) or "\\" in value or value.startswith("//"):
        raise RenderedRendererError(f"unsafe Markdown link in {source}: {value}")
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme.lower() != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise RenderedRendererError(f"unsafe Markdown link in {source}: {value}")
        return urlunsplit(("https", parsed.netloc, parsed.path, parsed.query, parsed.fragment))
    if parsed.netloc or parsed.path.startswith("/"):
        raise RenderedRendererError(f"unsafe Markdown link in {source}: {value}")
    if not parsed.path:
        if not parsed.fragment:
            raise RenderedRendererError(f"Markdown link has no target in {source}")
        return f"#{quote(unquote(parsed.fragment), safe='-._~')}"
    path = PurePosixPath(unquote(parsed.path))
    if any(part in {"", ".", ".."} for part in path.parts):
        raise RenderedRendererError(f"Markdown link escapes its project in {source}: {value}")
    encoded = quote(path.as_posix(), safe="/@-._~")
    fragment = quote(unquote(parsed.fragment), safe="-._~") if parsed.fragment else ""
    return urlunsplit(("", "", encoded, parsed.query, fragment))


def _normalize_stylesheet(value: str) -> str:
    if value == "../progress-index.css":
        return value
    if not value or "\\" in value or value.startswith(("/", "//")):
        raise RenderedRendererError("stylesheet must be a project-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts) or path.suffix != ".css":
        raise RenderedRendererError("stylesheet must be a normalized project-relative CSS path")
    return path.as_posix()
