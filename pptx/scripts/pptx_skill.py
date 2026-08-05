"""pptx_skill.py — Reusable building blocks for .pptx generation.

Each slide builder appends one slide to a Presentation and returns the slide.
All builders share the same palette + fonts so decks stay consistent.
"""
from __future__ import annotations
from pathlib import Path
from typing import Sequence

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE


# ---- Palette & fonts ------------------------------------------------------

COLORS = {
    "bg":     RGBColor(0xFA, 0xFA, 0xF7),
    "text":   RGBColor(0x1A, 0x1A, 0x1A),
    "accent": RGBColor(0xD4, 0x50, 0x2A),
    "sub":    RGBColor(0x6B, 0x6B, 0x6B),
    "white":  RGBColor(0xFF, 0xFF, 0xFF),
}

FONT_LATIN = "Inter"
FONT_CJK   = "Noto Sans CJK JP"


# ---- New deck -------------------------------------------------------------

def new_deck(widescreen: bool = True) -> Presentation:
    """16:9 by default; 4:3 if widescreen=False."""
    prs = Presentation()
    if widescreen:
        prs.slide_width  = Inches(13.333)
        prs.slide_height = Inches(7.5)
    else:
        prs.slide_width  = Inches(10)
        prs.slide_height = Inches(7.5)
    return prs


def _blank(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _set_bg(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _text(slide, left, top, width, height, text,
          size=18, bold=False, color=None,
          align=PP_ALIGN.LEFT, font=None):
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font or FONT_LATIN
    if color:
        run.font.color.rgb = color
    return box


def _rect(slide, left, top, width, height,
          fill_color: RGBColor, line_color: RGBColor | None = None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color is not None:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()
    return shape


# ---- Slide builders -------------------------------------------------------

def cover_slide(prs: Presentation, title: str, subtitle: str = "",
                date: str = "") -> None:
    s = _blank(prs)
    _set_bg(s, COLORS["bg"])
    _rect(s, 1.0, 3.0, 0.15, 1.5, COLORS["accent"])
    _text(s, 1.4, 2.8, 10, 1.5, title,
          size=44, bold=True, color=COLORS["text"])
    if subtitle:
        _text(s, 1.4, 4.3, 10, 0.8, subtitle,
              size=20, color=COLORS["sub"])
    if date:
        _text(s, 1.4, 6.5, 5, 0.5, date,
              size=14, color=COLORS["sub"])


def section_slide(prs: Presentation, num: int, title: str) -> None:
    s = _blank(prs)
    _set_bg(s, COLORS["text"])
    _text(s, 1.0, 2.5, 3, 1, f"{num:02d}",
          size=120, bold=True, color=COLORS["accent"])
    _text(s, 1.0, 4.5, 11, 1, title,
          size=36, bold=True, color=COLORS["white"])


def bullet_slide(prs: Presentation, title: str,
                 bullets: Sequence[str],
                 sub_bullets: dict | None = None) -> None:
    s = _blank(prs)
    _set_bg(s, COLORS["bg"])
    _text(s, 0.8, 0.5, 11, 1, title,
          size=32, bold=True, color=COLORS["text"])
    _rect(s, 0.8, 1.5, 1.5, 0.05, COLORS["accent"])

    box = s.shapes.add_textbox(
        Inches(0.8), Inches(2.0), Inches(11), Inches(5),
    )
    tf = box.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"•  {b}"
        p.font.size = Pt(20)
        p.font.name = FONT_LATIN
        p.space_after = Pt(12)
        if sub_bullets and i in sub_bullets:
            for sb in sub_bullets[i]:
                sp = tf.add_paragraph()
                sp.text = f"   –  {sb}"
                sp.font.size = Pt(16)
                sp.font.name = FONT_LATIN
                sp.font.color.rgb = COLORS["sub"]
                sp.space_after = Pt(6)


def image_text_slide(prs: Presentation, title: str,
                     image_path: str | Path, text: str,
                     image_side: str = "left") -> None:
    s = _blank(prs)
    _set_bg(s, COLORS["bg"])
    _text(s, 0.8, 0.5, 11, 1, title,
          size=32, bold=True, color=COLORS["text"])

    if image_side == "left":
        s.shapes.add_picture(str(image_path),
                             Inches(0.8), Inches(2.0), width=Inches(5.5))
        _text(s, 7.0, 2.5, 5.5, 4, text,
              size=18, color=COLORS["text"])
    else:
        _text(s, 0.8, 2.5, 5.5, 4, text,
              size=18, color=COLORS["text"])
        s.shapes.add_picture(str(image_path),
                             Inches(7.0), Inches(2.0), width=Inches(5.5))


def chart_slide(prs: Presentation, title: str,
                categories: Sequence[str],
                series_data: dict,
                chart_type=XL_CHART_TYPE.COLUMN_CLUSTERED) -> None:
    s = _blank(prs)
    _set_bg(s, COLORS["bg"])
    _text(s, 0.8, 0.5, 11, 1, title,
          size=32, bold=True, color=COLORS["text"])

    cd = CategoryChartData()
    cd.categories = list(categories)
    for name, values in series_data.items():
        cd.add_series(name, list(values))

    gframe = s.shapes.add_chart(
        chart_type,
        Inches(1), Inches(1.8), Inches(11), Inches(5.2),
        cd,
    )
    gframe.chart.has_legend = True
    gframe.chart.has_title = False


def table_slide(prs: Presentation, title: str,
                headers: Sequence[str],
                rows: Sequence[Sequence[object]]) -> None:
    s = _blank(prs)
    _set_bg(s, COLORS["bg"])
    _text(s, 0.8, 0.5, 11, 1, title,
          size=32, bold=True, color=COLORS["text"])

    rows_count = len(rows) + 1
    cols_count = len(headers)
    tbl_shape = s.shapes.add_table(
        rows_count, cols_count,
        Inches(0.8), Inches(1.8), Inches(11.5), Inches(5),
    )
    tbl = tbl_shape.table

    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.text = str(h)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS["text"]
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.color.rgb = COLORS["white"]
                r.font.bold = True
                r.font.size = Pt(16)

    for ri, row in enumerate(rows, start=1):
        for ci, v in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.text = str(v)
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(14)
                    r.font.name = FONT_LATIN


# ---- Save -----------------------------------------------------------------

def save(prs: Presentation, filename: str,
         out_dir: str = "/home/z/my-project/download") -> Path:
    p = Path(out_dir) / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    prs.save(p)
    return p


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    prs = new_deck()
    cover_slide(prs, "Demo Deck", "Built with pptx_skill.py", "2025-08-05")
    section_slide(prs, 1, "Background")
    bullet_slide(prs, "Why Now?", [
        "Market is growing 30% YoY",
        "Competitors are slow",
        "Customer demand is clear",
    ])
    chart_slide(prs, "Quarterly Revenue",
                ["Q1", "Q2", "Q3", "Q4"],
                {"Revenue": [120, 180, 240, 310]})
    table_slide(prs, "Team",
                ["Name", "Role", "Years"],
                [("Alice", "CEO", "10"),
                 ("Bob",   "CTO", "8"),
                 ("Carol", "CMO", "5")])
    out = save(prs, "pptx_skill_demo.pptx")
    print(f"Saved: {out}")
