"""Readability and layout observations for ats-check.py (#38 phase 5).

Not a CLI — ats-check.py loads this file by path (scripts run with `python3 -I`).

Every item is an *observation* from the extracted text layer — where text sat,
which fonts drew it, what the DOCX keeps outside the body — never a claim that
a given ATS can't read the file. Each is {"risk", "observed"}.

PDF positions come from pypdf's text visitor; without pypdf (pdftotext only)
the position-based checks are skipped and the report says so.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ICON_FONT = re.compile(r"awesome|icon|symbol|wingding|dingbat|material|glyph", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
COLUMN_GAP = 120      # points between two left margins to count as separate columns
COLUMN_MIN_LINES = 5  # lines starting at a margin before it counts as a column


def pdf_lines(pdf: Path) -> list[dict] | None:
    """[{page, x, y, text, font}] per visual line, or None when pypdf isn't available."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    out: list[dict] = []
    for pno, page in enumerate(PdfReader(str(pdf)).pages, 1):
        height = float(page.mediabox.height)
        chunks: list[tuple[float, float, str, str]] = []

        def visit(text, cm, tm, font, size, _c=chunks):
            if not text or not text.strip():
                return
            x = cm[0] * tm[4] + cm[2] * tm[5] + cm[4]
            y = cm[1] * tm[4] + cm[3] * tm[5] + cm[5]
            name = str((font or {}).get("/BaseFont", "")).lstrip("/")
            _c.append((round(y, 1), x, text.strip(), name))

        page.extract_text(visitor_text=visit)
        rows: dict[float, list] = defaultdict(list)
        for y, x, t, f in chunks:
            rows[round(y / 2) * 2].append((x, t, f))
        for y, items in rows.items():
            items.sort()
            # split a visual row where a big horizontal jump separates two columns
            groups, cur = [], [items[0]]
            for prev, it in zip(items, items[1:]):
                if it[0] - prev[0] > COLUMN_GAP and len(prev[1]) * 4 < it[0] - prev[0]:
                    groups.append(cur); cur = [it]
                else:
                    cur.append(it)
            groups.append(cur)
            for g in groups:
                out.append({"page": pno, "x": round(g[0][0]), "y": y, "top": 1 - y / height,
                            "text": " ".join(t for _, t, _ in g), "font": g[0][2]})
    return out


def _columns(lines: list[dict]) -> list[dict]:
    out = []
    for page in sorted({ln["page"] for ln in lines}):
        # Short items (right-aligned dates, page numbers) aren't a column of text.
        pl = [ln for ln in lines if ln["page"] == page and len(ln["text"]) > 20]
        bins: dict[int, list[dict]] = defaultdict(list)
        for ln in pl:
            bins[round(ln["x"] / 20) * 20].append(ln)
        margins = sorted(x for x, ls in bins.items() if len(ls) >= COLUMN_MIN_LINES)
        far = [x for x in margins if x - margins[0] >= COLUMN_GAP] if margins else []
        if not far:
            continue
        left = {round(ln["y"]) for ln in bins[margins[0]]}
        right_lines = [ln for x in far for ln in bins[x]]
        shared = sum(1 for ln in right_lines if any(abs(round(ln["y"]) - y) <= 2 for y in left))
        lo, hi = min(ln["y"] for ln in right_lines), max(ln["y"] for ln in right_lines)
        overlap = sum(1 for ln in bins[margins[0]] if lo <= ln["y"] <= hi)
        if shared >= 3 or overlap >= COLUMN_MIN_LINES:
            out.append({"risk": "multi-column layout",
                        "observed": f"page {page}: {len(bins[margins[0]])} lines start at x≈{margins[0]}pt and "
                                    f"{len(right_lines)} at x≈{far[0]}pt over the same stretch of the page "
                                    f"({shared} rows share a line) — a parser reading left to right can interleave them"})
    return out


def _repeated_edges(lines: list[dict]) -> list[dict]:
    pages = {ln["page"] for ln in lines}
    if len(pages) < 2:
        return []
    edge = defaultdict(set)
    for ln in lines:
        if ln["top"] < 0.07 or ln["top"] > 0.93:
            edge[re.sub(r"\d+", "#", ln["text"].lower())].add(ln["page"])
    rep = [t for t, ps in edge.items() if len(ps) >= 2]
    if not rep:
        return []
    return [{"risk": "running header or footer",
             "observed": f"{len(rep)} line(s) repeat at the top or bottom of every page, e.g. \"{rep[0][:50]}\" — "
                         "some parsers read them into the entry they interrupt"}]


def _fonts(lines: list[dict]) -> list[dict]:
    icons = sorted({ln["font"] for ln in lines if ln["font"] and ICON_FONT.search(ln["font"])})
    if not icons:
        return []
    return [{"risk": "icon font",
             "observed": f"text drawn in {', '.join(icons)} — icons there usually stand in for words "
                         "(a phone or envelope glyph), which extract as nothing or as stray characters"}]


def _contacts_pdf(lines: list[dict]) -> list[dict]:
    hit = next((ln for ln in lines if EMAIL.search(ln["text"])), None)
    if hit and (hit["page"] > 1 or hit["top"] > 0.25):
        where = f"page {hit['page']}" if hit["page"] > 1 else f"{hit['top']:.0%} of the way down page 1"
        return [{"risk": "contact block placement",
                 "observed": f"the email first appears {where} — parsers look for contacts at the top"}]
    return []


def observe_pdf(pdf: Path) -> tuple[list[dict], list[str]]:
    """(observations, notes about what couldn't be checked)."""
    lines = pdf_lines(pdf) if pdf.is_file() else None
    if lines is None:
        return [], ["Text positions need pypdf; column, header/footer, font and contact-placement checks were skipped."]
    fonts = sorted({ln["font"] for ln in lines if ln["font"]})
    notes = [f"Fonts in the text layer: {', '.join(fonts)}."] if fonts else []
    return _columns(lines) + _repeated_edges(lines) + _fonts(lines) + _contacts_pdf(lines), notes


def observe_docx(parts: dict) -> list[dict]:
    out = []
    if parts.get("tables"):
        out.append({"risk": "tables", "observed": f"{len(parts['tables'])} table row(s) — read here row by row with "
                                                  "cells joined by '|'; parsers differ on table order"})
    if parts.get("text_boxes"):
        out.append({"risk": "text boxes", "observed": f"{len(parts['text_boxes'])} text box(es), e.g. "
                                                      f"\"{parts['text_boxes'][0][:50]}\" — they sit outside the "
                                                      "body's reading order and are often skipped"})
    for kind in ("headers", "footers"):
        lines = parts.get(kind) or []
        if any(EMAIL.search(x) or re.search(r"\+?\d[\d\s().-]{7,}\d", x) for x in lines):
            out.append({"risk": "contact block placement",
                        "observed": f"contact details are in the document {kind[:-1]} — many parsers skip "
                                    f"{kind}, so they may not reach the profile"})
        elif lines:
            out.append({"risk": f"running {kind[:-1]}", "observed": f"{len(lines)} line(s) in the {kind[:-1]}, "
                                                                    f"e.g. \"{lines[0][:50]}\""})
    return out


def observe_text(sections: list[str], md_headings: list[str], section_of) -> list[dict]:
    """Headings parsers wouldn't recognise as a section kind (from the CV markdown when given)."""
    pool = md_headings or sections
    odd = [h for h in pool if section_of(h) is None]
    if not odd:
        return []
    return [{"risk": "non-standard headings",
             "observed": f"{', '.join(odd)} — not a section name parsers know; entries under it may be filed nowhere"}]
