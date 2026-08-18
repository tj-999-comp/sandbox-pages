#!/usr/bin/env python3
"""Validate local work-record names, headers, links, and generated HTML."""

from __future__ import annotations

import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import convert_work_records_to_html as converter


ROOT = Path(__file__).resolve().parents[2]
WORK_RECORDS_DIR = ROOT / "work-records"
MARKDOWN_DIR = WORK_RECORDS_DIR / "md"
RECORD_RE = re.compile(r"^work_record_(\d{3})\.md$")
HTML_RE = re.compile(r"^work_record_(\d{3})\.html$")
HEADING_RE = re.compile(r"^# 作業記録 (\d{3}): .+$")
DATE_RE = re.compile(r"^作成日:\s*(\d{4}-\d{2}-\d{2})\s*$")
OLD_REFERENCE_RE = re.compile(
    r"(?:Issues/|Issue_(?:\d{3}|Template)\.md)"
)
REQUIRED_FILES = ("README.md", "design.md", "work_record.css")


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value is not None:
                self.links.append(value)


def main() -> int:
    violations: list[str] = []

    if (ROOT / "Issues").exists():
        violations.append("Issues/: old work-record directory still exists")
    if not WORK_RECORDS_DIR.is_dir():
        print("work-records/ directory not found.")
        return 1

    for name in REQUIRED_FILES:
        if not (WORK_RECORDS_DIR / name).is_file():
            violations.append(f"work-records/{name}: required file not found")

    root_markdown = sorted(WORK_RECORDS_DIR.glob("*.md"))
    allowed_root_markdown = {"README.md", "design.md"}
    for path in root_markdown:
        if path.name not in allowed_root_markdown:
            violations.append(
                f"{path.relative_to(ROOT)}: only README.md and design.md "
                "may be placed directly under work-records/"
            )

    markdown_numbers: set[str] = set()
    if not MARKDOWN_DIR.is_dir():
        violations.append("work-records/md/: directory not found")
    else:
        for path in sorted(MARKDOWN_DIR.glob("*.md")):
            name_match = RECORD_RE.fullmatch(path.name)
            if name_match is None:
                violations.append(
                    f"{path.relative_to(ROOT)}: expected work_record_###.md"
                )
                continue
            number = name_match.group(1)
            if not 1 <= int(number) <= 999:
                violations.append(
                    f"{path.relative_to(ROOT)}: record number must be 001-999"
                )
            if number in markdown_numbers:
                violations.append(
                    f"{path.relative_to(ROOT)}: duplicate record number {number}"
                )
            markdown_numbers.add(number)

            lines = path.read_text(encoding="utf-8").splitlines()
            if not lines:
                violations.append(f"{path.relative_to(ROOT)}: file is empty")
                continue
            heading_match = HEADING_RE.fullmatch(lines[0])
            if heading_match is None:
                violations.append(
                    f"{path.relative_to(ROOT)}: expected first line "
                    f"'# 作業記録 {number}: <内容>'"
                )
            elif heading_match.group(1) != number:
                violations.append(
                    f"{path.relative_to(ROOT)}: filename and heading numbers differ"
                )

            date_line = next(
                (
                    date_match.group(1)
                    for line in lines[1:]
                    if (date_match := DATE_RE.fullmatch(line.strip()))
                ),
                None,
            )
            if date_line is None:
                violations.append(
                    f"{path.relative_to(ROOT)}: '作成日: YYYY-MM-DD' not found"
                )
            else:
                try:
                    date.fromisoformat(date_line)
                except ValueError:
                    violations.append(
                        f"{path.relative_to(ROOT)}: invalid date {date_line}"
                    )

            output_path = WORK_RECORDS_DIR / f"{path.stem}.html"
            if not output_path.is_file():
                violations.append(
                    f"{path.relative_to(ROOT)}: corresponding HTML not found"
                )
            else:
                try:
                    expected_html = converter.render_document(path)
                except ValueError as error:
                    violations.append(str(error))
                else:
                    if output_path.read_text(encoding="utf-8") != expected_html:
                        violations.append(
                            f"{output_path.relative_to(ROOT)}: generated HTML is stale"
                        )

    html_numbers: set[str] = set()
    for path in sorted(WORK_RECORDS_DIR.glob("work_record_*.html")):
        name_match = HTML_RE.fullmatch(path.name)
        if name_match is None:
            violations.append(
                f"{path.relative_to(ROOT)}: expected work_record_###.html"
            )
            continue
        number = name_match.group(1)
        html_numbers.add(number)
        markdown_path = MARKDOWN_DIR / f"work_record_{number}.md"
        if not markdown_path.is_file():
            violations.append(
                f"{path.relative_to(ROOT)}: corresponding Markdown not found"
            )
        html_text = path.read_text(encoding="utf-8")
        if '<link rel="stylesheet" href="work_record.css">' not in html_text:
            violations.append(
                f"{path.relative_to(ROOT)}: work_record.css link not found"
            )
        collector = LinkCollector()
        collector.feed(html_text)
        for href in collector.links:
            parsed = urlsplit(href)
            if parsed.scheme in {"http", "https"} or not parsed.path:
                continue
            if parsed.scheme or parsed.netloc:
                violations.append(
                    f"{path.relative_to(ROOT)}: unsupported link target {href}"
                )
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                violations.append(
                    f"{path.relative_to(ROOT)}: link escapes repository: {href}"
                )
                continue
            if not target.is_file():
                violations.append(
                    f"{path.relative_to(ROOT)}: link target not found: {href}"
                )

    if markdown_numbers != html_numbers:
        missing_html = sorted(markdown_numbers - html_numbers)
        missing_markdown = sorted(html_numbers - markdown_numbers)
        if missing_html:
            violations.append(
                "missing HTML for record numbers: " + ", ".join(missing_html)
            )
        if missing_markdown:
            violations.append(
                "missing Markdown for record numbers: "
                + ", ".join(missing_markdown)
            )

    # Historical records may name the old path while explaining the migration.
    # Only current operating instructions must be free from the retired scheme.
    scan_paths = [ROOT / "AGENTS.md", ROOT / "README.md"]
    for path in scan_paths:
        if not path.is_file():
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if OLD_REFERENCE_RE.search(line):
                violations.append(
                    f"{path.relative_to(ROOT)}:{line_number}: old work-record "
                    "path or filename remains"
                )

    if violations:
        print("Work-record rule violations detected:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print(
        "Work-record filename, content, and generated HTML validation passed "
        f"for {len(markdown_numbers)} records."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
