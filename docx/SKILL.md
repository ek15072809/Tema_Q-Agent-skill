---
name: docx
description: Generate advanced Microsoft Word (.docx) files with python-docx. Includes TOC, styles, tables, images, headers/footers, sections, formulas. Use for any real document-generation task.
---

# DOCX Skill

## Overview
Generate `.docx` files with the `python-docx` library.
Output path: `/home/z/my-project/download/<filename>.docx`

## Required Library
```bash
pip install python-docx
```

## Bundled Helper Module
**`skill/docx/scripts/docx_skill.py`** provides reusable helpers:
`new_doc`, `setup_styles`, `add_toc`, `add_page_number_footer`,
`add_header_text`, `add_table`, `add_image`, `add_page_break`, `save`.

Import it instead of inlining the templates below:
```python
import sys; sys.path.insert(0, "skill/docx/scripts")
from docx_skill import new_doc, setup_styles, add_toc, add_table, save
```
Run `python skill/docx/scripts/docx_skill.py` to write a demo file and verify the install.

## Standard Template

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# Page setup (A4)
section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

# CJK font setup (mandatory for non-Latin text)
style = doc.styles['Normal']
style.font.name = 'Noto Sans CJK JP'  # or 'Yu Gothic', 'MS Gothic'
style.font.size = Pt(11)
style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Noto Sans CJK JP')
```

## Style Hierarchy (mandatory)

```python
def setup_styles(doc):
    # Heading 1: 18pt bold
    h1 = doc.styles['Heading 1']
    h1.font.size = Pt(18)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)

    # Heading 2: 14pt bold
    h2 = doc.styles['Heading 2']
    h2.font.size = Pt(14)
    h2.font.bold = True

    # Heading 3: 12pt bold
    h3 = doc.styles['Heading 3']
    h3.font.size = Pt(12)
    h3.font.bold = True

    # Normal: 11pt
    normal = doc.styles['Normal']
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
```

## Auto-Generated Table of Contents

```python
def add_toc(doc):
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)

    run = paragraph.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    run._r.append(instrText)

    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'separate')
    run._r.append(fldChar)

    run = paragraph.add_run("(Press F9 in Word to refresh the TOC)")
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)
```

## Header & Footer (with page numbers)

```python
def add_page_number(doc):
    section = doc.sections[0]
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = p.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)

    run = p.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.text = "PAGE"
    run._r.append(instrText)

    run = p.add_run()
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar2)
```

## Bordered Table

```python
def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for p in hdr[i].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.bold = True

    for row in rows:
        cells = table.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
```

## Image Insertion

```python
def add_image(doc, path, width_cm=12):
    doc.add_picture(path, width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
```

## Page Break

```python
def add_page_break(doc):
    doc.add_page_break()
```

## Full Workflow

1. **Clarify requirements**: doc type (report / proposal / paper / manual), length, required sections
2. **Design structure**: title → TOC → intro → body → conclusion → appendix
3. **Generate script**: save as `/home/z/my-project/scripts/gen_<name>.py`
4. **Run**: `python scripts/gen_<name>.py`
5. **Verify**: file size, page count, TOC links

## Output Rules (mandatory)

- Always save scripts to `/home/z/my-project/scripts/gen_<name>.py` before running
- Output path: `/home/z/my-project/download/<filename>.docx`
- Always set CJK fonts explicitly (defaults to Latin fonts otherwise)
- Use page breaks only at chapter boundaries (no arbitrary breaks)
- Lists must be left-aligned (no justified — avoids stretched line-ends)
- Each paragraph ≥ 3–5 sentences; each heading ≥ 150–200 words of body (prevents thin content)

## Doc-Type Templates

### Report
1. Cover (title, date, author)
2. TOC
3. Executive summary (1 page)
4. Background & purpose
5. Methodology
6. Results & discussion
7. Conclusion & recommendations
8. Appendix (data, references)

### Proposal
1. Cover
2. TOC
3. Introduction
4. Current challenges
5. Proposal details
6. Implementation schedule
7. Cost & expected effect
8. Company overview

### Academic Paper
1. Title, author, affiliation
2. Abstract
3. Introduction
4. Related work
5. Methodology
6. Results
7. Discussion
8. Conclusion
9. References

## Common Pitfalls

| Pitfall | Cause | Fix |
|---|---|---|
| CJK glyphs render as □□□ | Font not set | Must use `rFonts.set(qn('w:eastAsia'), ...)` |
| Empty TOC | Word must refresh it client-side | Tell user to press F9 |
| Page breaks in odd places | Arbitrary page breaks | Use only at chapter boundaries |
| Table overflows page | Column widths not set | `table.columns[i].width = Cm(x)` |
| Image too large | Width not set | Specify `width=Cm(12)` etc. |
