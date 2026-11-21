"""Text extraction for ats-check.py: PDF (pypdf, then pdftotext) and DOCX (stdlib).

Not a CLI — ats-check.py loads this file by path (scripts run with `python3 -I`).

`extract(path)` returns an Extraction dict:

  format       "pdf" | "docx"
  engine       "pypdf" | "pdftotext" | "docx-xml"
  text         everything a parser could read, in reading order
  pages        page count, or None when the file doesn't say (DOCX without app.xml)
  parts        DOCX only: {"body", "tables", "headers", "footers", "text_boxes"},
               each a list of strings, so a later check can say *where* text sat
  limitations  what this extraction can't see, in plain words

DOCX is a zip of WordprocessingML; reading it needs only zipfile + xml.etree,
so there is no new dependency.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
DOCX_LIMITATIONS = [
    "Images, charts and SmartArt are not read — text inside them is invisible here, as it is to most parsers.",
    "Text boxes are listed after the body; where they sit on the page isn't known.",
    "Headers and footers are read, but many parsers skip them — contact details there are a risk.",
    "Footnotes, comments and tracked changes are ignored.",
]


def extract_pdf(pdf: Path, engine: str | None = None) -> tuple[str, int, str]:
    """(text, pages, engine). engine None = pypdf, falling back to pdftotext."""
    if engine in (None, "pypdf"):
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(pdf))
            return "\n".join(p.extract_text() or "" for p in reader.pages), len(reader.pages), "pypdf"
        except ImportError:
            if engine == "pypdf":
                raise
    if not shutil.which("pdftotext"):
        sys.exit("No text extractor: install pypdf (pip install pypdf) or poppler (pdftotext).")
    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    pages = text.count("\f") or 1
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", info, re.M)
        pages = int(m.group(1)) if m else pages
    return text, pages, "pdftotext"


def _run_text(el: ET.Element) -> str:
    """Text of one paragraph, skipping text boxes nested inside it and mc:Fallback copies."""
    out: list[str] = []

    def walk(e: ET.Element) -> None:
        if e.tag in (W + "txbxContent", MC + "Fallback"):
            return
        if e.tag == W + "t":
            out.append(e.text or "")
        elif e.tag == W + "tab":
            out.append("\t")
        elif e.tag in (W + "br", W + "cr"):
            out.append("\n")
        for c in e:
            walk(c)

    walk(el)
    return "".join(out)


def _table(tbl: ET.Element) -> list[str]:
    """One line per row, cells joined with ' | ' — the order a parser reads them."""
    rows = []
    for tr in tbl.iter(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            cells.append(" ".join(t for t in (_run_text(p).strip() for p in tc.iter(W + "p")) if t))
        rows.append(" | ".join(cells))
    return rows


def _text_boxes(root: ET.Element) -> list[str]:
    boxes = []
    for fb in root.iter(MC + "Fallback"):  # mark the duplicates so they're skipped
        for tx in fb.iter(W + "txbxContent"):
            tx.set("_dup", "1")
    for tx in root.iter(W + "txbxContent"):
        if tx.get("_dup"):
            continue
        t = "\n".join(s for s in (_run_text(p).strip() for p in tx.iter(W + "p")) if s)
        if t:
            boxes.append(t)
    return boxes


def _part_lines(root: ET.Element) -> list[str]:
    return [s for s in (_run_text(p).strip() for p in root.iter(W + "p")) if s]


def extract_docx(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        doc = ET.fromstring(z.read("word/document.xml"))
        headers = [ET.fromstring(z.read(n)) for n in sorted(names) if re.fullmatch(r"word/header\d*\.xml", n)]
        footers = [ET.fromstring(z.read(n)) for n in sorted(names) if re.fullmatch(r"word/footer\d*\.xml", n)]
        pages = None
        if "docProps/app.xml" in names:
            m = re.search(rb"<Pages>(\d+)</Pages>", z.read("docProps/app.xml"))
            pages = int(m.group(1)) if m else None

    body_el = doc.find(W + "body")
    body: list[str] = []
    tables: list[str] = []
    for child in (body_el if body_el is not None else []):
        if child.tag == W + "p":
            t = _run_text(child).strip()
            if t:
                body.append(t)
        elif child.tag == W + "tbl":
            rows = _table(child)
            tables += rows
            body += rows
    boxes = _text_boxes(doc)
    head = [line for h in headers for line in _part_lines(h)]
    foot = [line for f in footers for line in _part_lines(f)]
    text = "\n".join(head + body + boxes + foot)
    limitations = list(DOCX_LIMITATIONS)
    if pages is None:
        limitations.append("The file doesn't record its page count, so the page check is skipped.")
    return {"format": "docx", "engine": "docx-xml", "text": text, "pages": pages,
            "parts": {"body": body, "tables": tables, "headers": head, "footers": foot, "text_boxes": boxes},
            "limitations": limitations}


def extract(path: Path) -> dict:
    """Pick the extractor by file suffix."""
    if path.suffix.lower() == ".docx":
        return extract_docx(path)
    text, pages, engine = extract_pdf(path)
    return {"format": "pdf", "engine": engine, "text": text, "pages": pages, "parts": {}, "limitations": []}
