---
name: art
description: Use when making design decisions (color, typography, layout, UI/UX) so the output looks human-made, not AI-made. Apply across all design-related tasks.
---

# Art Direction Skill

## Purpose
Avoid the "AI-made" look that LLMs fall into by default. Aim for the polished, intentional output a professional designer would ship.

## AI-Look Red Flags (always avoid)

### Color Pitfalls
- Purple-to-pink gradients (the canonical AI palette)
- Neon blue + magenta cyberpunk pairing
- Rainbow gradients, gradient overuse
- White background with only purple accents
- Black background with fluorescent colors (meaningless dark mode)

### Layout Pitfalls
- Center-aligned "hero three-stack" (H1 + subtitle + CTA)
- Card-ify everything (everything in rounded rectangles)
- Over-rigid uniform grid (no asymmetry)
- Lack of whitespace (over-stuffed)
- Icon on every card

### Typography Pitfalls
- Single font for everything
- Small size differential (e.g., h1=24px, p=16px)
- Default line-height / letter-tracking untouched
- Ignored Latin + CJK font pairing balance

### Icon & Illustration Pitfalls
- Emoji used as UI icons (🚀✨ etc.)
- Generic flat illustrations (unDraw / Storyset style)
- Lucide / Heroicons used out-of-the-box without color tuning

## Pro Design Principles

### Color: 60-30-10 Rule
- 60% Base (background)
- 30% Secondary (text, sections)
- 10% Accent (CTA, highlights)

### Color Schemes
| Scheme | Effect | Example |
|---|---|---|
| Analogous | Harmonious, calm | Blue + Indigo + Teal |
| Complementary | Strong contrast | Blue + Orange |
| Triadic | Balanced | Red + Yellow + Blue |
| Monochromatic | Chic, premium | Lightness variations of one hue |

### Ready-to-Use Palettes
- Editorial: `#FAFAF7` / `#1A1A1A` / `#D4502A`
- Tech: `#0A0A0A` / `#E5E5E5` / `#00FF88`
- Warm: `#F5EFE6` / `#3D2C1E` / `#C97B3F`
- Minimal: `#FFFFFF` / `#111111` / `#0066FF`

### Typography
- Pairing rule: serif (headings) + sans-serif (body), or reverse
- Size ratio: 1.25–1.5 (major scale recommended)
- Line-height: body 1.5–1.7, headings 1.1–1.3
- Letter-tracking: tighten large headings, leave body at default
- CJK: Noto Serif JP / Noto Sans JP / Zen Kaku Gothic / Shippori Mincho
- Latin: Inter / Playfair Display / IBM Plex / JetBrains Mono

### Layout
- 8pt grid (8, 16, 24, 32, 48, 64, 96, 128px)
- Asymmetry: 7:5 or 5:7 split
- Whitespace is intentional (do not stuff)
- Z pattern (general) or F pattern (heavy text)

### Photos vs Illustrations
- Product photos > stock illustrations
- Apply unified filter to photos (consistent color temperature, contrast)
- If illustration is needed, prefer geometric / abstract / hand-drawn

## Reference Design Styles
See `references.md` for details:
- Swiss Design / Bauhaus / Editorial / Brutalism / Neo-brutalism / Apple HIG

## Bundled Helper Module
**`skill/art/scripts/art_skill.py`** provides:
- `palettes` — 8 ready-to-use 3-color sets (editorial, tech, warm, ...)
- `font_pairs` — 6 font-pairing presets (modern, classic, tech, JP, ...)
- `tailwind_boilerplate(title)` — HTML skeleton w/ Tailwind + Alpine via CDN
- `plain_html_boilerplate(title, bg, text, accent)` — self-contained inline-CSS HTML
- `render_to_file(html, filename)` — write to `/home/z/my-project/download/`
- `check_for_ai_look(html)` — returns matched AI-look red-flag substrings

```python
import sys; sys.path.insert(0, "skill/art/scripts")
from art_skill import palettes, plain_html_boilerplate, render_to_file, check_for_ai_look

bg, text, accent = palettes["editorial"]
html = plain_html_boilerplate("My Page", bg=bg, text=text, accent=accent)
flags = check_for_ai_look(html)   # should be []
render_to_file(html, "my_page.html")
```
Run `python skill/art/scripts/art_skill.py` to emit a demo HTML file.

## Workflow
1. **Clarify intent**: what, for whom, in what tone
2. **Make design decisions**: apply the principles above (color, type, layout)
3. **Implement**: HTML/CSS, Tailwind, or instruction text
4. **Self-evaluate**: check against the "AI-Look Red Flags"
5. **Adjust**: refine if needed

## Output Spec

### Design instructions
- Palette (3-color set with HEX)
- Typography (font names, sizes, line-height)
- Layout (grid, spacing)
- Concrete HTML/CSS snippet (10–30 lines)

### HTML output
- Tailwind CSS (CDN allowed) or inline CSS
- Responsive (mobile-first)
- Accessibility: WCAG AA (contrast ratio ≥ 4.5:1)
- Single self-contained file (only CDN external deps)

## Final Self-Check
Before delivering, ask:
- [ ] No purple-pink gradient?
- [ ] No center-stacked hero three-piece?
- [ ] Sufficient font-size differential?
- [ ] Whitespace is intentional?
- [ ] No emoji used as icons?
