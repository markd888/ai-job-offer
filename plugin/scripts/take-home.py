#!/usr/bin/env python3
"""Take-home assignments: check a draft against the brief's limits, freeze what was submitted.

Used by /take-home (#10).

Usage:
  python3 -I take-home.py check <draft.md> --limits <limits.json> [--json]
  python3 -I take-home.py freeze <role-dir> <draft.md> [<file> ...] [--brief brief.md]
      [--limits limits.json] [--date YYYY-MM-DD] [--force]

limits.json is written by /take-home from the brief. Every key is optional; a
missing key means the brief set no such limit:

  {"max_words": 1500, "max_requirements": 5, "requirements_heading": "Requirements",
   "required_sections": ["Problem", "Assumptions", "Requirements", "Metrics"],
   "assumptions": "marked", "ai_policy": "allowed|disclose|forbidden|unknown",
   "penalise_over_documentation": true, "deadline": "2026-11-28"}

check exits 1 when a hard limit fails: over the word cap, too many requirements,
a required section missing, an assumption marker with no entry (or the other way
round), or no "AI use" section when the brief asks for disclosure. Everything
else is a warning and leaves the exit code at 0.

freeze copies the draft, any extra files, the brief and the limits into
<role-dir>/submitted-take-home-<date>/, writes a manifest with hashes, and adds
one History line. It never changes status.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path


def _load(name: str):
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mf = _load("metafile")

AI_POLICIES = ("allowed", "disclose", "forbidden", "unknown")
NEAR_CAP = 0.9
_MARK = re.compile(r"\[(A\d+)\]")
_EXTRA = re.compile(r"appendix|annex|further reading|additional notes|faq|glossary|references", re.I)


# ----- parsing the draft -------------------------------------------------------

def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            return parts[1].split("\n", 1)[1] if "\n" in parts[1] else ""
    return text


def words(text: str) -> int:
    body = re.sub(r"```.*?```", " ", strip_frontmatter(text), flags=re.S)
    body = re.sub(r"^\s*\|?[-:| ]+\|?\s*$", " ", body, flags=re.M)   # table rules
    body = re.sub(r"[#*_>`|\[\]()]", " ", body)
    return len(re.findall(r"[\w'’%.,-]*\w[\w'’%.,-]*", body))


def sections(text: str) -> list[tuple[int, str, str]]:
    """(level, heading, body) for every markdown heading, outside code blocks."""
    body = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), strip_frontmatter(text), flags=re.S)
    out: list[tuple[int, str, list[str]]] = []
    for line in body.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            out.append((len(m.group(1)), m.group(2), []))
        elif out:
            out[-1][2].append(line)
    return [(lvl, h, "\n".join(b)) for lvl, h, b in out]


def _norm(h: str) -> str:
    return re.sub(r"^[\d.\s]+", "", h).strip().lower()


def find_section(secs, name: str):
    n = name.strip().lower()
    for lvl, h, b in secs:
        if _norm(h) == n or _norm(h).startswith(n):
            return lvl, h, b
    return None


def top_level_items(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^(?:[-*+]|\d+[.)])\s+(.*)$", body, re.M)]


# ----- check -------------------------------------------------------------------

def check(text: str, limits: dict) -> dict:
    secs = sections(text)
    results: list[dict] = []

    def add(name, ok, detail, hard=True):
        results.append({"check": name, "status": "pass" if ok else ("fail" if hard else "warn"), "detail": detail})

    n = words(text)
    cap = limits.get("max_words")
    if cap:
        add("words", n <= cap, f"{n} of {cap}")
        if n <= cap and n >= NEAR_CAP * cap:
            add("words near cap", False, f"{n} is within 10% of {cap}", hard=False)
    for name in limits.get("required_sections") or []:
        add(f"section: {name}", find_section(secs, name) is not None,
            "present" if find_section(secs, name) else "missing")

    mx = limits.get("max_requirements")
    if mx:
        heading = limits.get("requirements_heading", "Requirements")
        sec = find_section(secs, heading)
        if sec is None:
            add("requirements", False, f'no "{heading}" section to count')
        else:
            # Count the section's own list plus any sub-headings' lists up to the next same-level heading.
            lvl = sec[0]
            idx = secs.index(sec)
            body = sec[2]
            for l2, _, b2 in secs[idx + 1:]:
                if l2 <= lvl:
                    break
                body += "\n" + b2
            items = [i for i in top_level_items(body) if not re.match(r"^\s", i)]
            add("requirements", len(items) <= mx, f"{len(items)} of {mx}")

    if limits.get("assumptions") == "marked":
        log = find_section(secs, "Assumptions")
        body_wo_log = "\n".join(b for lvl, h, b in secs if not _norm(h).startswith("assumptions"))
        used = set(_MARK.findall(body_wo_log))
        logged = set(_MARK.findall(log[2])) if log else set()
        if log is None:
            add("assumptions", False, 'no "Assumptions" section')
        else:
            missing, unused = sorted(used - logged), sorted(logged - used)
            detail = []
            if missing:
                detail.append("marked but not in the log: " + ", ".join(missing))
            if unused:
                detail.append("in the log but never marked in the text: " + ", ".join(unused))
            add("assumptions", not missing and not unused,
                "; ".join(detail) or f"{len(logged)} logged, all marked in the text")
            if not logged:
                add("assumptions used", False, "the log is empty — no assumption is marked", hard=False)

    policy = limits.get("ai_policy", "unknown")
    if policy not in AI_POLICIES:
        policy = "unknown"
    has_ai = find_section(secs, "AI use") is not None
    if policy == "disclose":
        add("AI use note", has_ai, "present" if has_ai else 'the brief asks for one; add an "AI use" section')
    elif policy == "forbidden":
        add("AI policy", False, "the brief forbids AI tools — the text must be yours; this check can't verify it",
            hard=False)
    elif policy == "unknown":
        add("AI policy", False, "the brief says nothing about AI tools — ask, or state your use", hard=False)

    if limits.get("penalise_over_documentation"):
        extra = [h for _, h, _ in secs if _EXTRA.search(h)]
        if extra:
            add("over-documentation", False, "sections the brief may penalise: " + ", ".join(extra), hard=False)
        allowed = {s.lower() for s in limits.get("required_sections") or []}
        if allowed:
            # Second-level sections outside the brief's structure (the AI note is always allowed).
            unasked = [h for lvl, h, _ in secs if lvl == 2 and _norm(h) != "ai use"
                       and not any(_norm(h).startswith(a) for a in allowed)]
            if unasked:
                add("unasked sections", False, "not in the brief's structure: " + ", ".join(unasked), hard=False)

    dl = limits.get("deadline")
    if dl:
        try:
            left = (date.fromisoformat(dl) - date.today()).days
            add("deadline", left >= 0, f"{dl} ({left} days left)" if left >= 0 else f"{dl} has passed", hard=False)
        except ValueError:
            add("deadline", False, f"unreadable date {dl!r}", hard=False)

    hard_fail = any(r["status"] == "fail" for r in results)
    return {"words": n, "results": results, "exit_code": 1 if hard_fail else 0}


def render(res: dict) -> str:
    icon = {"pass": "✅", "fail": "❌", "warn": "⚠️"}
    lines = ["| Check | Result | Detail |", "|---|---|---|"]
    lines += [f"| {r['check']} | {icon[r['status']]} | {r['detail']} |" for r in res["results"]]
    fails = [r["check"] for r in res["results"] if r["status"] == "fail"]
    lines.append("")
    lines.append(("FAIL: " + ", ".join(fails)) if fails else "PASS — every hard limit holds.")
    return "\n".join(lines)


# ----- freeze ------------------------------------------------------------------

def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def freeze(role: Path, files: list[Path], brief: Path | None, limits: Path | None, day: str, force: bool) -> Path:
    meta_path = mf.role_meta(role)
    dest = role / f"submitted-take-home-{day}"
    if dest.exists() and not force:
        raise SystemExit(f"{dest.name} already exists — pass --force to replace it")
    for f in files + [p for p in (brief, limits) if p]:
        if not f.is_file():
            raise SystemExit(f"Not a file: {f}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir()
    rows = []
    for f, kind in [(f, "submitted") for f in files] + [(p, k) for p, k in ((brief, "brief"), (limits, "limits")) if p]:
        target = dest / f.name
        shutil.copy2(f, target)
        rows.append(f"| {f.name} | {kind} | {_sha(target)} |")
    (dest / "manifest.md").write_text(
        f"# Take-home submitted {day}\n\n| File | Kind | sha256 (12) |\n|---|---|---|\n" + "\n".join(rows) + "\n",
        encoding="utf-8")
    meta = meta_path.read_text(encoding="utf-8")
    names = ", ".join(f.name for f in files)
    meta_path.write_text(mf.append_history(meta, f"- {day}: take-home submitted ({names}) → {dest.name}/"),
                         encoding="utf-8")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("draft", type=Path)
    c.add_argument("--limits", type=Path, required=True)
    c.add_argument("--json", action="store_true")
    f = sub.add_parser("freeze")
    f.add_argument("role", type=Path)
    f.add_argument("files", type=Path, nargs="+")
    f.add_argument("--brief", type=Path)
    f.add_argument("--limits", type=Path)
    f.add_argument("--date", default=date.today().isoformat())
    f.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.cmd == "check":
        res = check(a.draft.read_text(encoding="utf-8"), json.loads(a.limits.read_text(encoding="utf-8")))
        print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else render(res))
        return res["exit_code"]
    dest = freeze(a.role, a.files, a.brief, a.limits, a.date, a.force)
    print(f"Froze {len(a.files)} file(s) into {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
