---
name: pdf
description: Generate PDFs from HTML via Playwright (Chromium headless) and convert Office files (docx/pptx/xlsx) to PDF via LibreOffice. Print CSS, page setup, headers/footers supported.
---

# PDF Skill

## Overview
Two paths:
1. **HTML → PDF**: Render with Playwright (headless Chromium). Maximum design freedom.
2. **Office → PDF**: Convert docx/pptx/xlsx via LibreOffice (`soffice --headless`).

Output path: `/home/z/my-project/download/<filename>.pdf`

## Required Tools

```bash
# Playwright
pip install playwright
playwright install chromium

# LibreOffice (for Office → PDF)
apt-get install -y libreoffice  # or: brew install libreoffice
```

## Bundled Helper Module
**`skill/pdf/scripts/pdf_skill.py`** provides a single entry point:

```python
import sys; sys.path.insert(0, "skill/pdf/scripts")
from pdf_skill import to_pdf, html_to_pdf, office_to_pdf, write_html_template

# Auto-route by extension
to_pdf("input.html")          # → Playwright
to_pdf("input.docx")          # → LibreOffice

# Or explicit:
html_to_pdf("input.html", "output.pdf")
office_to_pdf("input.pptx", output_dir=".")

# Starter HTML template
write_html_template("starter.html", title="My Report", body="Hello.")
```

Run `python skill/pdf/scripts/pdf_skill.py <input.html|docx|pptx|xlsx>` to convert one file.

## Path 1: HTML → PDF (recommended for design-rich output)

### Basic Template

```python
import asyncio
from playwright.async_api import async_playwright

async def html_to_pdf(html_path, pdf_path, format_='A4',
                      print_background=True, margin_cm=2.0):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f'file://{html_path}', wait_until='networkidle')

        await page.pdf(
            path=pdf_path,
            format=format_,
            print_background=print_background,
            margin={
                'top': f'{margin_cm}cm',
                'bottom': f'{margin_cm}cm',
                'left': f'{margin_cm}cm',
                'right': f'{margin_cm}cm',
            },
            display_header_footer=True,
            header_template='<div></div>',  # empty
            footer_template='''
                <div style="font-size:9px; color:#999;
                            width:100%; text-align:center;
                            padding:0 2cm;">
                    <span class="pageNumber"></span> /
                    <span class="totalPages"></span>
                </div>
            ''',
        )
        await browser.close()

# Run
asyncio.run(html_to_pdf('/path/input.html', '/path/output.pdf'))
```

### HTML Template (for PDF)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Document</title>
<style>
  @page {
    size: A4;
    margin: 0;
  }
  body {
    font-family: 'Inter', 'Noto Sans', sans-serif;
    margin: 2cm;
    color: #1a1a1a;
    font-size: 11pt;
    line-height: 1.6;
  }
  h1 { font-size: 22pt; margin: 0 0 0.5em; }
  h2 {
    font-size: 16pt;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 0.3em;
    margin-top: 2em;
  }
  h3 { font-size: 13pt; margin-top: 1.5em; }
  p { margin: 0.5em 0; }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }
  th { background: #1a1a1a; color: white; }
  .page-break {
    page-break-after: always;
  }
  .cover {
    page-break-after: always;
    text-align: center;
    padding-top: 8cm;
  }
  .no-break {
    page-break-inside: avoid;
  }
  img { max-width: 100%; height: auto; }
</style>
</head>
<body>
  <div class="cover">
    <h1>Title</h1>
    <p>Date: 2025-08-05</p>
  </div>

  <h2>Section 1</h2>
  <p>Body...</p>

  <div class="page-break"></div>

  <h2>Section 2</h2>
  <p>Body...</p>
</body>
</html>
```

### Key PDF-CSS Rules
- `@page { size: A4; margin: 0; }` — paper size
- `body` margin (≈2cm)
- `page-break-after: always` — explicit page break
- `page-break-inside: avoid` — keep element together
- `print_background: true` is mandatory (otherwise bg colors/images disappear)

## Path 2: Office → PDF Conversion

### docx → pdf
```bash
soffice --headless --convert-to pdf --outdir /home/z/my-project/download/ /path/input.docx
```

### pptx → pdf
```bash
soffice --headless --convert-to pdf --outdir /home/z/my-project/download/ /path/input.pptx
```

### xlsx → pdf
```bash
# To force landscape
soffice --headless --convert-to pdf:calc_pdf_Export --outdir /home/z/my-project/download/ /path/input.xlsx
```

### Python Wrapper

```python
import subprocess
import os

def convert_to_pdf(input_path, output_dir='/home/z/my-project/download/'):
    """Convert any Office file to PDF via LibreOffice."""
    cmd = [
        'soffice', '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"PDF conversion failed: {result.stderr}")
    base = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(output_dir, f"{base}.pdf")
```

## Path Selection Flow

```
User request
  ├── "design-rich" / "advanced layout"     → HTML → PDF
  ├── "convert existing Word/PPT/Excel"     → Office → PDF
  ├── "new multi-page report"               → HTML → PDF
  └── "form / invoice / template"           → HTML → PDF
```

## Advanced Features

### Cover-Page PDF (HTML)

```html
<div class="cover" style="height: 100vh; page-break-after: always;
                            background: #1a1a1a; color: white;
                            display: flex; flex-direction: column;
                            justify-content: center; padding: 4cm;
                            margin: -2cm;">
  <h1 style="color: white; font-size: 36pt;">Title</h1>
  <p style="color: #ccc;">Subtitle</p>
</div>
```

### Manual TOC

```html
<h2>Table of Contents</h2>
<ul style="list-style: none; padding: 0;">
  <li><a href="#sec1">1. Introduction</a> ... 3</li>
  <li><a href="#sec2">2. Methodology</a> ... 5</li>
</ul>
```

### Image Optimization (base64 embedding)

```python
import base64
def embed_image(path):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.split('.')[-1].lower()
    mime = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png',
            'gif': 'gif', 'svg': 'svg+xml'}[ext]
    return f'data:image/{mime};base64,{b64}'
```

## Output Workflow

1. **Clarify requirements**: content, page count, design level
2. **Pick path**: HTML or Office conversion
3. **Generate HTML** (`/home/z/my-project/scripts/gen_<name>.html`)
4. **Render PDF** (`/home/z/my-project/scripts/render_<name>.py`)
5. **Verify**: page count, text overflow, image rendering

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| CJK glyphs as □□□ | Set `font-family: 'Noto Sans JP'` explicitly |
| Background comes out white | Set `print_background=True` |
| Page break in odd places | Use `page-break-inside: avoid` |
| Font mismatch | Pre-download web fonts |
| Image not showing | Use absolute path or base64 |
| Office conversion garbled | Install CJK fonts system-wide |

## System Font Check

```bash
# CJK fonts
fc-list :lang=ja | head -20

# Available fonts
fc-list | grep -i "noto\|inter\|dejavu"
```

If missing:
```bash
apt-get install fonts-noto-cjk fonts-noto-cjk-extra
```
