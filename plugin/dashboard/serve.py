"""job-offer dashboard — Python stdlib HTTP server.

Implementation lands across tasks A2-A12. Each task adds one pure helper
or one HTTP endpoint via TDD.
"""
from __future__ import annotations

import argparse
import json as _json
import os
import re
import signal
import sys
import tempfile
import webbrowser
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer
from typing import Any
from urllib.parse import unquote


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
_INDENT_RE = re.compile(r"^(\s+)(\S)")
_LEADING_NOISE_RE = re.compile(r"\A(?:\s+|<!--.*?-->\s*)+", re.DOTALL)
# Match an unquoted inline ` # comment` tail on a YAML value line.
# Requires whitespace before # so URLs like https://example.com#frag stay intact.
_INLINE_COMMENT_RE = re.compile(r"\s+#.*$")


def parse_frontmatter(md: str) -> tuple[dict[str, str], str]:
    """Parse YAML-ish frontmatter from a markdown string.

    Returns (frontmatter_dict, body). Frontmatter values are returned as
    strings (quotes stripped). Nested one-level mappings are flattened with
    dot-notation keys, e.g. `weekly_targets.outreach` -> "7".

    Leading blank lines and HTML comment blocks before the opening `---`
    are skipped, so template files can carry inline documentation above
    the frontmatter without breaking the parse.

    Lines starting with '#' inside the frontmatter are treated as comments
    and ignored. Returns ({}, original_md) if no frontmatter present.
    """
    noise = _LEADING_NOISE_RE.match(md)
    trimmed = md[noise.end():] if noise else md
    match = _FRONTMATTER_RE.match(trimmed)
    if not match:
        return {}, md

    raw_block, body = match.group(1), match.group(2)
    out: dict[str, str] = {}
    current_parent: str | None = None

    for raw_line in raw_block.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent_match = _INDENT_RE.match(raw_line)
        is_nested = indent_match is not None

        if is_nested and current_parent is not None:
            key, _, value = stripped.partition(":")
            out[f"{current_parent}.{key.strip()}"] = _clean_value(value.strip())
            continue

        key, sep, value = stripped.partition(":")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()

        if value == "":
            current_parent = key
        else:
            current_parent = None
            out[key] = _clean_value(value)

    return out, body


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _clean_value(value: str) -> str:
    """Strip inline YAML comments from unquoted values, then strip quotes.

    `true  # re-open in Q3` -> `true`
    `"some # literal"` -> `some # literal` (quoted, comment preserved)
    `https://example.com#frag` -> `https://example.com#frag` (no whitespace before #)
    """
    if value and value[0] not in ('"', "'"):
        value = _INLINE_COMMENT_RE.sub("", value).rstrip()
    return _strip_quotes(value)


_SLUG_RE = re.compile(r"[^a-z0-9]+")
_BRIEF_NAME_RE = re.compile(r"^daily-brief-(\d{4}-\d{2}-\d{2})\.md$")


def position_slug(position: str) -> str:
    """Lowercase, replace runs of non-alphanumeric with a single hyphen, trim hyphens.

    "Senior PM, Consumer Credit" -> "senior-pm-consumer-credit"
    """
    lowered = position.lower()
    hyphenated = _SLUG_RE.sub("-", lowered)
    return hyphenated.strip("-")


_STATUS_LINE_RE = re.compile(r"^(\s*status\s*:\s*)(\"[^\"]*\"|'[^']*'|[^\n]*)$", re.MULTILINE)


def rewrite_status(md: str, new_status: str) -> str:
    """Replace the `status:` value in the frontmatter, preserving quoting style.

    Raises ValueError if no frontmatter is present or no status line is found.
    Only the frontmatter block (between the first two `---` lines) is searched.
    """
    match = _FRONTMATTER_RE.match(md)
    if not match:
        raise ValueError("no frontmatter")
    fm_block = match.group(1)
    body = match.group(2)

    def _replace(m: re.Match[str]) -> str:
        prefix, current = m.group(1), m.group(2)
        if current.startswith('"') and current.endswith('"'):
            return f'{prefix}"{new_status}"'
        if current.startswith("'") and current.endswith("'"):
            return f"{prefix}'{new_status}'"
        return f"{prefix}{new_status}"

    new_block, count = _STATUS_LINE_RE.subn(_replace, fm_block, count=1)
    if count == 0:
        raise ValueError("no status line in frontmatter")

    return f"---\n{new_block}\n---\n{body}"


