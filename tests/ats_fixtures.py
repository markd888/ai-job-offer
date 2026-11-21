"""Builds synthetic DOCX CVs for the ATS tests — no binary fixtures in the repo.

A .docx is a zip of WordprocessingML. make_docx writes the minimum Word and
the stdlib reader both accept: [Content_Types].xml, word/document.xml and,
when asked, header/footer parts and docProps/app.xml (page count).

Body items: a str is a paragraph; a list of lists is a table (rows of cells);
{"text_box": "…"} is a paragraph holding a text box, written the way Word
does it — once in mc:Choice and again in mc:Fallback.
"""
from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
      'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
      'xmlns:v="urn:schemas-microsoft-com:vml"')


def _p(text: str) -> str:
    return f'<w:p><w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def _tbl(rows: list[list[str]]) -> str:
    trs = "".join("<w:tr>" + "".join(f"<w:tc>{_p(c)}</w:tc>" for c in row) + "</w:tr>" for row in rows)
    return f"<w:tbl>{trs}</w:tbl>"


def _text_box(text: str) -> str:
    inner = "".join(_p(line) for line in text.splitlines())
    return ("<w:p><w:r><mc:AlternateContent>"
            f"<mc:Choice Requires=\"wps\"><w:drawing><wps:txbx><w:txbxContent>{inner}</w:txbxContent></wps:txbx></w:drawing></mc:Choice>"
            f"<mc:Fallback><w:pict><v:textbox><w:txbxContent>{inner}</w:txbxContent></v:textbox></w:pict></mc:Fallback>"
            "</mc:AlternateContent></w:r></w:p>")


def make_docx(path: Path, body: list, header: list[str] | None = None,
              footer: list[str] | None = None, pages: int | None = 1) -> Path:
    parts = []
    for item in body:
        if isinstance(item, str):
            parts.append(_p(item))
        elif isinstance(item, dict):
            parts.append(_text_box(item["text_box"]))
        else:
            parts.append(_tbl(item))
    files = {
        "[Content_Types].xml": '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                               '<Default Extension="xml" ContentType="application/xml"/></Types>',
        "word/document.xml": f'<?xml version="1.0"?><w:document {NS}><w:body>{"".join(parts)}</w:body></w:document>',
    }
    if header:
        files["word/header1.xml"] = f'<?xml version="1.0"?><w:hdr {NS}>{"".join(map(_p, header))}</w:hdr>'
    if footer:
        files["word/footer1.xml"] = f'<?xml version="1.0"?><w:ftr {NS}>{"".join(map(_p, footer))}</w:ftr>'
    if pages is not None:
        files["docProps/app.xml"] = f'<?xml version="1.0"?><Properties><Pages>{pages}</Pages></Properties>'
    with zipfile.ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)
    return path


# --- The ten synthetic cases from #38 --------------------------------------------
#
# build_case(name, folder) -> (cv_path, md_text). PDFs use reportlab's built-in
# fonts (no font install), DOCX uses make_docx. Every person, company and
# contact is fictional.

CASE_MD = """# ALEX EXAMPLE
Lisbon, Portugal | +351 912 111 222 | alex@example.com

## PROFESSIONAL SUMMARY
Senior product manager for payment orchestration and merchant onboarding.

## WORK EXPERIENCE

### SENIOR PRODUCT MANAGER, Payments | Paycorp — Lisbon
*2024 – Present*
- Unified PSP integrations into one framework and cut merchant onboarding time.
- Built reconciliation tooling with the finance team.

### PRODUCT MANAGER | Ledgerly — Porto
*2020 – 2023*
- Launched approval-rate dashboards and decline analysis for card payments.

## PROFESSIONAL SKILLS

**Payments:** PSP integrations, reconciliation, chargebacks

**Data:** SQL, Grafana

## EDUCATION

### MSc Computer Science | Example University
*2014 – 2019*
"""

CASES = ("clean-pdf", "two-column-pdf", "icon-contacts-pdf", "broken-glyphs-pdf", "reading-order-pdf",
         "no-contacts-pdf", "plain-docx", "tables-docx", "undated-pdf", "skills-only-pdf")


def case_lines(md: str = CASE_MD) -> list[str]:
    out = []
    for ln in md.splitlines():
        s = ln.strip()
        if not s:
            continue
        s = s.lstrip("#").strip()
        s = s.strip("*").replace("**", "")
        s = s[2:] if s.startswith("- ") else s
        out.append(s)
    return out


def _pdf(path: Path, rows: list[tuple[float, float, str, str]]) -> Path:
    """rows: (x, y, text, font), drawn in the given order (= text-stream order)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(path), pagesize=A4)
    for x, y, text, font in rows:
        c.setFont(font, 9)
        c.drawString(x, y, text)
    c.save()
    return path


def _column(lines: list[str], x: float = 40, top: float = 800, font: str = "Helvetica"):
    return [(x, top - 13 * i, ln, font) for i, ln in enumerate(lines)]


def build_case(name: str, folder: Path) -> tuple[Path, str]:
    md = CASE_MD
    lines = case_lines(md)
    if name == "clean-pdf":
        return _pdf(folder / f"{name}.pdf", _column(lines)), md
    if name == "two-column-pdf":
        edu = lines.index("EDUCATION")
        skills = lines.index("PROFESSIONAL SKILLS")
        main = lines[:skills]
        side = [f"{ln} (sidebar line {i})" if len(ln) < 21 else ln for i, ln in enumerate(lines[skills:])]
        rows = []
        for i in range(max(len(main), len(side))):   # stream interleaves the columns row by row
            if i < len(main):
                rows.append((40, 800 - 13 * i, main[i], "Helvetica"))
            if i < len(side):
                rows.append((340, 800 - 13 * i, side[i], "Helvetica"))
        return _pdf(folder / f"{name}.pdf", rows), md
    if name == "icon-contacts-pdf":
        rows = _column(lines)
        rows.insert(1, (30, 787, "(", "ZapfDingbats"))   # an icon glyph beside the contact line
        return _pdf(folder / f"{name}.pdf", rows), md
    if name == "broken-glyphs-pdf":
        # A real (cid:N) layer needs a broken font; the text layer is crafted instead (see text_case).
        return _pdf(folder / f"{name}.pdf", _column(lines)), md
    if name == "reading-order-pdf":
        edu = lines.index("EDUCATION")
        order = lines[edu:] + lines[:edu]              # education drawn first in the stream…
        y = {ln: 800 - 13 * i for i, ln in enumerate(lines)}
        return _pdf(folder / f"{name}.pdf", [(40, y[ln], ln, "Helvetica") for ln in order]), md  # …but at the bottom
    if name == "no-contacts-pdf":
        return _pdf(folder / f"{name}.pdf", _column([lines[0], *lines[2:]])), md
    if name == "plain-docx":
        return make_docx(folder / f"{name}.docx", lines), md
    if name == "tables-docx":
        body = [lines[0], [["Lisbon, Portugal", "+351 912 111 222", "alex@example.com"]], *lines[2:]]
        return make_docx(folder / f"{name}.docx", body), md
    if name == "undated-pdf":
        md = md.replace("*2020 – 2023*\n", "")
        return _pdf(folder / f"{name}.pdf", _column(case_lines(md))), md
    if name == "skills-only-pdf":
        md = md.replace("**Data:** SQL, Grafana", "**Data:** SQL, Grafana, Kubernetes, Kafka")
        return _pdf(folder / f"{name}.pdf", _column(case_lines(md))), md
    raise ValueError(name)
