#!/usr/bin/env python3
"""Render numbered work-record Markdown files as deterministic static HTML."""

from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_DIR = ROOT / "work-records" / "md"
OUTPUT_DIR = ROOT / "work-records"
RECORD_RE = re.compile(r"^work_record_(\d{3})\.md$")
DATE_RE = re.compile(r"^作成日:\s*(\d{4}-\d{2}-\d{2})\s*$")
HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|(\d+)\.)\s+(.+?)\s*$")
TABLE_SEPARATOR_RE = re.compile(
    r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$"
)
ALLOWED_EXTERNAL_SCHEMES = {"http", "https"}
SECTION_LABELS = {
    "概要": "対象",
    "対象と入力": "前提",
    "進行ログ（バトンタッチ順）": "実行",
    "適用した役割": "担当",
    "実施内容": "作業",
    "主要な判断": "根拠",
    "自動公開機構の現在地": "状況",
    "次のセッションの開始地点": "継続",
    "PR・マージ記録": "履歴",
    "追記": "経過",
    "追加対応": "追補",
    "最終結果": "確認",
}


def normalize_href(value: str, source_path: Path) -> str:
    """Validate a Markdown link and rebase relative paths for the HTML output."""

    parsed = urlsplit(value)
    scheme = parsed.scheme.lower()
    if scheme:
        if scheme not in ALLOWED_EXTERNAL_SCHEMES:
            raise ValueError(f"{source_path}: unsupported link scheme: {scheme}")
        return value
    if parsed.netloc or value.startswith("//"):
        raise ValueError(f"{source_path}: protocol-relative links are not allowed")
    if not parsed.path:
        return value

    target = (source_path.parent / unquote(parsed.path)).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError as error:
        raise ValueError(f"{source_path}: link escapes repository: {value}") from error

    relative = Path(os.path.relpath(target, OUTPUT_DIR)).as_posix()
    encoded_path = quote(relative, safe="/:@-._~")
    return urlunsplit(("", "", encoded_path, parsed.query, parsed.fragment))


def inline_markdown(value: str, source_path: Path) -> str:
    """Render the inline Markdown used by the work records."""

    placeholders: list[str] = []

    def hold(value_to_hold: str) -> str:
        placeholders.append(value_to_hold)
        return f"\x00{len(placeholders) - 1}\x00"

    def render_link(match: re.Match[str]) -> str:
        label = inline_markdown(match.group(1), source_path)
        href = normalize_href(match.group(2), source_path)
        return hold(f'<a href="{html.escape(href, quote=True)}">{label}</a>')

    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", render_link, value)
    value = html.escape(value, quote=False)
    value = re.sub(
        r"`([^`]+)`",
        lambda match: hold(f"<code>{match.group(1)}</code>"),
        value,
    )
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)

    for index, replacement in enumerate(placeholders):
        value = value.replace(f"\x00{index}\x00", replacement)
    return value


def document_details(lines: list[str], path: Path) -> tuple[str, str, str]:
    match = RECORD_RE.fullmatch(path.name)
    if match is None:
        raise ValueError(f"{path}: expected work_record_###.md")
    number = match.group(1)

    if not lines:
        raise ValueError(f"{path}: file is empty")
    heading_match = HEADING_RE.fullmatch(lines[0])
    expected_prefix = f"作業記録 {number}: "
    if (
        heading_match is None
        or len(heading_match.group(1)) != 1
        or not heading_match.group(2).startswith(expected_prefix)
    ):
        raise ValueError(
            f"{path}: first line must be '# 作業記録 {number}: <内容>'"
        )
    title = heading_match.group(2)[len(expected_prefix) :].strip()
    if not title:
        raise ValueError(f"{path}: title is empty")

    date = next(
        (
            date_match.group(1)
            for line in lines[1:]
            if (date_match := DATE_RE.fullmatch(line.strip()))
        ),
        None,
    )
    if date is None:
        raise ValueError(f"{path}: '作成日: YYYY-MM-DD' not found")
    return number, title, date


def content_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    removed_title = False
    removed_date = False
    for line in lines:
        if not removed_title and HEADING_RE.fullmatch(line):
            removed_title = True
            continue
        if removed_title and not removed_date and DATE_RE.fullmatch(line.strip()):
            removed_date = True
            continue
        result.append(line)
    return result