# Date field each status implies. A status change from the dashboard stamps it
# when missing, so weekly counts (date_applied) and the decided history
# (date_rejected / date_not_interested) work for roles moved by dropdown.
_STATUS_DATE_FIELD = {
    "applied": "date_applied",
    "rejected": "date_rejected",
    "not_interested": "date_not_interested",
}


def stamp_status_date(md: str, new_status: str, today: date) -> str:
    """Add the date field implied by `new_status` to the frontmatter if absent.

    An existing value (even an older one) is never overwritten. The new line is
    appended at the end of the frontmatter block. Unknown statuses are a no-op.
    """
    field = _STATUS_DATE_FIELD.get(new_status)
    if field is None:
        return md
    match = _FRONTMATTER_RE.match(md)
    if not match:
        return md
    fm_block, body = match.group(1), match.group(2)
    existing = re.search(rf"^\s*{field}\s*:\s*(.*)$", fm_block, re.MULTILINE)
    if existing and existing.group(1).strip().strip("\"'"):
        return md
    line = f"{field}: {today.isoformat()}"
    if existing:
        fm_block = fm_block[: existing.start()] + line + fm_block[existing.end() :]
    else:
        fm_block = f"{fm_block}\n{line}"
    return f"---\n{fm_block}\n---\n{body}"


_NEXT_EVENT_LINE_RE = re.compile(r"^[ \t]*next_event[ \t]*:.*$", re.MULTILINE)


def normalize_next_event(value: str) -> str:
    """One frontmatter-safe line: newlines become '; ' (the card splits on ';'),
    double quotes become single quotes, empty steps are dropped."""
    steps = [s.strip() for s in re.split(r"[\r\n;]+", value) if s.strip()]
    return "; ".join(steps).replace('"', "'")


def rewrite_next_event(md: str, value: str, today: date) -> str:
    """Set (or clear, when value is empty) `next_event:` in the frontmatter and
    append a `## History` line, the same trail /today writes for next_event.

    Raises ValueError if there is no frontmatter.
    """
    match = _FRONTMATTER_RE.match(md)
    if not match:
        raise ValueError("no frontmatter")
    fm_block, body = match.group(1), match.group(2)
    new_value = normalize_next_event(value)
    line = f'next_event: "{new_value}"'
    existing = _NEXT_EVENT_LINE_RE.search(fm_block)
    if existing:
        if _clean_value(existing.group(0).split(":", 1)[1].strip()) == new_value:
            return md
        fm_block = fm_block[: existing.start()] + line + fm_block[existing.end() :]
    elif new_value:
        fm_block = f"{fm_block}\n{line}"
    else:
        return md

    history = (
        f'- {today.isoformat()}: next_event → "{new_value}" (dashboard)'
        if new_value
        else f"- {today.isoformat()}: next_event cleared (dashboard)"
    )
    body = body.rstrip("\n")
    if not re.search(r"^## History\s*$", body, re.MULTILINE):
        body = f"{body}\n\n## History" if body.strip() else "## History"
    body = f"{body}\n{history}\n"
    return f"---\n{fm_block}\n---\n{body}"


