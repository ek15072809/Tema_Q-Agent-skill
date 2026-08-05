"""pdf_skill.py — Two PDF paths in one module.

  * html_to_pdf()   — Playwright (Chromium headless), design-rich output.
  * office_to_pdf() — LibreOffice headless, converts .docx/.pptx/.xlsx.

Run as a script to test:  python pdf_skill.py <input.html|docx|pptx|xlsx>
"""
from __future__ import annotations
import asyncio
import os
import subprocess
import sys
from pathlib import Path


# ---- Path 1: HTML -> PDF via Playwright ----------------------------------

async def _html_to_pdf_async(html_path: str | Path,
                             pdf_path: str | Path,
                             format_: str = "A4",
                             print_background: bool = True,
                             margin_cm: float = 2.0,
                             show_page_numbers: bool = True) -> Path:
    from playwright.async_api import async_playwright

    html_path = Path(html_path).resolve()
    pdf_path  = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{html_path}", wait_until="networkidle")

        footer_template = ""
        if show_page_numbers:
            footer_template = (
                '<div style="font-size:9px; color:#999;'
                ' width:100%; text-align:center; padding:0 2cm;">'
                '<span class="pageNumber"></span> / '
                '<span class="totalPages"></span>'
                '</div>'
            )

        await page.pdf(
            path=str(pdf_path),
            format=format_,
            print_background=print_background,
            margin={
                "top":    f"{margin_cm}cm",
                "bottom": f"{margin_cm}cm",
                "left":   f"{margin_cm}cm",
                "right":  f"{margin_cm}cm",
            },
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=footer_template,
        )
        await browser.close()
    return pdf_path


def html_to_pdf(html_path: str | Path,
                pdf_path: str | Path | None = None,
                **kwargs) -> Path:
    """Sync wrapper. If pdf_path is None, derive from html_path."""
    html_path = Path(html_path)
    if pdf_path is None:
        pdf_path = html_path.with_suffix(".pdf")
    return asyncio.run(_html_to_pdf_async(html_path, pdf_path, **kwargs))


# ---- Path 2: Office -> PDF via LibreOffice -------------------------------

def office_to_pdf(input_path: str | Path,
                  output_dir: str | Path = "/home/z/my-project/download",
                  timeout_sec: int = 120) -> Path:
    """Convert .docx/.pptx/.xlsx to PDF via `soffice --headless`."""
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "soffice", "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_dir),
        str(input_path),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout_sec,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"PDF conversion failed (exit {result.returncode}):\n"
            f"stderr: {result.stderr}\nstdout: {result.stdout}"
        )
    base = input_path.stem
    return output_dir / f"{base}.pdf"


# ---- Auto-detect path ----------------------------------------------------

def to_pdf(input_path: str | Path,
           output_dir: str | Path = "/home/z/my-project/download",
           **kwargs) -> Path:
    """Auto-route based on file extension.

    .html  -> Playwright
    .docx / .pptx / .xlsx  -> LibreOffice
    """
    input_path = Path(input_path)
    ext = input_path.suffix.lower()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if ext in (".html", ".htm"):
        return html_to_pdf(input_path,
                           output_dir / f"{input_path.stem}.pdf",
                           **kwargs)
    if ext in (".docx", ".pptx", ".xlsx"):
        return office_to_pdf(input_path, output_dir)
    raise ValueError(f"Unsupported input extension: {ext}")


# ---- Convenience HTML template ------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  @page {{ size: A4; margin: 0; }}
  body {{
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
    margin: 2cm;
    color: #1a1a1a;
    font-size: 11pt;
    line-height: 1.6;
  }}
  h1 {{ font-size: 22pt; margin: 0 0 0.5em; }}
  h2 {{
    font-size: 16pt;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 0.3em;
    margin-top: 2em;
  }}
  h3 {{ font-size: 13pt; margin-top: 1.5em; }}
  p  {{ margin: 0.5em 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1em 0; }}
  th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
  th {{ background: #1a1a1a; color: white; }}
  .page-break {{ page-break-after: always; }}
  .cover {{
    page-break-after: always;
    text-align: center;
    padding-top: 8cm;
  }}
  .no-break {{ page-break-inside: avoid; }}
  img {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
  <div class="cover">
    <h1>{title}</h1>
    <p>{subtitle}</p>
  </div>

  <h2>Section 1</h2>
  <p>{body}</p>
</body>
</html>
"""


def write_html_template(out_path: str | Path,
                        title: str = "Document Title",
                        subtitle: str = "",
                        body: str = "Replace this body.",
                        lang: str = "en") -> Path:
    """Write a starter HTML file using the bundled template."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = HTML_TEMPLATE.format(
        title=title, subtitle=subtitle, body=body, lang=lang,
    )
    out_path.write_text(html, encoding="utf-8")
    return out_path


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_skill.py <input.html|docx|pptx|xlsx>")
        sys.exit(1)
    src = sys.argv[1]
    out = to_pdf(src)
    print(f"PDF written: {out}")