def table_cells(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    return [cell.strip() for cell in value.split("|")]


def render_table(
    lines: list[str], index: int, source_path: Path
) -> tuple[str, int]:
    header = table_cells(lines[index])
    index += 2
    rows: list[list[str]] = []
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        rows.append(table_cells(lines[index]))
        index += 1

    output = ["<table>", "<thead><tr>"]
    output.extend(
        f'<th scope="col">{inline_markdown(cell, source_path)}</th>'
        for cell in header
    )
    output.append("</tr></thead><tbody>")
    for row in rows:
        output.append("<tr>")
        output.extend(
            f"<td>{inline_markdown(cell, source_path)}</td>" for cell in row
        )
        output.append("</tr>")
    output.append("</tbody></table>")
    return "".join(output), index


def render_list(
    lines: list[str], index: int, source_path: Path
) -> tuple[str, int]:
    first_match = LIST_RE.fullmatch(lines[index])
    assert first_match is not None
    base_indent = len(first_match.group(1).replace("\t", "    "))
    tag = "ol" if first_match.group(3) else "ul"
    output = [f"<{tag}>"]

    while index < len(lines):
        match = LIST_RE.fullmatch(lines[index])
        if match is None:
            break
        indent = len(match.group(1).replace("\t", "    "))
        if indent < base_indent:
            break
        if indent > base_indent:
            nested, index = render_list(lines, index, source_path)
            if output[-1].endswith("</li>"):
                output[-1] = output[-1][:-5] + nested + "</li>"
            else:
                output.append(nested)
            continue

        current_tag = "ol" if match.group(3) else "ul"
        if current_tag != tag:
            break
        content = match.group(4)
        if content.startswith(("[x] ", "[X] ")):
            content = f"完了：{content[4:]}"
        elif content.startswith("[ ] "):
            content = f"未完了：{content[4:]}"
        output.append(f"<li>{inline_markdown(content, source_path)}</li>")
        index += 1

    output.append(f"</{tag}>")
    return "".join(output), index


def render_ordered_list(
    lines: list[str], index: int, source_path: Path
) -> tuple[str, int]:
    """Keep top-level ordered items with the list content that follows them."""

    output = ["<ol>"]
    while index < len(lines):
        match = LIST_RE.fullmatch(lines[index])
        if match is None or match.group(3) is None or match.group(1).strip():
            break
        content = match.group(4)
        index += 1
        child_lines: list[str] = []
        while index < len(lines):
            if not lines[index].strip():
                lookahead = index
                while lookahead < len(lines) and not lines[lookahead].strip():
                    lookahead += 1
                if lookahead >= len(lines):
                    index = lookahead
                    break
                following_list = LIST_RE.fullmatch(lines[lookahead])
                if following_list and following_list.group(3) is None:
                    child_lines.extend(lines[index:lookahead])
                    index = lookahead
                    continue
                index = lookahead
                break
            next_list = LIST_RE.fullmatch(lines[index])
            next_heading = HEADING_RE.fullmatch(lines[index])
            if next_list and next_list.group(3) and not next_list.group(1).strip():
                break
            if next_heading and len(next_heading.group(1)) <= 3:
                break
            child_lines.append(lines[index])
            index += 1
        child_content = (
            render_content(child_lines, source_path)
            if any(line.strip() for line in child_lines)
            else ""
        )
        output.append(
            f"<li>{inline_markdown(content, source_path)}{child_content}</li>"
        )
    output.append("</ol>")
    return "".join(output), index


def render_content(lines: list[str], source_path: Path) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(part.strip() for part in paragraph)
            output.append(f"<p>{inline_markdown(text, source_path)}</p>")
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
            while index < len(lines) and not lines[index].strip().startswith(
                "```"
            ):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            language_class = (
                f' class="language-{html.escape(language, quote=True)}"'
                if language
                else ""
            )
            code = html.escape("\n".join(code_lines))
            output.append(f"<pre><code{language_class}>{code}</code></pre>")
            continue
        heading_match = HEADING_RE.fullmatch(line)
        if heading_match and len(heading_match.group(1)) >= 3:
            flush_paragraph()
            level = min(len(heading_match.group(1)), 4)
            heading = inline_markdown(heading_match.group(2), source_path)
            output.append(f"<h{level}>{heading}</h{level}>")
            index += 1
            continue
        if (
            "|" in stripped
            and index + 1 < len(lines)
            and TABLE_SEPARATOR_RE.fullmatch(lines[index + 1])
        ):
            flush_paragraph()
            table, index = render_table(lines, index, source_path)
            output.append(table)
            continue
        if LIST_RE.fullmatch(line):
            flush_paragraph()
            match = LIST_RE.fullmatch(line)
            assert match is not None
            if match.group(3) and not match.group(1).strip():
                rendered, index = render_ordered_list(lines, index, source_path)
            else:
                rendered, index = render_list(lines, index, source_path)
            output.append(rendered)
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip()[1:].strip())
                index += 1
            quote_text = inline_markdown(" ".join(quote_lines), source_path)
            output.append(f"<blockquote><p>{quote_text}</p></blockquote>")
            continue
        if stripped == "---":
            flush_paragraph()
            output.append("<hr>")
            index += 1
            continue
        paragraph.append(line)
        index += 1

    flush_paragraph()
    return "\n".join(output)