def atomic_write(target: Path, content: str) -> None:
    """Write content to target atomically: write to temp file in same dir, then rename.

    Creates the target's parent directory if missing.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path_str = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(target.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path_str, target)
    except Exception:
        Path(tmp_path_str).unlink(missing_ok=True)
        raise


def collect_companies(userdata_root: Path) -> list[dict[str, Any]]:
    """Glob both flat and subfolder meta.md files; return one record per position.

    When a company has BOTH a flat meta.md and at least one role-slug
    subfolder (mid-migration state), the flat entry is dropped in favour of
    the subfolder entries — matches /today's "prefer the role-slug-subfolder
    entries" rule. Prevents the dashboard from showing the same company twice
    when an install is mid-migration.
    """
    companies_root = userdata_root / "companies"
    if not companies_root.is_dir():
        return []

    flat_files = list(companies_root.glob("*/meta.md"))
    sub_files = list(companies_root.glob("*/*/meta.md"))

    # Companies that have at least one subfolder meta.md — flat entries for
    # these are stale leftovers from before the multi-role migration.
    companies_with_subfolders = {meta_path.parent.parent.name for meta_path in sub_files}

    results: list[dict[str, Any]] = []

    for meta_path in flat_files:
        company_name = meta_path.parent.name
        if company_name in companies_with_subfolders:
            continue  # subfolder entries take precedence
        fm, _ = parse_frontmatter(meta_path.read_text(encoding="utf-8"))
        record = _build_record(fm, company_name, folder_path=company_name, is_multi_role=False)
        record["has_notes"] = (meta_path.parent / "notes.md").is_file()
        results.append(record)

    for meta_path in sub_files:
        company_name = meta_path.parent.parent.name
        slug = meta_path.parent.name
        fm, _ = parse_frontmatter(meta_path.read_text(encoding="utf-8"))
        record = _build_record(
            fm,
            company_name,
            folder_path=f"{company_name}/{slug}",
            is_multi_role=True,
        )
        record["has_notes"] = (meta_path.parent / "notes.md").is_file()
        results.append(record)

    return results


_OPTIONAL_FIELDS = (
    "score",
    "link",
    "date_added",
    "date_applied",
    "last_inbound",
    "monitoring",
    # Status-specific fields per the /today + /evaluate-position meta.md spec:
    "next_event",       # if a future event is scheduled (input-phase write contract)
    "date_rejected",    # if status: rejected
    "rejection_stage",  # if status: rejected — needed for Coach Trigger C cond 2 surface
    "max_stage",        # deepest stage reached (application|screening|interview|final) — funnel + process goal
    "rejection_note",   # if status: rejected — short quoted recruiter feedback
    "date_not_interested",  # if status: not_interested
)


def _build_record(
    fm: dict[str, str],
    company_name: str,
    *,
    folder_path: str,
    is_multi_role: bool,
) -> dict[str, Any]:
    position = fm.get("position", "")
    record: dict[str, Any] = {
        "company": fm.get("company", company_name),
        "position": position,
        "position_slug": position_slug(position),
        "tier": fm.get("tier", ""),
        "status": fm.get("status", ""),
        "folder_path": folder_path,
        "is_multi_role": is_multi_role,
    }
    for field in _OPTIONAL_FIELDS:
        if field in fm:
            record[field] = fm[field]
    return record


def latest_brief(userdata_root: Path) -> dict[str, str] | None:
    """Return {date, markdown} for the most recent daily-brief, or None if absent."""
    outputs = userdata_root / "outputs"
    if not outputs.is_dir():
        return None
    candidates: list[tuple[str, Path]] = []
    for path in outputs.iterdir():
        m = _BRIEF_NAME_RE.match(path.name)
        if m:
            candidates.append((m.group(1), path))
    if not candidates:
        return None
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    date, path = candidates[0]
    return {"date": date, "markdown": path.read_text(encoding="utf-8")}


def read_strategy(userdata_root: Path) -> dict[str, Any]:
    """Read strategy.md frontmatter, returning {target_offer_date, weekly_targets}."""
    strategy_path = userdata_root / "strategy.md"
    if not strategy_path.is_file():
        return {}
    fm, _ = parse_frontmatter(strategy_path.read_text(encoding="utf-8"))
    weekly: dict[str, int] = {}
    for key, value in fm.items():
        if key.startswith("weekly_targets."):
            sub_key = key.split(".", 1)[1]
            try:
                weekly[sub_key] = int(value)
            except ValueError:
                continue
    out: dict[str, Any] = {"weekly_targets": weekly}
    if "target_offer_date" in fm:
        out["target_offer_date"] = fm["target_offer_date"]
    return out


def _make_handler(
    userdata_root: Path,
    dist_dir: Path | None,
) -> type[BaseHTTPRequestHandler]:
    """Build a request handler class closed over the userdata + dist paths."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            # Suppress default access log; tests want clean output.
            return

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/state":
                self._handle_state()
                return
            if self.path.startswith("/api/positions/") and self.path.endswith("/notes"):
                self._handle_notes_get()
                return
            if self.path.startswith("/api/positions/") and self.path.endswith("/artifacts"):
                self._handle_artifacts_get()
                return
            if dist_dir is not None:
                self._serve_static()
                return
            self._send_status(404, b"not found")

        def do_PATCH(self) -> None:  # noqa: N802
            if self.path.startswith("/api/positions/") and self.path.endswith("/status"):
                self._handle_status_patch()
                return
            if self.path.startswith("/api/positions/") and self.path.endswith("/next_event"):
                self._handle_next_event_patch()
                return
            self._send_status(404, b"not found")

        def do_POST(self) -> None:  # noqa: N802
            if self.path.startswith("/api/positions/") and self.path.endswith("/notes"):
                self._handle_note_post()
                return
            self._send_status(404, b"not found")

        def do_PUT(self) -> None:  # noqa: N802
            if self.path.startswith("/api/positions/") and self.path.endswith("/notes"):
                self._handle_note_mutate(op="edit")
                return
            self._send_status(404, b"not found")

        def do_DELETE(self) -> None:  # noqa: N802
            if self.path.startswith("/api/positions/") and self.path.endswith("/notes"):
                self._handle_note_mutate(op="delete")
                return
            self._send_status(404, b"not found")

        def _handle_artifacts_get(self) -> None:
            folder_path = self.path[len("/api/positions/") : -len("/artifacts")]
            meta_path = _resolve_meta_path(userdata_root, folder_path)
            if meta_path is None:
                self._send_status(400, b"invalid folder_path")
                return
            if not meta_path.is_file():
                self._send_status(404, b"position not found")
                return
            self._send_json(200, collect_artifacts(meta_path.parent))

        def _handle_notes_get(self) -> None:
            folder_path = self.path[len("/api/positions/") : -len("/notes")]
            meta_path = _resolve_meta_path(userdata_root, folder_path)
            if meta_path is None:
                self._send_status(400, b"invalid folder_path")
                return
            notes_path = meta_path.parent / "notes.md"
            markdown = notes_path.read_text(encoding="utf-8") if notes_path.is_file() else ""
            self._send_json(200, {"markdown": markdown})

        def _handle_status_patch(self) -> None:
            folder_path = self.path[len("/api/positions/") : -len("/status")]
            meta_path = _resolve_meta_path(userdata_root, folder_path)
            if meta_path is None:
                self._send_status(400, b"invalid folder_path")
                return
            if not meta_path.is_file():
                self._send_status(404, b"company not found")
                return
            try:
                body = self._read_json_body()
            except _json.JSONDecodeError:
                self._send_status(400, b"invalid json")
                return
            new_status = body.get("status")
            if not isinstance(new_status, str) or not new_status:
                self._send_status(400, b"missing status")
                return
            try:
                new_md = rewrite_status(meta_path.read_text(encoding="utf-8"), new_status)
                new_md = stamp_status_date(new_md, new_status, date.today())
            except ValueError as e:
                self._send_status(409, str(e).encode())
                return
            atomic_write(meta_path, new_md)
            self._send_json(200, {"ok": True})

        def _handle_next_event_patch(self) -> None:
            folder_path = self.path[len("/api/positions/") : -len("/next_event")]
            meta_path = _resolve_meta_path(userdata_root, folder_path)
            if meta_path is None:
                self._send_status(400, b"invalid folder_path")
                return
            if not meta_path.is_file():
                self._send_status(404, b"company not found")
                return
            try:
                body = self._read_json_body()
            except _json.JSONDecodeError:
                self._send_status(400, b"invalid json")
                return
            value = body.get("next_event")
            if not isinstance(value, str):
                self._send_status(400, b"missing next_event")
                return
            try:
                new_md = rewrite_next_event(meta_path.read_text(encoding="utf-8"), value, date.today())
            except ValueError as e:
                self._send_status(409, str(e).encode())
                return
            atomic_write(meta_path, new_md)
            self._send_json(200, {"ok": True, "next_event": normalize_next_event(value)})

        def _handle_note_post(self) -> None:
            folder_path = self.path[len("/api/positions/") : -len("/notes")]
            meta_path = _resolve_meta_path(userdata_root, folder_path)
            if meta_path is None:
                self._send_status(400, b"invalid folder_path")
                return
            if not meta_path.is_file():
                self._send_status(404, b"company not found")
                return
            try:
                body = self._read_json_body()
            except _json.JSONDecodeError:
                self._send_status(400, b"invalid json")
                return
            note = body.get("note")
            if not isinstance(note, str) or not note.strip():
                self._send_status(400, b"missing note")
                return
            fm, _ = parse_frontmatter(meta_path.read_text(encoding="utf-8"))
            company = fm.get("company", meta_path.parent.name)
            position = fm.get("position", "")
            append_note(meta_path.parent / "notes.md", company, position, note)
            self._send_json(200, {"ok": True})

        def _handle_note_mutate(self, *, op: str) -> None:
            folder_path = self.path[len("/api/positions/") : -len("/notes")]
            meta_path = _resolve_meta_path(userdata_root, folder_path)
            if meta_path is None:
                self._send_status(400, b"invalid folder_path")
                return
            notes_path = meta_path.parent / "notes.md"
            if not notes_path.is_file():
                self._send_status(404, b"notes file not found")
                return
            try:
                body = self._read_json_body()
            except _json.JSONDecodeError:
                self._send_status(400, b"invalid json")
                return
            index = body.get("index")
            heading = body.get("heading")
            if not isinstance(index, int) or not isinstance(heading, str) or not heading.strip():
                self._send_status(400, b"missing index or heading")
                return
            current_md = notes_path.read_text(encoding="utf-8")
            try:
                if op == "edit":
                    new_body = body.get("body")
                    if not isinstance(new_body, str) or not new_body.strip():
                        self._send_status(400, b"missing body")
                        return
                    new_md = edit_note(current_md, index, heading, new_body)
                else:  # op == "delete"
                    new_md = delete_note(current_md, index, heading)
            except ValueError as e:
                self._send_status(409, str(e).encode())
                return
            atomic_write(notes_path, new_md)
            self._send_json(200, {"ok": True})

        def _handle_state(self) -> None:
            companies = collect_companies(userdata_root)
            payload = {
                "companies": companies,
                "strategy": read_strategy(userdata_root),
                "weekly_progress": compute_weekly_progress(userdata_root, companies),
                "latest_brief": latest_brief(userdata_root),
                "userdata_root": str(userdata_root.resolve()),
            }
            self._send_json(200, payload)

        def _serve_static(self) -> None:
            # Map "/" to index.html; anything else to the literal path under dist_dir.
            assert dist_dir is not None
            rel = self.path.lstrip("/") or "index.html"
            file_path = (dist_dir / rel).resolve()
            try:
                file_path.relative_to(dist_dir.resolve())
            except ValueError:
                self._send_status(403, b"forbidden")
                return
            if not file_path.is_file():
                # SPA fallback: serve index.html for unknown routes
                file_path = dist_dir / "index.html"
                if not file_path.is_file():
                    self._send_status(404, b"not found")
                    return
            content = file_path.read_bytes()
            ctype = _guess_content_type(file_path.name)
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def _send_json(self, status: int, payload: Any) -> None:
            body = _json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_status(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b""
            return _json.loads(raw) if raw else {}

    return Handler


def _resolve_meta_path(userdata_root: Path, folder_path: str) -> Path | None:
    """Resolve a folder_path from the URL to a meta.md path, refusing traversal."""
    decoded = unquote(folder_path)
    if not decoded or ".." in decoded.split("/") or decoded.startswith("/"):
        return None
    target = (userdata_root / "companies" / decoded / "meta.md").resolve()
    try:
        target.relative_to((userdata_root / "companies").resolve())
    except ValueError:
        return None
    return target


def append_note(notes_path: Path, company: str, position: str, note: str) -> None:
    """Append a timestamped note to notes_path. Create with title heading on first write."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {timestamp}\n\n{note.strip()}\n"
    if not notes_path.exists():
        header = f"# Notes — {company} {position}\n".rstrip() + "\n"
        atomic_write(notes_path, header + entry)
        return
    atomic_write(notes_path, notes_path.read_text(encoding="utf-8") + entry)


def split_notes(md: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a notes.md file into (preamble, [(heading, body), ...]).

    Preamble is everything before the first `## ` heading (typically the `# Notes — …` title).
    Each entry's body keeps its original spacing minus the heading line itself.
    """
    preamble: list[str] = []
    entries: list[tuple[str, list[str]]] = []
    current: tuple[str, list[str]] | None = None
    for line in md.splitlines(keepends=True):
        m = re.match(r"^##\s+(.+?)\s*\n?$", line)
        if m:
            if current is not None:
                entries.append(current)
            current = (m.group(1).strip(), [])
        else:
            if current is None:
                preamble.append(line)
            else:
                current[1].append(line)
    if current is not None:
        entries.append(current)
    return "".join(preamble), [(h, "".join(b)) for h, b in entries]


def _join_notes(preamble: str, entries: list[tuple[str, str]]) -> str:
    """Inverse of split_notes — rebuild the file with the canonical append_note spacing."""
    parts: list[str] = []
    if preamble:
        parts.append(preamble.rstrip("\n") + "\n" if preamble.strip() else preamble)
    for heading, body in entries:
        parts.append(f"\n## {heading}\n\n{body.strip()}\n")
    return "".join(parts)


def edit_note(md: str, index: int, expected_heading: str, new_body: str) -> str:
    """Replace the body of the note at `index`. Heading is preserved."""
    if not new_body.strip():
        raise ValueError("note body cannot be empty")
    preamble, entries = split_notes(md)
    if not 0 <= index < len(entries):
        raise ValueError(f"note index {index} out of range (0-{len(entries) - 1})")
    actual_heading = entries[index][0]
    if actual_heading != expected_heading:
        raise ValueError(
            f"heading mismatch at index {index}: expected {expected_heading!r}, found {actual_heading!r}"
        )
    entries[index] = (actual_heading, new_body)
    return _join_notes(preamble, entries)


def delete_note(md: str, index: int, expected_heading: str) -> str:
    """Drop the note at `index`. Verifies the heading matches as a concurrency check."""
    preamble, entries = split_notes(md)
    if not 0 <= index < len(entries):
        raise ValueError(f"note index {index} out of range (0-{len(entries) - 1})")
    if entries[index][0] != expected_heading:
        raise ValueError(
            f"heading mismatch at index {index}: expected {expected_heading!r}, found {entries[index][0]!r}"
        )
    entries.pop(index)
    return _join_notes(preamble, entries)


# -- Weekly progress -----------------------------------------------------------
#
# Mirrors the /today skill's contract (plugin/skills/today/SKILL.md):
#   - warm_outreach: `sent` outreach lines (reach-out, referral-ask, intro-ask,
#     follow-up) in userdata/people/*.md logs dated in the current ISO week.
#     The rules live in plugin/scripts/people.py, shared with the skills and the
#     schema validator; schema in plugin/schemas/person.md.schema.md.
#   - applications: count of meta.md files with date_applied in the current ISO
#     week.
#   - feedback_requests: count of journal.md bullets in the current ISO week
#     that log a feedback request (dashboard-only; /today doesn't report it).
# Window is the current ISO week: [Monday of this week, today] inclusive.
# So on a Tuesday the window is 2 days; on a Sunday it is 7. This matches the
# user's intuitive "this week" framing — a Monday morning shows a fresh week.


def _load_people_module():
    import importlib.util
    path = Path(__file__).resolve().parent.parent / "scripts" / "people.py"
    spec = importlib.util.spec_from_file_location("job_offer_people", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


people = _load_people_module()

_JOURNAL_HEADING_RE = re.compile(r"^##\s+(.*?)\s*$")
_JOURNAL_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})$")
_BULLET_START_RE = re.compile(r"^\s*[-*]\s")


