# Reference Design Styles (Detail)

## Swiss Design
- **Traits**: grid-driven, minimal, sans-serif, left-aligned
- **Palette**: white / black / red (warning) + one accent
- **Fonts**: Helvetica / Inter / Noto Sans
- **Use cases**: corporate IR, technical docs, newspapers
- **Implementation**: strict 8-column grid, generous whitespace

## Bauhaus
- **Traits**: geometric shapes (circle, triangle, square), primary colors, functionalism
- **Palette**: white + red / yellow / blue (primaries)
- **Fonts**: Universal / Futura / Archivo
- **Use cases**: art, education, posters
- **Implementation**: large geometric shapes as background, minimal text

## Editorial (magazine style)
- **Traits**: large headings, multi-column, serif + sans-serif
- **Palette**: ivory / ink / one accent
- **Fonts**: Playfair Display / Cormorant + Inter / Noto Serif JP
- **Use cases**: blogs, magazines, long-form content
- **Implementation**: headings 5–8× body size, drop cap on first letter

## Brutalism
- **Traits**: intentional "ugliness", system fonts, extreme layouts
- **Palette**: white / black / occasional single fluorescent
- **Fonts**: Times New Roman / Courier / system defaults
- **Use cases**: underground, experimental
- **Implementation**: no borders, extreme whitespace, links as blue underline only

## Neo-Brutalism
- **Traits**: thick borders, hard shadows, primary-color blocks
- **Palette**: yellow / lime / pink + black borders
- **Fonts**: Space Grotesk / Archivo Black / Zen Kaku Gothic
- **Use cases**: SaaS, startups, creator-focused
- **Implementation**: 2–4px black borders, 4–8px offset shadows (`box-shadow: 8px 8px 0 #000`)

## Apple HIG / Premium Minimal
- **Traits**: large whitespace, clear hierarchy, subtle animations
- **Palette**: white / gray / one soft accent
- **Fonts**: SF Pro / Inter / Noto Sans JP
- **Use cases**: product pages, premium services
- **Implementation**: 12–16px corner radius, very thin shadows, 30ms fade-ins

## Tone-Based Font Pairing Cheatsheet

| Tone | Headings | Body | Accent |
|---|---|---|---|
| Modern | Inter Bold | Inter Regular | JetBrains Mono |
| Classic | Playfair Display | Lora | Cormorant |
| Tech | Space Grotesk | IBM Plex Sans | IBM Plex Mono |
| JP Editorial | Noto Serif JP | Noto Sans JP | Shippori Mincho |
| JP Modern | Zen Kaku Gothic New | Zen Kaku Gothic Regular | JetBrains Mono |
| Handwritten | Caveat | Noto Sans JP | Kalam |

## Color Tools
- **Coolors**: https://coolors.co/
- **Adobe Color**: https://color.adobe.com/
- **Realtime Colors**: https://realtimecolors.com/

When the user gives no direction:
1. Ask purpose (business / casual / art)
2. Pick one style from the list above
3. Generate or propose a palette
