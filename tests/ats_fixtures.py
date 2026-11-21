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