def read_journal(userdata_root: Path) -> str:
    """Return the raw contents of userdata/journal.md, or '' if missing."""
    journal_path = userdata_root / "journal.md"
    if not journal_path.is_file():
        return ""
    return journal_path.read_text(encoding="utf-8")


def _week_bullets(journal_md: str, today: date) -> list[str]:
    """Return the text of each journal bullet dated in the current ISO week.

    A bullet is a top-level `- …` or `* …` line plus its continuation lines.
    Bullets under dated headings outside [Monday of this week, today] are skipped.
    Malformed date headings (non-ISO) close the window until the next valid one.
    """
    if not journal_md.strip():
        return []

    window_start = today - timedelta(days=today.weekday())
    bullets: list[str] = []
    in_window = False
    bullet_lines: list[str] = []

    def _flush() -> None:
        if bullet_lines:
            bullets.append("\n".join(bullet_lines))

    for line in journal_md.splitlines():
        heading = _JOURNAL_HEADING_RE.match(line)
        if heading:
            # Any `## ` heading closes the current bullet and resets scope.
            # Only ISO-date headings open a new in-window section.
            _flush()
            bullet_lines = []
            date_match = _JOURNAL_DATE_RE.match(heading.group(1))
            if date_match:
                try:
                    entry_date = date.fromisoformat(date_match.group(1))
                except ValueError:
                    in_window = False
                    continue
                in_window = window_start <= entry_date <= today
            else:
                in_window = False
            continue

        if not in_window:
            continue

        if _BULLET_START_RE.match(line):
            _flush()
            bullet_lines = [line]
        elif bullet_lines:
            bullet_lines.append(line)

    _flush()
    return bullets


