---
name: pptx
description: Generate advanced Microsoft PowerPoint (.pptx) files with python-pptx. Master layouts, tables, charts, shapes, animations. Use for any real slide-deck generation task.
---

# PPTX Skill

## Overview
Generate `.pptx` files with the `python-pptx` library.
Output path: `/home/z/my-project/download/<filename>.pptx`

## Required Library
```bash
pip install python-pptx
```

## Bundled Helper Module
**`skill/pptx/scripts/pptx_skill.py`** provides reusable builders:
`new_deck`, `cover_slide`, `section_slide`, `bullet_slide`,
`image_text_slide`, `chart_slide`, `table_slide`, `save`.

```python
import sys; sys.path.insert(0, "skill/pptx/scripts")
from pptx_skill import new_deck, cover_slide, bullet_slide, chart_slide, save
```
Run `python skill/pptx/scripts/pptx_skill.py` to write a demo deck and verify the install.

## Standard Template

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XLChartType

# 16:9 widescreen
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Palette
COLORS = {
    'bg': RGBColor(0xFA, 0xFA, 0xF7),
    'text': RGBColor(0x1A, 0x1A, 0x1A),
    'accent': RGBColor(0xD4, 0x50, 0x2A),
    'sub': RGBColor(0x6B, 0x6B, 0x6B),
}
FONT_NAME = 'Inter'  # Latin
FONT_CJK = 'Noto Sans CJK JP'
```

## Slide-Helper Functions

```python
def add_bg(slide, color):
    """Set slide background color."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_text(slide, left, top, width, height, text, size=18, bold=False,
             color=None, align=PP_ALIGN.LEFT, font=None):
    """Add a text box."""
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                      Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font or FONT_NAME
    if color:
        run.font.color.rgb = color
    return txBox

def add_rect(slide, left, top, width, height, fill_color, line_color=None):
    """Add a rectangle."""
    from pptx.enum.shapes import MSO_SHAPE
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()
    return shape
```

## Slide-Type Templates

### 1. Cover
```python
def cover_slide(prs, title, subtitle, date):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    add_bg(slide, COLORS['bg'])

    # Accent bar
    add_rect(slide, 1.0, 3.0, 0.15, 1.5, COLORS['accent'])

    # Main title
    add_text(slide, 1.4, 2.8, 10, 1.5, title, size=44, bold=True,
             color=COLORS['text'])

    # Subtitle
    add_text(slide, 1.4, 4.3, 10, 0.8, subtitle, size=20,
             color=COLORS['sub'])

    # Date
    add_text(slide, 1.4, 6.5, 5, 0.5, date, size=14, color=COLORS['sub'])
```

### 2. Section Divider
```python
def section_slide(prs, num, title):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, COLORS['text'])  # dark background

    add_text(slide, 1.0, 2.5, 3, 1, f"{num:02d}", size=120, bold=True,
             color=COLORS['accent'])
    add_text(slide, 1.0, 4.5, 11, 1, title, size=36, bold=True,
             color=RGBColor(0xFF, 0xFF, 0xFF))
```

### 3. Bullet Slide
```python
def bullet_slide(prs, title, bullets, sub_bullets=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, COLORS['bg'])

    # Title
    add_text(slide, 0.8, 0.5, 11, 1, title, size=32, bold=True,
             color=COLORS['text'])

    # Accent line
    add_rect(slide, 0.8, 1.5, 1.5, 0.05, COLORS['accent'])

    # Body
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(2.0),
                                      Inches(11), Inches(5))
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"•  {b}"
        p.font.size = Pt(20)
        p.font.name = FONT_NAME
        p.space_after = Pt(12)
        if sub_bullets and i in sub_bullets:
            for sb in sub_bullets[i]:
                sp = tf.add_paragraph()
                sp.text = f"   –  {sb}"
                sp.font.size = Pt(16)
                sp.font.name = FONT_NAME
                sp.font.color.rgb = COLORS['sub']
                sp.space_after = Pt(6)
```

### 4. Image + Text
```python
def image_text_slide(prs, title, image_path, text, image_side='left'):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, COLORS['bg'])

    add_text(slide, 0.8, 0.5, 11, 1, title, size=32, bold=True,
             color=COLORS['text'])

    if image_side == 'left':
        slide.shapes.add_picture(image_path, Inches(0.8), Inches(2.0),
                                 width=Inches(5.5))
        add_text(slide, 7.0, 2.5, 5.5, 4, text, size=18,
                 color=COLORS['text'])
    else:
        add_text(slide, 0.8, 2.5, 5.5, 4, text, size=18,
                 color=COLORS['text'])
        slide.shapes.add_picture(image_path, Inches(7.0), Inches(2.0),
                                 width=Inches(5.5))
```

### 5. Chart Slide
```python
def chart_slide(prs, title, categories, series_data):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, COLORS['bg'])

    add_text(slide, 0.8, 0.5, 11, 1, title, size=32, bold=True,
             color=COLORS['text'])

    chart_data = CategoryChartData()
    chart_data.categories = categories
    for name, values in series_data.items():
        chart_data.add_series(name, values)

    gframe = slide.shapes.add_chart(
        XLChartType.COLUMN_CLUSTERED,
        Inches(1), Inches(1.8), Inches(11), Inches(5.2),
        chart_data
    )
    chart = gframe.chart
    chart.has_legend = True
    chart.has_title = False
```

### 6. Table Slide
```python
def table_slide(prs, title, headers, rows):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, COLORS['bg'])

    add_text(slide, 0.8, 0.5, 11, 1, title, size=32, bold=True,
             color=COLORS['text'])

    rows_count = len(rows) + 1
    cols_count = len(headers)
    table_shape = slide.shapes.add_table(
        rows_count, cols_count,
        Inches(0.8), Inches(1.8),
        Inches(11.5), Inches(5)
    )
    table = table_shape.table

    # Header row
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS['text']
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                r.font.bold = True
                r.font.size = Pt(16)

    # Data rows
    for ri, row in enumerate(rows, start=1):
        for ci, v in enumerate(row):
            cell = table.cell(ri, ci)
            cell.text = str(v)
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(14)
                    r.font.name = FONT_NAME
```

## Slide Design Principles

### 10/20/30 Rule (reference, not strict)
- ~10 slides
- 20 min per slide max
- 30pt+ font size

### Visual Hierarchy
- Title: 32–44pt bold
- Body: 18–22pt
- Caption: 14–16pt
- Whitespace: ≥ 0.8 inch on all sides

### One Slide, One Message
- Split multiple topics into separate slides
- 5–7 bullet items max
- ≤ 20 chars per line for readability

## Output Workflow

1. **Clarify requirements**: purpose (sales / conference / internal), slide count, audience
2. **Design structure**: cover → agenda → body → summary → back cover
3. **Generate script**: `/home/z/my-project/scripts/gen_ppt_<name>.py`
4. **Run**: `python scripts/gen_ppt_<name>.py`
5. **Verify**: page count, text overflow, image sizes

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Text overflowing frame | Set `tf.word_wrap = True` |
| CJK glyphs as □□□ | Set `run.font.name` explicitly |
| Image too large | Pass `width=Inches(x)` |
| Table cells distorted | Set `table.columns[i].width = Inches(x)` |
| Blank slide | On `slide_layouts[6]` (blank) always set bg explicitly |