def section_label(heading: str) -> str:
    for prefix, label in SECTION_LABELS.items():
        if heading.startswith(prefix):
            return label
    return "記録"


def render_sections(lines: list[str], source_path: Path) -> str:
    output: list[str] = []
    preamble: list[str] = []
    index = 0
    while index < len(lines):
        heading_match = HEADING_RE.fullmatch(lines[index])
        if heading_match and len(heading_match.group(1)) == 2:
            break
        preamble.append(lines[index])
        index += 1

    section_number = 0
    if any(line.strip() for line in preamble):
        section_number += 1
        section_id = f"section-{section_number:02d}"
        output.append(
            '<section class="record-section" '
            f'aria-labelledby="{section_id}">'
            '<div class="section-intro">'
            f'<p class="section-label">{section_number:02d}　補足</p>'
            f'<h2 id="{section_id}">記録前提</h2>'
            "</div>"
            f'<div class="section-content">{render_content(preamble, source_path)}</div>'
            "</section>"
        )

    index = len(preamble)
    while index < len(lines):
        heading_match = HEADING_RE.fullmatch(lines[index])
        if not heading_match or len(heading_match.group(1)) != 2:
            index += 1
            continue
        heading = heading_match.group(2)
        section_number += 1
        section_id = f"section-{section_number:02d}"
        index += 1
        section_lines: list[str] = []
        while index < len(lines):
            next_heading = HEADING_RE.fullmatch(lines[index])
            if next_heading and len(next_heading.group(1)) <= 2:
                break
            section_lines.append(lines[index])
            index += 1
        output.append(
            '<section class="record-section" '
            f'aria-labelledby="{section_id}">'
            '<div class="section-intro">'
            f'<p class="section-label">{section_number:02d}　'
            f'{html.escape(section_label(heading))}</p>'
            f'<h2 id="{section_id}">{inline_markdown(heading, source_path)}</h2>'
            "</div>"
            f'<div class="section-content">{render_content(section_lines, source_path)}</div>'
            "</section>"
        )
    return "\n".join(output)


def render_document(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    number, title, date = document_details(lines, path)
    sections = render_sections(content_lines(lines), path)
    if not sections:
        sections = (
            '<section class="record-section" aria-labelledby="section-01">'
            '<div class="section-intro">'
            '<p class="section-label">01　記録</p>'
            '<h2 id="section-01">本文なし</h2>'
            "</div>"
            '<div class="section-content"><p>この作業記録には本文がありません。</p></div>'
            "</section>"
        )

    document = f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>{html.escape(title)} — 作業記録 {number}</title>
    <link rel="stylesheet" href="work_record.css">
  </head>
  <body>
    <div class="shell">
      <header class="topbar">
        <a class="wordmark" href="../index.html">SANDBOX PAGES</a>
        <nav class="toplinks" aria-label="関連文書">
          <a href="README.md">運用ルール</a>
          <a href="design.md">デザインガイド</a>
          <a href="md/{html.escape(path.name, quote=True)}">Markdown原本</a>
        </nav>
      </header>
      <main>
        <header class="record-header">
          <p class="kicker">作業記録 {number} ・ <time datetime="{date}">{date}</time></p>
          <h1>{html.escape(title)}</h1>
          <dl class="record-meta">
            <div><dt>原本</dt><dd><code>md/{html.escape(path.name)}</code></dd></div>
            <div><dt>形式</dt><dd>Markdown原本から生成した静的HTML</dd></div>
          </dl>
        </header>
        {sections}
      </main>
      <footer>
        <span>SANDBOX PAGES · 作業記録 {number}</span>
        <span><a href="md/{html.escape(path.name, quote=True)}">Markdown原本</a></span>
      </footer>
    </div>
  </body>
</html>
"""
    return "\n".join(line.rstrip() for line in document.splitlines()) + "\n"


def markdown_paths() -> list[Path]:
    return sorted(
        path
        for path in MARKDOWN_DIR.glob("*.md")
        if RECORD_RE.fullmatch(path.name)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when generated HTML is missing or differs",
    )
    args = parser.parse_args()

    paths = markdown_paths()
    if not paths:
        print("No work-record Markdown files found.")
        return 1

    failures: list[str] = []
    for path in paths:
        try:
            document = render_document(path)
        except ValueError as error:
            failures.append(str(error))
            continue
        output_path = OUTPUT_DIR / f"{path.stem}.html"
        if args.check:
            if not output_path.is_file():
                failures.append(f"{output_path}: generated HTML is missing")
            elif output_path.read_text(encoding="utf-8") != document:
                failures.append(f"{output_path}: generated HTML is stale")
        else:
            output_path.write_text(document, encoding="utf-8")
            print(f"generated {output_path.relative_to(ROOT)}")

    if failures:
        print("Work-record HTML generation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    if args.check:
        print(f"Work-record HTML is current for {len(paths)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