def count_warm_outreach(userdata_root: Path, today: date) -> int:
    """Count `sent` outreach lines in people/*.md logs in the current ISO week."""
    return people.count_outreach(userdata_root, today)


# A feedback request is the user asking a company why they were turned down.
# Feedback someone else promised or gave ("James will give feedback") is not one.
_FEEDBACK_REQUEST_RE = re.compile(
    r"\bfeedback\s+requests?\b"
    r"|\brequest(?:ed|ing)?\s+(?:for\s+)?feedback\b"
    r"|\bask(?:ed|ing)?\b[^.\n]{0,60}\bfeedback\b",
    re.IGNORECASE,
)


def count_feedback_requests(journal_md: str, today: date) -> int:
    """Count journal bullets in the current ISO week that log a feedback request."""
    return sum(1 for text in _week_bullets(journal_md, today) if _FEEDBACK_REQUEST_RE.search(text))


def count_recent_applications(companies: list[dict[str, Any]], today: date) -> int:
    """Count positions whose date_applied falls in [Monday of this week, today]."""
    window_start = today - timedelta(days=today.weekday())
    count = 0
    for p in companies:
        raw = p.get("date_applied")
        if not isinstance(raw, str) or not raw:
            continue
        try:
            applied = date.fromisoformat(raw)
        except ValueError:
            continue
        if window_start <= applied <= today:
            count += 1
    return count


