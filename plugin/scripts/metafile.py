"""Small helpers the record-* scripts share for editing a role's meta.md.

Not a CLI. The scripts run with `python3 -I`, which drops their own folder from
sys.path, so they load this file by path (see load_metafile in each script).
"""
from __future__ import annotations

import re
from pathlib import Path


def field(meta: str, key: str) -> str:
    """A top-level frontmatter value, without quotes or a trailing comment."""
    m = re.search(rf"^{key}:\s*\"?([^\"\n#]*?)\"?\s*(#.*)?$", meta, re.M)
    return m.group(1).strip() if m else ""


def set_fields(meta: str, values: dict[str, str]) -> str:
    """Set top-level frontmatter keys in place, adding missing ones at the end
    of the block. Every other line, including the body, is left as it was."""
    lines = meta.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "---")
        end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise SystemExit("meta.md has no frontmatter block")
    pending = dict(values)
    for i in range(start + 1, end):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", lines[i])
        if m and m.group(1) in pending:
            lines[i] = f"{m.group(1)}: {pending.pop(m.group(1))}"
    lines[end:end] = [f"{k}: {v}" for k, v in pending.items()]
    return "\n".join(lines)


def append_history(meta: str, line: str) -> str:
    """Append one line to ## History, creating the section if needed."""
    if "## History" in meta:
        return meta.rstrip("\n") + "\n" + line + "\n"
    return meta.rstrip("\n") + "\n\n## History\n" + line + "\n"


def later(a: str, b: str) -> str:
    """The later of two ISO dates; an empty or malformed one loses."""
    ok = [d for d in (a, b) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d or "")]
    return max(ok) if ok else ""


def role_meta(role: Path) -> Path:
    path = role / "meta.md"
    if not path.is_file():
        raise SystemExit(f"No meta.md in {role}")
    return path
