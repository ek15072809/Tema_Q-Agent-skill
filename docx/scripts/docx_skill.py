"""docx_skill.py — Reusable building blocks for .docx generation.

Usage in other scripts:
    from docx_skill import (
        new_doc, setup_styles, add_toc, add_page_number,
        add_table, add_image, add_page_break, save,
    )
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Sequence

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ---- Document setup -------------------------------------------------------

def new_doc(page_size: str = "A4", margin_cm: float = 2.5,
            font_latin: str = "Calibri",
            font_cjk: str = "Noto Sans CJK JP",
            body_size_pt: int = 11) -> Document:
    """Create a Document with page setup and CJK-safe Normal style."""
    doc = Document()
    s = doc.sections[0]
    if page_size.upper() == "A4":
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    elif page_size.upper() == "LETTER":
        s.page_width, s.page_height = Cm(21.59), Cm(27.94)
    s.top_margin = s.bottom_margin = Cm(margin_cm)
    s.left_margin = s.right_margin = Cm(margin_cm)

    style = doc.styles['Normal']
    style.font.name = font_latin
    style.font.size = Pt(body_size_pt)
    # CJK font hint (mandatory for non-Latin glyphs)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), font_cjk)
    return doc


def setup_styles(doc: Document,
                 h1_pt: int = 18, h2_pt: int = 14, h3_pt: int = 12,
                 body_pt: int = 11,
                 text_color_hex: str = "1A1A1A") -> None:
    """Apply a consistent heading hierarchy."""
    rgb = RGBColor.from_string(text_color_hex)
    for name, size in (("Heading 1", h1_pt), ("Heading 2", h2_pt),
                        ("Heading 3", h3_pt)):
        st = doc.styles[name]
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = rgb

    normal = doc.styles['Normal']
    normal.font.size = Pt(body_pt)
    pf = normal.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)


# ---- Auto-updating Table of Contents -------------------------------------

def add_toc(doc: Document, levels: str = "1-3") -> None:
    """Insert a TOC field. Word will populate it on F9 / open."""
    p = doc.add_paragraph()
    _add_field(p, f'TOC \\o "{levels}" \\h \\z \\u')
    note = p.add_run("(Press F9 in Word to refresh the TOC)")
    note.font.color.rgb = RGBColor(0x99, 0x99, 0x99)


def _add_field(paragraph, instr: str) -> None:
    """Helper to insert a Word field (PAGE, TOC, etc.)."""
    for kind in ("begin",):
        run = paragraph.add_run()
        fc = OxmlElement('w:fldChar')
        fc.set(qn('w:fldCharType'), kind)
        run._r.append(fc)
    run = paragraph.add_run()
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = instr
    run._r.append(it)
    run = paragraph.add_run()
    fc = OxmlElement('w:fldChar')
    fc.set(qn('w:fldCharType'), 'separate')
    run._r.append(fc)
    run = paragraph.add_run()
    fc = OxmlElement('w:fldChar')
    fc.set(qn('w:fldCharType'), 'end')
    run._r.append(fc)


# ---- Header / Footer with page numbers -----------------------------------

def add_page_number_footer(doc: Document,
                           align=WD_ALIGN_PARAGRAPH.CENTER) -> None:
    """Add 'Page X' to the footer of the first section."""
    section = doc.sections[0]
    p = section.footer.paragraphs[0]
    p.alignment = align
    _add_field(p, "PAGE")


def add_header_text(doc: Document, text: str,
                    align=WD_ALIGN_PARAGRAPH.RIGHT) -> None:
    """Add a header string to the first section."""
    section = doc.sections[0]
    p = section.header.paragraphs[0]
    p.alignment = align
    p.add_run(text)


# ---- Tables & images -----------------------------------------------------

def add_table(doc: Document,
              headers: Sequence[str],
              rows: Iterable[Sequence[object]],
              style: str = "Light Grid Accent 1") -> None:
    """Add a styled table with a bold header row."""
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = style
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = str(h)
        for p in hdr[i].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.bold = True

    for row in rows:
        cells = table.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)


def add_image(doc: Document, path: str | Path,
              width_cm: float = 12.0,
              align=WD_ALIGN_PARAGRAPH.CENTER) -> None:
    """Insert an image at a fixed width, aligned."""
    doc.add_picture(str(path), width=Cm(width_cm))
    doc.paragraphs[-1].alignment = align


def add_page_break(doc: Document) -> None:
    doc.add_page_break()


# ---- Save -----------------------------------------------------------------

def save(doc: Document, filename: str,
         out_dir: str = "/home/z/my-project/download") -> Path:
    """Save under the canonical download dir and return the path."""
    p = Path(out_dir) / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    doc.save(p)
    return p


# ---- Self-test / demo ----------------------------------------------------

if __name__ == "__main__":
    doc = new_doc()
    setup_styles(doc)
    add_header_text(doc, "Demo Document")
    add_page_number_footer(doc)

    doc.add_heading("Demo Report", level=0)
    add_toc(doc)
    add_page_break(doc)

    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph("This is a demo paragraph generated by docx_skill.py.")

    add_table(doc,
              headers=["Item", "Qty", "Price"],
              rows=[("Widget", 3, "$9.99"),
                    ("Gadget", 1, "$49.00")])

    out = save(doc, "docx_skill_demo.docx")
    print(f"Saved: {out}")