# -- Per-position artifacts ---------------------------------------------------
#
# Each company folder may contain artifacts beyond meta.md + notes.md:
#   - research-brief.md (single, written by /evaluate-position)
#   - interview-prep-YYYY-MM-DD.md (multiple, written by /interview-prep)
#   - interview-debrief-YYYY-MM-DD-<stage>.md (multiple, written by
#     /interview-analysis; <stage> is free-form, e.g. "hm", "panel",
#     "cpo-round")
# These helpers feed the company drawer's tabs in the dashboard.

_PREP_FILENAME_RE = re.compile(r"^interview-prep-(\d{4}-\d{2}-\d{2})\.md$")
_DEBRIEF_FILENAME_RE = re.compile(r"^interview-debrief-(\d{4}-\d{2}-\d{2})-(.+)\.md$")


def read_artifact(folder: Path, filename: str) -> str | None:
    """Return the file contents, or None if it doesn't exist."""
    path = folder / filename
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def list_prep_docs(folder: Path) -> list[dict[str, str]]:
    """Return interview-prep docs in the folder, newest first.

    Filenames not matching `interview-prep-YYYY-MM-DD.md` are silently skipped
    so a user's accidental `interview-prep-rough.md` doesn't break the API.
    """
    out: list[dict[str, str]] = []
    for path in sorted(folder.glob("interview-prep-*.md")):
        m = _PREP_FILENAME_RE.match(path.name)
        if not m:
            continue
        out.append({
            "date": m.group(1),
            "filename": path.name,
            "markdown": path.read_text(encoding="utf-8"),
        })
    out.sort(key=lambda d: d["date"], reverse=True)
    return out


