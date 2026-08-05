"""art_skill.py — HTML/CSS builders for human-made-looking design.

Provides:
  * tailwind_boilerplate()  — HTML skeleton with Tailwind + Alpine via CDN.
  * plain_html_boilerplate() — minimal HTML with inline CSS.
  * render_to_file()        — write an HTML string to disk under download/.
  * palettes                — ready-to-use 3-color sets.
  * font_pairs              — ready-to-use font pairing suggestions.
"""
from __future__ import annotations
from pathlib import Path
from typing import Tuple


# ---- Ready-to-use palettes (background, text, accent) --------------------

palettes: dict[str, Tuple[str, str, str]] = {
    "editorial":     ("#FAFAF7", "#1A1A1A", "#D4502A"),
    "tech":          ("#0A0A0A", "#E5E5E5", "#00FF88"),
    "warm":          ("#F5EFE6", "#3D2C1E", "#C97B3F"),
    "minimal":       ("#FFFFFF", "#111111", "#0066FF"),
    "swiss":         ("#FFFFFF", "#000000", "#E63946"),
    "bauhaus":       ("#F4F4F4", "#1A1A1A", "#FFD700"),
    "neobrutal":     ("#FEE440", "#000000", "#393E46"),
    "premium_dark":  ("#0F0F0F", "#FFFFFF", "#B89968"),
}


# ---- Font pairings (heading, body, accent) -------------------------------

font_pairs: dict[str, Tuple[str, str, str]] = {
    "modern":       ("Inter Bold",            "Inter Regular",         "JetBrains Mono"),
    "classic":      ("Playfair Display",      "Lora",                  "Cormorant"),
    "tech":         ("Space Grotesk",         "IBM Plex Sans",         "IBM Plex Mono"),
    "jp_editorial": ("Noto Serif JP",         "Noto Sans JP",          "Shippori Mincho"),
    "jp_modern":    ("Zen Kaku Gothic New",   "Zen Kaku Gothic Reg.",  "JetBrains Mono"),
    "handwritten":  ("Caveat",                "Noto Sans JP",          "Kalam"),
}


# ---- Tailwind + Alpine boilerplate ---------------------------------------

TAILWIND_CDN = "https://cdn.tailwindcss.com"
ALPINE_CDN   = "https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"


def tailwind_boilerplate(title: str = "Untitled",
                          body_class: str = "bg-white text-gray-900",
                          lang: str = "en") -> str:
    """A starter HTML with Tailwind + Alpine via CDN, ready to fill in."""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <script src="{TAILWIND_CDN}"></script>
  <script defer src="{ALPINE_CDN}"></script>
  <style>[x-cloak]{{display:none}}</style>
</head>
<body class="{body_class}">

  <!-- TODO: build the page here -->

</body>
</html>
"""


# ---- Plain HTML + inline CSS (no external deps) -------------------------

def plain_html_boilerplate(title: str = "Untitled",
                           bg: str = "#FAFAF7",
                           text: str = "#1A1A1A",
                           accent: str = "#D4502A",
                           lang: str = "en") -> str:
    """A self-contained HTML file with inline CSS. Good for offline PDFs."""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', 'Noto Sans JP', system-ui, sans-serif;
      background: {bg};
      color: {text};
      line-height: 1.6;
      padding: 2rem;
    }}
    h1 {{ font-size: 2.5rem; margin-bottom: 0.5em; }}
    h2 {{
      font-size: 1.75rem;
      border-bottom: 2px solid {accent};
      padding-bottom: 0.3em;
      margin: 2em 0 1em;
    }}
    h3 {{ font-size: 1.25rem; margin: 1.5em 0 0.5em; }}
    p  {{ margin: 0.5em 0; }}
    a  {{ color: {accent}; }}
    .accent {{ color: {accent}; }}
    .container {{ max-width: 720px; margin: 0 auto; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{title}</h1>
    <!-- TODO: build the page here -->
  </div>
</body>
</html>
"""


# ---- Write file -----------------------------------------------------------

def render_to_file(html: str,
                   filename: str,
                   out_dir: str = "/home/z/my-project/download") -> Path:
    """Write an HTML string to disk under download/."""
    p = Path(out_dir) / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return p


# ---- Anti-AI-Look self-check ---------------------------------------------

AI_LOOK_RED_FLAGS = [
    "linear-gradient(to right, #a855f7",   # purple-pink gradient
    "linear-gradient(135deg, #ec4899",     # pink-purple gradient
    "🚀", "✨", "🎯", "🔥",                # emoji as UI icons
    "class=\"bg-gradient-to-br from-purple-",  # canonical AI tailwind
]


def check_for_ai_look(html: str) -> list[str]:
    """Return list of matched red-flag substrings (empty = clean)."""
    return [flag for flag in AI_LOOK_RED_FLAGS if flag in html]


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    html = plain_html_boilerplate(
        title="Art Skill Demo",
        bg=palettes["editorial"][0],
        text=palettes["editorial"][1],
        accent=palettes["editorial"][2],
    )
    # Inject some body content
    body = """
  <div class="container">
    <h1>Art Skill Demo</h1>
    <h2>Editorial Style</h2>
    <p>This page was generated by art_skill.py.</p>
    <p>It uses the <span class="accent">editorial</span> palette.</p>
  </div>"""
    html = html.replace("<!-- TODO: build the page here -->", body)

    out = render_to_file(html, "art_skill_demo.html")
    print(f"HTML written: {out}")
    flags = check_for_ai_look(html)
    print(f"AI-look red flags: {flags if flags else 'none (clean)'}")
