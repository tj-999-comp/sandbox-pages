"""Allowlist validation for source HTML, CSS, URLs, and local dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from urllib.parse import unquote, urlsplit

from .acceptance_files import AcceptanceFileError, validate_source_tree


ALLOWED_TAGS = frozenset(
    {
        "a", "aside", "body", "code", "dd", "div", "dl", "dt", "footer", "h1", "h2", "h3",
        "h4", "head", "header", "html", "hr", "li", "link", "main", "meta", "ol", "p", "pre",
        "section", "span", "strong", "table", "tbody", "td", "th", "thead", "time", "title",
        "tr", "ul", "blockquote",
    }
)
VOID_TAGS = frozenset({"link", "meta"})
GLOBAL_ATTRS = frozenset({"aria-labelledby", "class", "id", "lang"})
TAG_ATTRS = {
    "a": frozenset({"href"}),
    "link": frozenset({"href", "rel"}),
    "meta": frozenset({"charset", "content", "name"}),
    "th": frozenset({"scope"}),
    "time": frozenset({"datetime"}),
}
ALLOWED_META_NAMES = frozenset({"color-scheme", "viewport"})
ALLOWED_CSS_AT_RULES = frozenset({"media"})
ALLOWED_CSS_PROPERTIES = frozenset(
    {
        "align-items", "background", "border-bottom", "border-collapse", "border-left",
        "border-top", "box-sizing", "break-inside", "color", "display", "flex-direction",
        "flex-wrap", "font-family", "font-size", "font-weight", "gap", "grid-template-columns",
        "justify-content", "letter-spacing", "line-height", "margin", "margin-bottom",
        "margin-left", "margin-top", "max-width", "min-height", "min-width", "overflow-wrap",
        "overflow-x", "padding", "padding-bottom", "padding-left", "padding-top", "scroll-behavior",
        "text-align", "text-decoration", "text-decoration-thickness", "text-underline-offset",
        "vertical-align", "white-space", "width",
    }
)
CSS_URL_RE = re.compile(r"url\(\s*(?P<quote>['\"]?)(?P<value>.*?)(?P=quote)\s*\)", re.IGNORECASE)
CSS_AT_RULE_RE = re.compile(r"@([A-Za-z-]+)")
CSS_DANGEROUS_RE = re.compile(
    r"(?:expression\s*\(|javascript\s*:|(?<![-\w])behavior\s*:|-moz-binding\s*:)",
    re.IGNORECASE,
)


class ContentSafetyError(ValueError):
    """Raised when HTML, CSS, a URL, or a local dependency is unsafe."""


@dataclass(frozen=True)
class SafeHtmlDocument:
    """Validated HTML path and the local CSS dependencies it references."""

    path: str
    css_paths: tuple[str, ...]


def validate_source_html_tree(source_root: str | Path, source: Mapping[str, Any]) -> tuple[SafeHtmlDocument, ...]:
    """Validate all accepted source HTML files and their local dependencies."""

    try:
        accepted = validate_source_tree(source_root, source)
    except AcceptanceFileError as exc:
        raise ContentSafetyError(f"source file acceptance failed: {exc}") from exc
    root = Path(source_root)
    support_files = source.get("support_files", [])
    if not isinstance(support_files, list):
        raise ContentSafetyError("source support_files must be a list")
    for support_file in support_files:
        _resolve_local_path(root, support_file, current_relative="")
    documents = []
    for item in accepted.files:
        if not item.path.endswith(".html"):
            continue
        documents.append(validate_html_file(root, item.path))
    if source.get("html_mode") == "source_html" and not documents:
        raise ContentSafetyError("source_html requires at least one HTML document")
    return tuple(sorted(documents, key=lambda document: document.path))


def validate_html_file(source_root: str | Path, relative_path: str) -> SafeHtmlDocument:
    """Validate one HTML document and verify every local dependency exists."""

    root = Path(source_root)
    html_path = _resolve_local_path(root, relative_path, current_relative="")
    if html_path.suffix.lower() != ".html":
        raise ContentSafetyError(f"HTML path must use .html: {relative_path}")
    try:
        text = html_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ContentSafetyError(f"HTML must be UTF-8: {relative_path}") from exc
    parser = _SafeHtmlParser(root, relative_path)
    parser.feed(text)
    parser.close()
    parser.finish()
    for css_path in parser.css_paths:
        validate_css_file(root, css_path)
    return SafeHtmlDocument(relative_path, tuple(sorted(parser.css_paths)))


def validate_css_file(source_root: str | Path, relative_path: str) -> None:
    """Validate one CSS file using a small, conservative declaration parser."""

    root = Path(source_root)
    css_path = _resolve_local_path(root, relative_path, current_relative="")
    if css_path.suffix.lower() != ".css":
        raise ContentSafetyError(f"stylesheet must use .css: {relative_path}")
    try:
        text = css_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ContentSafetyError(f"CSS must be UTF-8: {relative_path}") from exc
    cleaned = _strip_css_comments(text)
    if CSS_DANGEROUS_RE.search(cleaned):
        raise ContentSafetyError(f"dangerous CSS syntax: {relative_path}")
    if re.search(r"@import\b|@namespace\b|@charset\b", cleaned, re.IGNORECASE):
        raise ContentSafetyError(f"unsupported CSS at-rule: {relative_path}")
    for match in CSS_AT_RULE_RE.finditer(cleaned):
        if match.group(1).lower() not in ALLOWED_CSS_AT_RULES:
            raise ContentSafetyError(f"unsupported CSS at-rule: @{match.group(1)}")
    _validate_css_blocks(cleaned, root, relative_path)


class _SafeHtmlParser(HTMLParser):
    def __init__(self, source_root: Path, html_relative_path: str):
        super().__init__(convert_charrefs=False)
        self.source_root = source_root
        self.html_relative_path = html_relative_path
        self.stack: list[str] = []
        self.css_paths: set[str] = set()
        self.seen_html = False
        self.seen_head = False
        self.seen_body = False
        self.seen_doctype = False

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower() != "doctype html" or self.seen_doctype:
            raise ContentSafetyError("only one <!DOCTYPE html> declaration is allowed")
        self.seen_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, self_closing=True)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            raise ContentSafetyError(f"mismatched HTML end tag: {tag}")
        self.stack.pop()

    def finish(self) -> None:
        if self.stack:
            raise ContentSafetyError(f"unclosed HTML element: {self.stack[-1]}")
        if not self.seen_html or not self.seen_head or not self.seen_body:
            raise ContentSafetyError("HTML must contain html, head, and body elements")

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], *, self_closing: bool) -> None:
        if tag not in ALLOWED_TAGS:
            raise ContentSafetyError(f"HTML element is not allowed: <{tag}>")
        if self_closing and tag not in VOID_TAGS:
            raise ContentSafetyError(f"non-void HTML element cannot be self-closed: <{tag} />")
        if tag in {"html", "head", "body"} and tag in self.stack:
            raise ContentSafetyError(f"duplicate HTML structural element: <{tag}>")
        if tag == "html":
            if self.stack or self.seen_html:
                raise ContentSafetyError("html must be the document root")
            self.seen_html = True
        elif tag == "head":
            if not self.seen_html or self.stack != ["html"] or self.seen_head:
                raise ContentSafetyError("head is not in the expected position")
            self.seen_head = True
        elif tag == "body":
            if not self.seen_head or self.stack != ["html"] or self.seen_body:
                raise ContentSafetyError("body is not in the expected position")
            self.seen_body = True
        self._validate_attrs(tag, attrs)
        if tag == "link":
            self._validate_link(attrs)
        if tag == "meta":
            self._validate_meta(attrs)
        if not self_closing and tag not in VOID_TAGS:
            self.stack.append(tag)

    def _validate_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        seen: set[str] = set()
        allowed = GLOBAL_ATTRS | TAG_ATTRS.get(tag, frozenset())
        for name, value in attrs:
            if name in seen:
                raise ContentSafetyError(f"duplicate HTML attribute: {name}")
            seen.add(name)
            if name.startswith("on") or name not in allowed:
                raise ContentSafetyError(f"HTML attribute is not allowed: {name}")
            if value is None:
                raise ContentSafetyError(f"boolean HTML attribute is not allowed: {name}")
            if name == "href":
                local = _validate_url(value, allow_external_https=(tag == "a"))
                if local is not None:
                    _resolve_local_path(self.source_root, local, current_relative=self.html_relative_path)

    def _validate_link(self, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("rel", "").lower() != "stylesheet":
            raise ContentSafetyError("only stylesheet links are allowed")
        href = values.get("href")
        if href is None:
            raise ContentSafetyError("stylesheet link requires href")
        local = _validate_url(href, allow_external_https=False)
        if local is None:
            raise ContentSafetyError("stylesheet must be a local project file")
        resolved = _resolve_local_path(self.source_root, local, current_relative=self.html_relative_path)
        self.css_paths.add(resolved.relative_to(self.source_root).as_posix())

    def _validate_meta(self, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if "http-equiv" in values:
            raise ContentSafetyError("http-equiv and meta refresh are not allowed")
        if "charset" in values and values["charset"].lower() != "utf-8":
            raise ContentSafetyError("only UTF-8 charset is allowed")
        if "name" in values and values["name"].lower() not in ALLOWED_META_NAMES:
            raise ContentSafetyError(f"meta name is not allowed: {values['name']}")


def _validate_url(value: str, *, allow_external_https: bool) -> str | None:
    if not isinstance(value, str) or not value or any(ord(char) < 0x20 for char in value):
        raise ContentSafetyError("URL is empty or contains control characters")
    if "\\" in value or value.startswith("//"):
        raise ContentSafetyError(f"URL is not a safe project URL: {value}")
    decoded = unquote(value)
    if "\\" in decoded or any(part in {"..", "."} for part in decoded.split("/")):
        raise ContentSafetyError(f"URL contains traversal or normalization: {value}")
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme.lower() != "https" or not parsed.netloc or not allow_external_https:
            raise ContentSafetyError(f"URL scheme is not allowed: {value}")
        if parsed.username or parsed.password:
            raise ContentSafetyError("HTTPS URL credentials are not allowed")
        return None
    if parsed.netloc or parsed.path.startswith("/"):
        raise ContentSafetyError(f"URL is outside the project: {value}")
    if not parsed.path:
        if not value.startswith("#"):
            raise ContentSafetyError(f"URL has no safe target: {value}")
        return None
    return parsed.path


def _resolve_local_path(root: Path, url_path: str, *, current_relative: str) -> Path:
    current_parent = PurePosixPath(current_relative).parent
    candidate = PurePosixPath(current_parent, url_path)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ContentSafetyError(f"local URL escapes the project: {url_path}")
    resolved = root / Path(candidate.as_posix())
    if not resolved.is_file() or resolved.is_symlink():
        raise ContentSafetyError(f"local dependency is missing or unsafe: {candidate.as_posix()}")
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ContentSafetyError(f"local URL escapes the project: {url_path}") from exc
    return resolved


def _strip_css_comments(text: str) -> str:
    result = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    if "/*" in result or "*/" in result:
        raise ContentSafetyError("unterminated CSS comment")
    return result


def _validate_css_blocks(text: str, root: Path, css_relative_path: str) -> None:
    stack: list[str] = []
    segment: list[str] = []
    saw_declaration_block = False
    quote: str | None = None
    escaped = False
    for char in text:
        if quote:
            segment.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            segment.append(char)
        elif char == "{":
            prelude = "".join(segment).strip()
            if not prelude:
                raise ContentSafetyError(f"CSS block has no selector: {css_relative_path}")
            if prelude.lower().startswith("@"):
                at_name = prelude[1:].split(None, 1)[0].lower()
                if at_name not in ALLOWED_CSS_AT_RULES:
                    raise ContentSafetyError(f"unsupported CSS at-rule: @{at_name}")
                stack.append("at")
            else:
                stack.append("declarations")
                saw_declaration_block = True
            segment = []
        elif char == ";":
            if stack and stack[-1] == "declarations":
                _validate_declaration("".join(segment), root, css_relative_path)
            elif stack:
                if "".join(segment).strip():
                    raise ContentSafetyError(f"unexpected CSS statement: {css_relative_path}")
            segment = []
        elif char == "}":
            if not stack:
                raise ContentSafetyError(f"unmatched CSS closing brace: {css_relative_path}")
            if stack[-1] == "declarations":
                _validate_declaration("".join(segment), root, css_relative_path)
            stack.pop()
            segment = []
        else:
            segment.append(char)
    if quote or stack:
        raise ContentSafetyError(f"unterminated CSS structure: {css_relative_path}")
    if not saw_declaration_block:
        raise ContentSafetyError(f"CSS has no declaration block: {css_relative_path}")


def _validate_declaration(statement: str, root: Path, css_relative_path: str) -> None:
    statement = statement.strip()
    if not statement:
        return
    if ":" not in statement:
        raise ContentSafetyError(f"invalid CSS declaration: {css_relative_path}")
    property_name, value = statement.split(":", 1)
    property_name = property_name.strip().lower()
    if property_name not in ALLOWED_CSS_PROPERTIES and not property_name.startswith("--"):
        raise ContentSafetyError(f"CSS property is not allowed: {property_name}")
    if CSS_DANGEROUS_RE.search(value):
        raise ContentSafetyError(f"dangerous CSS value: {css_relative_path}")
    if not _balanced_parentheses(value):
        raise ContentSafetyError(f"unbalanced CSS value: {css_relative_path}")
    if re.search(r"url\(", value, re.IGNORECASE) and not CSS_URL_RE.search(value):
        raise ContentSafetyError(f"malformed CSS url(): {css_relative_path}")
    for match in CSS_URL_RE.finditer(value):
        url = match.group("value").strip()
        local = _validate_url(url, allow_external_https=False)
        if local is not None:
            _resolve_local_path(root, local, current_relative=css_relative_path)


def _balanced_parentheses(value: str) -> bool:
    depth = 0
    quote: str | None = None
    escaped = False
    for char in value:
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and quote is None
