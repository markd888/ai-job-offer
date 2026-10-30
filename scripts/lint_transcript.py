#!/usr/bin/env python3
"""Deterministic lint over a journey transcript.

Single source of truth for the mechanically-checkable half of what used to be
rubrics/lint-checklist.md. Called three ways:
  * test-personas Phase 3.5 — over the transcript a journey just produced
  * CI (tests/test_lint_transcript.py) — over each frozen corpus transcript
  * by hand: python3 scripts/lint_transcript.py <transcript.md>

Its output reaches the judge as an authoritative block, same contract as the
schema validator: a lint finding is a fact, not something to re-litigate from
the transcript. So a false finding is worse than a missing one — every rule
here is deliberately narrow, and anything needing judgement stayed with the
judge (old Rule 2, "two unrelated asks", lives in rubrics/tone.md as Rule A).

Rules, and what each needs:
  lint.fenced-summary      transcript only
  lint.unresolved-ref      transcript + plugin/ tree
  lint.jargon              transcript only
  lint.file-path           transcript only
  lint.prior-state-prompt  transcript + the snapshot the run started from
  lint.hardcoded-cadence   transcript + the userdata/ tree the run produced

Rules whose input is missing are reported as NOT CHECKED rather than silently
passing — a clean run must not be mistaken for full coverage.

Stdlib only, no deps. Exit 0 = clean, 1 = findings, 2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import namedtuple
from pathlib import Path

Finding = namedtuple("Finding", ["turn", "rule", "detail"])

TURN_RE = re.compile(r"^## Turn (\d+) — (USER|ASSISTANT)\s*$", re.MULTILINE)
SNAPSHOT_RE = re.compile(r"^\*\*Snapshot:\*\*\s*(.+?)\s*$", re.MULTILINE)
FENCE_RE = re.compile(r"^```(.*)$")

# A fenced block is allowed when it carries a real language tag, or when its
# first non-blank line reads as a shell command the user is meant to run. The
# violation this rule targets is a summary rendered to chat inside a bare
# fence. Corpus evidence: across 15 transcripts there is exactly one fenced
# block in an assistant turn, and it is the allowed dashboard launch command.
PROSE_INFO = {"", "text", "txt", "markdown", "md"}
SHELL_START_RE = re.compile(
    r"^\s*(?:\$\s*)?(?:python3?|pip3?|npm|npx|node|git|cd|ls|cat|make|curl"
    r"|open|sh|bash|zsh|chmod|mkdir|mv|cp|rm|echo|export|\./)\b"
)

# Both plugins in this repo, so a job-sweep transcript gets checked too. The
# regex used to match `/job-offer:` only, which made this rule silently
# inert on sweep-smoke runs — it reported nothing and looked like a pass.
SKILL_REF_RE = re.compile(r"/(job-offer|job-sweep):([A-Za-z0-9_-]+)")
ROOT_REF_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")

# Flat ban, not "jargon without explanation". The largest measured source of
# judge disagreement in the corpus was three findings arguing about whether
# `meta.md` / `status: new` / `tier: unscored` counted as explained. As a flat
# ban that argument cannot occur, and it is the better product rule anyway.
# The `(?<!\w\s)` guard on the two key forms separates a frontmatter key from
# an ordinary word that happens to precede a colon. `**BNPL rewards tier:**` in
# a proof-point bullet is English; `` `tier: unscored` `` is the field. Without
# the guard the rule fired on the bullet and, being colon-anchored, missed both
# real leaks in the same run (2026-08-22 turns 11 and 19) — a false positive and
# two misses from one pattern. The backtick-value alternative catches the other
# shape the product actually emits: "filed with status `new`".
JARGON = [
    ("frontmatter", re.compile(r"\bfrontmatter\b", re.IGNORECASE)),
    ("tier_weights", re.compile(r"\btier_weights\b")),
    ("tier_thresholds", re.compile(r"\btier_thresholds\b")),
    ("tier rubric", re.compile(r"\btier\s+rubric\b", re.IGNORECASE)),
    ("P0/P1/P2", re.compile(r"\bP[012]\b")),
    ("status:", re.compile(r"(?<!\w\s)\bstatus\s*:|\bstatus\s+`")),
    ("tier:", re.compile(r"(?<!\w\s)\btier\s*:")),
    ("CLAUDE_PLUGIN_ROOT", re.compile(r"CLAUDE_PLUGIN_ROOT")),
]

# Files the plugin owns and the user never authors. Naming one in chat is the
# single most common way internal detail reaches the user — it accounted for
# seven of the eleven findings in the 2026-08-22 blind pass, of which the judge
# reported two. Mechanically decidable, so it belongs here and not in a rubric.
# `cv.md` is on the list deliberately: the user does place that file, but they
# should be told a folder in plain words, not a filename.
PLUGIN_FILES = [
    "profile.md", "strategy.md", "journal.md", "applications.md",
    "meta.md", "research-brief.md", "cv.md", "help.md", "integrations.md",
]
PLUGIN_FILE_RE = re.compile(
    r"\b(" + "|".join(re.escape(f) for f in PLUGIN_FILES) + r")\b"
    r"|\b((?:daily-brief|interview-prep|interview-debrief|offer-evaluation|cv)"
    r"-[0-9A-Za-z*<>-]+\.md)\b"
)
# A bare `userdata/` is allowed: it is the one folder the user physically puts a
# file into, and no wording avoids naming it. Anything BELOW it is the plugin's
# own structure and has no business in chat.
USERDATA_PATH_RE = re.compile(r"\buserdata/[A-Za-z0-9_*.<>-]+[A-Za-z0-9_*./<>-]*")

PRIOR_STATE_RE = re.compile(
    r"since (?:the )?last time|since we last|since your last|since you last"
    r"|anything (?:that(?:'s| has)? )?moved|last time you|previous run"
    r"|your last run|catch me up on",
    re.IGNORECASE,
)

CADENCE_RE = re.compile(
    r"\b(\d+)\s+(applications?|outreaches?|messages?|founders?|roles?|threads?)\b",
    re.IGNORECASE,
)
CLOCK_RE = re.compile(r"\bevery\s+(\d{1,2})\s*(?:am|pm)\b", re.IGNORECASE)

Turn = namedtuple("Turn", ["number", "role", "body"])


def parse_turns(text: str) -> list[Turn]:
    """Split a transcript into turns. Anything before the first turn header
    (the run metadata block) is not a turn and is never linted."""
    marks = list(TURN_RE.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append(Turn(int(m.group(1)), m.group(2), text[m.end():end]))
    return out


def fenced_blocks(body: str) -> list[tuple[str, str]]:
    """(info string, content) for each fenced block. An unterminated fence
    runs to the end of the turn rather than swallowing the rest of the file."""
    out, info, buf, inside = [], None, [], False
    for line in body.splitlines():
        m = FENCE_RE.match(line)
        if m and not inside:
            inside, info, buf = True, m.group(1).strip(), []
        elif m and inside:
            out.append((info or "", "\n".join(buf)))
            inside = False
        elif inside:
            buf.append(line)
    if inside:
        out.append((info or "", "\n".join(buf)))
    return out


def strip_fences(body: str) -> str:
    out, inside = [], False
    for line in body.splitlines():
        if FENCE_RE.match(line):
            inside = not inside
            continue
        if not inside:
            out.append(line)
    return "\n".join(out)


INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")


def mask_shell_spans(text: str) -> str:
    """Blank out inline `code` spans that read as shell commands, preserving
    length so match offsets still index the original text. A command the user
    is meant to type is not jargon — `python3 ${CLAUDE_PLUGIN_ROOT}/…` in
    2026-07-11 turn 22 is the case this exists for, and the judge that read it
    agreed it was allowed."""
    return INLINE_CODE_RE.sub(
        lambda m: "`" + " " * len(m.group(1)) + "`"
        if SHELL_START_RE.match(m.group(1)) else m.group(0),
        text,
    )


def _quote(text: str, match_start: int, width: int = 90) -> str:
    """The line the match sits on, windowed around the match. Centring matters:
    long assistant lines routinely push the offending term past a plain
    left-anchored truncation, leaving a finding whose quote doesn't show the
    thing it is complaining about."""
    start = text.rfind("\n", 0, match_start) + 1
    end = text.find("\n", match_start)
    if end == -1:
        end = len(text)
    line, off = text[start:end], match_start - start
    if len(line) > width:
        lo = max(0, off - width // 2)
        hi = min(len(line), lo + width)
        lo = max(0, hi - width)
        line = ("…" if lo > 0 else "") + line[lo:hi] + ("…" if hi < len(line) else "")
    return re.sub(r"\s+", " ", line).strip()


def check_fenced_summary(turns: list[Turn]) -> list[Finding]:
    out = []
    for t in turns:
        if t.role != "ASSISTANT":
            continue
        for info, content in fenced_blocks(t.body):
            if info.lower() not in PROSE_INFO:
                continue  # a real language tag — file content or code
            first = next((ln for ln in content.splitlines() if ln.strip()), "")
            if SHELL_START_RE.match(first):
                continue  # shell command the user is meant to run
            out.append(Finding(t.number, "lint.fenced-summary",
                               f"bare fenced block in chat: \"{_quote(first, 0)}\""))
    return out


def default_roots(plugin: Path) -> dict[str, Path]:
    """The two plugins this repo ships. `plugin-sweep` is only registered when
    it is actually there, so a caller pointing at some other tree gets an
    explicit 'no plugin tree configured' finding rather than a false pass."""
    roots = {"job-offer": Path(plugin)}
    sweep = Path(plugin).parent / "plugin-sweep"
    if sweep.is_dir():
        roots["job-sweep"] = sweep
    return roots


def check_unresolved_refs(turns: list[Turn], roots: dict[str, Path]) -> list[Finding]:
    """`roots` maps a slash-command namespace to the plugin tree that owns it.
    A namespace with no configured root is reported, not skipped — silently
    passing an unresolvable reference is the failure this rule exists to stop."""
    out = []
    for t in turns:
        if t.role != "ASSISTANT":
            continue
        for m in SKILL_REF_RE.finditer(t.body):
            ns, name = m.group(1), m.group(2)
            root = roots.get(ns)
            if root is None:
                out.append(Finding(t.number, "lint.unresolved-ref",
                                   f"/{ns}:{name} — no plugin tree configured for "
                                   f"'{ns}', cannot resolve"))
            elif not (root / "skills" / name).is_dir():
                out.append(Finding(t.number, "lint.unresolved-ref",
                                   f"/{ns}:{name} — no such skill"))
        # ${CLAUDE_PLUGIN_ROOT} means whichever plugin is running, and the
        # transcript does not say which. Resolving under ANY configured tree
        # counts: a false finding here would be reported to the judge as fact.
        for m in ROOT_REF_RE.finditer(t.body):
            rel = m.group(1).rstrip(".,;:!?)\"'`")
            if not any((r / rel).exists() for r in roots.values()):
                out.append(Finding(t.number, "lint.unresolved-ref",
                                   f"${{CLAUDE_PLUGIN_ROOT}}/{rel} — no such file"))
    return out


def check_jargon(turns: list[Turn]) -> list[Finding]:
    out = []
    for t in turns:
        if t.role != "ASSISTANT":
            continue
        prose = strip_fences(t.body)
        masked = mask_shell_spans(prose)
        for label, rx in JARGON:
            hits = list(rx.finditer(masked))
            if not hits:
                continue
            times = f" ({len(hits)}×)" if len(hits) > 1 else ""
            out.append(Finding(t.number, "lint.jargon",
                               f"'{label}'{times} in user-facing text: "
                               f"\"{_quote(prose, hits[0].start())}\""))
    return out


def check_file_path(turns: list[Turn]) -> list[Finding]:
    """Plugin-owned filenames and `userdata/` paths in user-facing copy.

    Separate from lint.jargon so the two can be read apart: jargon is a term the
    user has no reason to know, this is the plugin narrating its own storage.
    One finding per turn per distinct token, so a turn that names four files
    reports four times rather than collapsing to one."""
    out = []
    for t in turns:
        if t.role != "ASSISTANT":
            continue
        prose = strip_fences(t.body)
        masked = mask_shell_spans(prose)
        seen: dict[str, int] = {}
        first: dict[str, int] = {}
        # Spans of every `userdata/...` path, so a filename sitting inside one
        # is not counted a second time. `userdata/outputs/daily-brief-x.md` is
        # one leak; reporting it as three (the path, the filename, and again as
        # a dated-brief match) overstates the turn and makes the count useless.
        paths = [(m.start(), m.end()) for m in USERDATA_PATH_RE.finditer(masked)]
        for rx in (USERDATA_PATH_RE, PLUGIN_FILE_RE):
            for m in rx.finditer(masked):
                token = m.group(0)
                if rx is PLUGIN_FILE_RE and any(s <= m.start() < e for s, e in paths):
                    continue  # already reported as the path it sits in
                seen[token] = seen.get(token, 0) + 1
                first.setdefault(token, m.start())
        for token in sorted(first, key=first.get):
            times = f" ({seen[token]}×)" if seen[token] > 1 else ""
            out.append(Finding(t.number, "lint.file-path",
                               f"'{token}'{times} named in user-facing text: "
                               f"\"{_quote(prose, first[token])}\""))
    return out


def snapshot_has_prior_state(snapshot: Path) -> bool:
    """Prior state = something a 'since last time' prompt could refer to: a
    dated journal entry, or any tracked company."""
    journal = snapshot / "journal.md"
    if journal.exists() and re.search(r"^## \d{4}-\d{2}-\d{2}", journal.read_text(),
                                      re.MULTILINE):
        return True
    companies = snapshot / "companies"
    if not companies.is_dir():
        return False
    return any(companies.glob("*/meta.md")) or any(companies.glob("*/*/meta.md"))


def check_prior_state_prompt(turns: list[Turn], snapshot: Path) -> list[Finding]:
    if snapshot_has_prior_state(snapshot):
        return []
    out = []
    for t in turns:
        if t.role != "ASSISTANT":
            continue
        prose = strip_fences(t.body)
        m = PRIOR_STATE_RE.search(prose)
        if m:
            out.append(Finding(t.number, "lint.prior-state-prompt",
                               f"prior-state prompt with no prior state "
                               f"(snapshot '{snapshot.name}'): "
                               f"\"{_quote(prose, m.start())}\""))
    return out


def _numbers_in(path: Path) -> set[str]:
    return set(re.findall(r"\b\d+\b", path.read_text())) if path.exists() else set()


def check_hardcoded_cadence(turns: list[Turn], userdata: Path) -> list[Finding]:
    """A cadence number is fine when it traces to the user's own plan. Allowed
    if it appears anywhere in strategy.md or profile.md — deliberately loose,
    because a false finding here costs more than a missed one."""
    allowed = _numbers_in(userdata / "strategy.md") | _numbers_in(userdata / "profile.md")
    out = []
    for t in turns:
        if t.role != "ASSISTANT":
            continue
        prose = mask_shell_spans(strip_fences(t.body))
        for m in CADENCE_RE.finditer(prose):
            if m.group(1) in allowed:
                continue
            out.append(Finding(t.number, "lint.hardcoded-cadence",
                               f"'{m.group(1)} {m.group(2)}' not in strategy.md "
                               f"or profile.md: \"{_quote(prose, m.start())}\""))
        for m in CLOCK_RE.finditer(prose):
            out.append(Finding(t.number, "lint.hardcoded-cadence",
                               f"hardcoded time of day: \"{_quote(prose, m.start())}\""))
    return out


def snapshot_name(text: str) -> str | None:
    """The '**Snapshot:** name' header, minus any parenthetical note — several
    corpus transcripts write 'maya-active (after Phase 2 backfill fix)'."""
    m = SNAPSHOT_RE.search(text)
    if not m:
        return None
    return re.sub(r"\s*\(.*\)\s*$", "", m.group(1)).strip() or None


def lint_transcript(text: str, plugin: Path | dict[str, Path],
                    snapshot: Path | None = None,
                    userdata: Path | None = None) -> tuple[list[Finding], list[str]]:
    """Returns (findings, names of rules that could not be checked).

    `plugin` is either the job-offer tree (its sibling `plugin-sweep` is
    inferred) or an explicit {namespace: root} map."""
    turns = parse_turns(text)
    roots = plugin if isinstance(plugin, dict) else default_roots(plugin)
    findings = (check_fenced_summary(turns)
                + check_unresolved_refs(turns, roots)
                + check_jargon(turns)
                + check_file_path(turns))
    skipped = []
    if snapshot is not None:
        findings += check_prior_state_prompt(turns, snapshot)
    else:
        skipped.append("lint.prior-state-prompt (no snapshot supplied)")
    if userdata is not None:
        findings += check_hardcoded_cadence(turns, userdata)
    else:
        skipped.append("lint.hardcoded-cadence (no userdata tree supplied)")
    findings.sort(key=lambda f: (f.turn, f.rule, f.detail))
    return findings, skipped


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    ap.add_argument("transcript")
    ap.add_argument("--plugin", default=str(root / "plugin"),
                    help="plugin/ tree used to resolve skill and file references")
    ap.add_argument("--snapshots", default=str(root / "tests" / "snapshots"),
                    help="directory of snapshot fixtures; the transcript's "
                         "'**Snapshot:**' header selects one")
    ap.add_argument("--snapshot", default=None,
                    help="explicit snapshot directory, overriding the header")
    ap.add_argument("--userdata", default=None,
                    help="userdata/ tree the run produced (enables cadence check)")
    try:
        args = ap.parse_args(argv[1:])
    except SystemExit:
        return 2

    tpath = Path(args.transcript)
    if not tpath.is_file():
        print(f"usage: lint_transcript.py <transcript.md>  (no such file: {tpath})",
              file=sys.stderr)
        return 2
    text = tpath.read_text()

    if args.snapshot:
        snapshot = Path(args.snapshot)
    else:
        name = snapshot_name(text)
        cand = Path(args.snapshots) / name if name else None
        snapshot = cand if cand and cand.is_dir() else None
    userdata = Path(args.userdata) if args.userdata else None
    if userdata is not None and not userdata.is_dir():
        print(f"usage: --userdata is not a directory: {userdata}", file=sys.stderr)
        return 2

    findings, skipped = lint_transcript(text, Path(args.plugin), snapshot, userdata)
    for f in findings:
        print(f"turn {f.turn}: {f.rule} — {f.detail}")
    if not findings:
        print("No lint findings.")
    for s in skipped:
        print(f"NOT CHECKED: {s}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
