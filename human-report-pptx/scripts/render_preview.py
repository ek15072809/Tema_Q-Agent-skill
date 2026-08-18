#!/usr/bin/env python3
"""render_preview.py — .pptx をスライドごとのJPEG画像に変換してQAするための小道具。

LibreOffice (soffice) と pdftoppm (Poppler) が入っている環境専用。
どちらもプロプライエタリな依存はなく、素の CLI を呼び出すだけ。

使い方:
    python3 render_preview.py /path/to/deck.pptx [出力先ディレクトリ]

出力: <出力先>/slide-1.jpg, slide-2.jpg, ... を作成し、パスを標準出力に列挙する。
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path


def render_preview(pptx_path: str, out_dir: str | None = None) -> list[str]:
    pptx = Path(pptx_path).resolve()
    if not pptx.exists():
        raise FileNotFoundError(pptx)

    out = Path(out_dir).resolve() if out_dir else pptx.parent / f"{pptx.stem}_preview"
    out.mkdir(parents=True, exist_ok=True)

    # 1) pptx -> pdf
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out), str(pptx)],
        check=True, capture_output=True,
    )
    pdf_path = out / f"{pptx.stem}.pdf"
    if not pdf_path.exists():
        raise RuntimeError(f"PDF conversion failed, expected {pdf_path}")

    # 2) pdf -> jpeg (1枚ずつ)
    for old in out.glob("slide-*.jpg"):
        old.unlink()
    subprocess.run(
        ["pdftoppm", "-jpeg", "-r", "150", str(pdf_path), str(out / "slide")],
        check=True, capture_output=True,
    )

    images = sorted(out.glob("slide-*.jpg"))
    return [str(p) for p in images]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: render_preview.py deck.pptx [out_dir]", file=sys.stderr)
        sys.exit(1)
    paths = render_preview(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    for p in paths:
        print(p)