def list_debrief_docs(folder: Path) -> list[dict[str, str]]:
    """Return interview-debrief docs in the folder, newest first.

    Stage is whatever appears between the date and `.md` — free-form so a user
    can write `interview-debrief-2026-05-12-cpo-round.md` without us mangling it.
    """
    out: list[dict[str, str]] = []
    for path in sorted(folder.glob("interview-debrief-*.md")):
        m = _DEBRIEF_FILENAME_RE.match(path.name)
        if not m:
            continue
        out.append({
            "date": m.group(1),
            "stage": m.group(2),
            "filename": path.name,
            "markdown": path.read_text(encoding="utf-8"),
        })
    out.sort(key=lambda d: d["date"], reverse=True)
    return out


def collect_artifacts(folder: Path) -> dict[str, Any]:
    """Build the {research, preps, debriefs} payload for the company drawer."""
    return {
        "research": read_artifact(folder, "research-brief.md"),
        "preps": list_prep_docs(folder),
        "debriefs": list_debrief_docs(folder),
    }


def compute_weekly_progress(
    userdata_root: Path,
    companies: list[dict[str, Any]],
    today: date | None = None,
) -> dict[str, Any]:
    """Build the {warm_outreach, feedback_requests, applications, window_days} payload for /api/state.

    `window_days` is the number of days from Monday of this week through today
    inclusive — so Monday → 1, Tuesday → 2, …, Sunday → 7.
    """
    today = today or date.today()
    journal_md = read_journal(userdata_root)
    return {
        "warm_outreach": count_warm_outreach(userdata_root, today),
        "feedback_requests": count_feedback_requests(journal_md, today),
        "applications": count_recent_applications(companies, today),
        "window_days": today.weekday() + 1,
    }


