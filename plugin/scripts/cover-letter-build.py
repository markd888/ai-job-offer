#!/usr/bin/env python3
"""Cover letter PDF in the same look as cv-build.py.

Usage:
  python3 -I cover-letter-build.py <letter.md> <out.pdf> --cv <cv.md> [font-size 10.5] [leading-factor 1.3]

The name and contact line come from the top of the CV markdown (the "# NAME"
line and the line after it), so the letter and the CV always match.
Paragraphs in <letter.md> are separated by blank lines; ReportLab inline tags
(<b>, <i>) are allowed.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path

from reportlab.lib.colors import HexColor, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate

# Fonts, inline markdown and contact links are shared with the CV builder.
_spec = importlib.util.spec_from_file_location("cv_build", Path(__file__).with_name("cv-build.py"))
cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cv)

ap = argparse.ArgumentParser()
ap.add_argument("letter")
ap.add_argument("out")
ap.add_argument("--cv", required=True, help="tailored CV markdown; its header is reused")
ap.add_argument("font_size", nargs="?", type=float, default=10.5)
ap.add_argument("leading", nargs="?", type=float, default=1.3)
a = ap.parse_args()

FS, LD = a.font_size, a.font_size * a.leading
md = Path(a.cv).read_text(encoding="utf-8")
m = re.search(r"^# (.+)\n+(.+)$", md, re.M)
if not m:
    raise SystemExit("CV markdown has no '# NAME' line followed by a contact line.")
who, contact_line = m.group(1).strip(), m.group(2).strip()

GREY = HexColor("#666666")
name = ParagraphStyle("n", fontName="Carlito-Bold", fontSize=21, leading=24, alignment=1)
contact = ParagraphStyle("c", fontName="Carlito", fontSize=9.6, leading=12, alignment=1, textColor=GREY)
body = ParagraphStyle("b", fontName="Carlito", fontSize=FS, leading=LD, spaceAfter=FS * 0.8)

story = [
    Paragraph(cv.inline(who), name),
    Paragraph(cv.linkify(cv.inline(contact_line)), contact),
    HRFlowable(width="100%", thickness=0.8, color=black, spaceBefore=6, spaceAfter=18),
]
paras = [p.strip() for p in Path(a.letter).read_text(encoding="utf-8").split("\n\n") if p.strip()]
for p in paras:
    story.append(Paragraph(p.replace("&", "&amp;").replace("\n", "<br/>"), body))

author = who.title()
doc = SimpleDocTemplate(a.out, pagesize=A4, leftMargin=54, rightMargin=54, topMargin=28, bottomMargin=28,
                        title=f"{author} — Cover letter", author=author)
doc.build(story)
