#!/usr/bin/env python3
"""Build a one-page CV PDF from a tailored CV markdown file.

The markdown is the source of truth; this script only lays it out (reportlab +
the Carlito font, single column, plain text layer an ATS can read).

  # NAME                          -> name line
  first line after it            -> contact line (emails and URLs become links)
  ## SECTION                     -> section heading with a rule
  ### Title | Company — Place    -> role row; the part before " | " is bold
  *2024 – 2025*                  -> dates, right-aligned on the role row
  plain line right after a role  -> italic one-line context under the role
  - bullet                       -> bullet
  anything else                  -> paragraph
  **bold**, *italic*             -> inline styles

Usage:
  python3 -I cv-build.py <cv.md> <out.pdf> [font-size 9] [leading-factor 1.15]

Needs reportlab and the Carlito font (macOS: ~/Library/Fonts, Linux:
fonts-crosextra-carlito). Check the result with ats-check.py.
"""
from __future__ import annotations

import os
import re
import sys

from reportlab.lib.colors import HexColor, black
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Table, TableStyle

FONT_DIRS = [os.path.expanduser("~/Library/Fonts/"), "/Library/Fonts/", "/usr/share/fonts/truetype/crosextra/"]
F = next((d for d in FONT_DIRS if os.path.exists(d + "Carlito-Regular.ttf")), None)
if F is None:
    sys.exit("Carlito font not found: install it (macOS: Font Book; Linux: fonts-crosextra-carlito).")
for style, suffix in [("Carlito", "Regular"), ("Carlito-Bold", "Bold"), ("Carlito-Italic", "Italic"), ("Carlito-BoldItalic", "BoldItalic")]:
    pdfmetrics.registerFont(TTFont(style, F + f"Carlito-{suffix}.ttf"))
addMapping("Carlito", 0, 0, "Carlito"); addMapping("Carlito", 1, 0, "Carlito-Bold")
addMapping("Carlito", 0, 1, "Carlito-Italic"); addMapping("Carlito", 1, 1, "Carlito-BoldItalic")



def _num(i: int, default: float) -> float:
    try:
        return float(sys.argv[i])
    except (IndexError, ValueError):
        return default


FS = _num(3, 9.0)
LD = FS * _num(4, 1.15)
GREY = HexColor("#666666"); LINK = "#1a55b8"
name_s = ParagraphStyle("n", fontName="Carlito-Bold", fontSize=21, leading=24, alignment=1)
contact_s = ParagraphStyle("c", fontName="Carlito", fontSize=FS, leading=LD + 1, alignment=1, textColor=GREY)
h_s = ParagraphStyle("h", fontName="Carlito-Bold", fontSize=FS + 2.4, leading=FS + 3.5, spaceBefore=2)
body = ParagraphStyle("b", fontName="Carlito", fontSize=FS, leading=LD)
ital = ParagraphStyle("i", parent=body, fontName="Carlito-Italic", textColor=GREY)
right = ParagraphStyle("r", parent=body, fontName="Carlito-Bold", alignment=2)
W = A4[0] - 2 * 36 - 12  # frame inner width (6pt padding each side)


def inline(s: str) -> str:
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)


def linkify(s: str) -> str:
    def mail(m):
        return f'<link href="mailto:{m.group(0)}" color="{LINK}"><u>{m.group(0)}</u></link>'

    def url(m):
        href = m.group(0) if m.group(0).startswith("http") else "https://" + m.group(0)
        return f'<link href="{href}" color="{LINK}"><u>{m.group(0)}</u></link>'

    parts = []
    for part in s.split(" | "):
        if "@" in part:
            part = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", mail, part)
        elif re.match(r"(https?://)?([\w-]+\.)+[a-z]{2,}(/\S*)?$", part.strip()):
            part = re.sub(r"\S+", url, part)
        parts.append(part)
    return " | ".join(parts)


def build(md: str, out: str) -> None:
    lines = md.splitlines()
    story: list = []
    bullets: list[str] = []
    pending_role: str | None = None
    after_role = False
    contact_done = False

    def flush_bullets():
        if bullets:
            story.append(ListFlowable([ListItem(Paragraph(b, body), leftIndent=10, value="•") for b in bullets],
                                      bulletType="bullet", start="•", leftIndent=10, bulletFontSize=FS - 1, bulletOffsetY=-0.5))
            bullets.clear()

    def flush_role(dates: str = ""):
        nonlocal pending_role
        if pending_role is not None:
            t = Table([[Paragraph(pending_role, body), Paragraph(dates, right)]], colWidths=[W - 90, 90])
            t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                   ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
            story.append(t)
            pending_role = None

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:].strip()), name_s))
            continue
        if story and not contact_done and not line.startswith("#"):
            story.append(Paragraph(linkify(inline(line)), contact_s))
            contact_done = True
            continue
        contact_done = True
        if line.startswith("## "):
            flush_bullets(); flush_role()
            story.append(Paragraph(inline(line[3:].strip()), h_s))
            story.append(HRFlowable(width="100%", thickness=0.8, color=black, spaceBefore=1, spaceAfter=2))
            after_role = False
            continue
        if line.startswith("### "):
            flush_bullets(); flush_role()
            title, sep, rest = line[4:].strip().partition(" | ")
            pending_role = f"<b>{inline(title)}</b>" + (f" | {inline(rest)}" if sep else "")
            after_role = True
            continue
        m = re.fullmatch(r"\*([^*]+)\*", line)
        if m and pending_role is not None:
            flush_role(inline(m.group(1)))
            continue
        flush_role()
        if line.startswith(("- ", "* ")):
            bullets.append(inline(line[2:].strip()))
            after_role = False
            continue
        flush_bullets()
        story.append(Paragraph(inline(line), ital if after_role else body))
        after_role = False
    flush_bullets(); flush_role()

    title = re.search(r"^# (.+)$", md, re.M)
    who = title.group(1).strip().title() if title else ""
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=20, bottomMargin=16,
                            title=f"{who} — CV".strip(" —"), author=who)
    doc.build(story)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    build(open(sys.argv[1], encoding="utf-8").read(), sys.argv[2])