def _guess_content_type(name: str) -> str:
    if name.endswith(".html"):
        return "text/html; charset=utf-8"
    if name.endswith(".js"):
        return "application/javascript; charset=utf-8"
    if name.endswith(".css"):
        return "text/css; charset=utf-8"
    if name.endswith(".svg"):
        return "image/svg+xml"
    if name.endswith(".json"):
        return "application/json"
    return "application/octet-stream"


def build_server(
    userdata_root: Path,
    *,
    preferred_port: int,
    dist_dir: Path | None,
) -> tuple[TCPServer, int]:
    """Bind a ThreadingHTTPServer on exactly preferred_port.

    The dashboard always lives at one address (7890 by default), so a busy port
    is an error, not a reason to drift to the next one: a second server on 7891
    would hide the first. If preferred_port is 0, the OS picks any free port
    (used in tests).
    """
    handler_cls = _make_handler(userdata_root, dist_dir)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", preferred_port), handler_cls)
    except OSError as e:
        raise RuntimeError(
            f"port {preferred_port} is already in use — if it's the dashboard, open "
            f"http://localhost:{preferred_port}; otherwise see what holds it with "
            f"`lsof -iTCP:{preferred_port} -sTCP:LISTEN`"
        ) from e
    return server, server.server_address[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pm-dashboard")
    parser.add_argument("--userdata", required=True, type=Path,
                        help="Path to the workspace's userdata/ directory")
    parser.add_argument("--dist", default=None, type=Path,
                        help="Path to the built dashboard dist/ (defaults to ./dist relative to this file)")
    parser.add_argument("--port", default=7890, type=int)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args(argv)

    userdata_root = args.userdata.expanduser().resolve()
    if not userdata_root.is_dir():
        print(f"error: userdata directory not found: {userdata_root}", file=sys.stderr)
        return 1

    dist_dir = args.dist or (Path(__file__).parent / "dist")
    dist_dir = dist_dir.expanduser().resolve()
    if not dist_dir.is_dir():
        print(
            f"error: dashboard bundle not found at {dist_dir}.\n"
            "If you're a contributor, build it first: cd plugin/dashboard && npm install && npm run build",
            file=sys.stderr,
        )
        return 1

    try:
        server, port = build_server(
            userdata_root=userdata_root,
            preferred_port=args.port,
            dist_dir=dist_dir,
        )
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    url = f"http://localhost:{port}"
    print(f"job-offer dashboard: {url}", flush=True)
    print("Press ctrl-C to stop.", flush=True)

    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def _handle_sigint(_signum: int, _frame: Any) -> None:
        print("\nshutting down...", flush=True)
        server.shutdown()

    signal.signal(signal.SIGINT, _handle_sigint)
    try:
        server.serve_forever()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
