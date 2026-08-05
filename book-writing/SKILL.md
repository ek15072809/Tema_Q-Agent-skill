---
name: book-writing
description: Write a long-form novel (≈80,000 words) without quality collapse. Use for any fiction project ≥10,000 words where consistency, character voice, and pacing must hold across many chapters.
---

# Book-Writing Skill

## Overview
Write a novel of **≈80,000 words** without quality collapse.
The biggest risks at this length:
1. **Inconsistency** — character traits, world rules, timeline contradictions.
2. **Voice drift** — narrative tone changing across chapters.
3. **Pacing collapse** — middle-book sag, rushed ending.
4. **Plot holes** — promises (foreshadowing) forgotten or unfulfilled.
5. **Context overflow** — even a large context window cannot hold 80k words at once.

**Core strategy**: persistent outline + chapter bible + per-chapter consistency check.
The agent writes one chapter at a time, **always re-reading the bible first**.

## Bundled Helper Module
**`skill/book-writing/scripts/book_writing.py`** provides (standard library only):
- `Book` / `Chapter` / `Character` / `PlotPoint` / `WorldRule` dataclasses.
- `Bible` — JSON-serializable state file (characters, world rules, plot beats, timeline).
- `Bible.load(path)` / `Bible.save(path)` — persist across chapters.
- `outline_chapters(n, three_act=True)` — generate a balanced chapter arc.
- `word_count_target(total, n)` — per-chapter word target.
- `consistency_check(bible, chapter)` — flag character / timeline / plot issues.
- `format_bible_md(bible)` — render the bible as Markdown for human review.

```python
import sys; sys.path.insert(0, "skill/book-writing/scripts")
from book_writing import (Book, Chapter, Character, PlotPoint, WorldRule, Bible,
                          outline_chapters, word_count_target,
                          consistency_check, format_bible_md)
```
Run `python skill/book-writing/scripts/book_writing.py` to generate a sample
bible + outline for a 24-chapter / 80k-word novel.

## File Layout (mandatory)

```
/home/z/my-project/download/books/<book-slug>/
├── bible.json             # canonical state (characters, world, plot, timeline)
├── outline.md             # chapter-by-chapter outline (the spine)
├── chapters/
│   ├── ch01.md
│   ├── ch02.md
│   └── ...
├── notes/
│   ├── voice_style.md     # narrative voice guidelines
│   ├── pacing.md          # per-act pacing notes
│   └── revision_log.md    # what changed and why
└── final.md               # assembled full manuscript (last step)
```

## Workflow (do not skip steps)

### Phase 1 — Premise & Bible (1 session)
1. Capture premise: logline, genre, target audience, comparable titles.
2. Define **characters** (name, age, role, voice, want, need, flaw, arc).
3. Define **world rules** (setting, magic/science system, social rules).
4. Define **plot beats** (the 15-25 major turning points).
5. Write `bible.json` via `Bible.save()`. This is the single source of truth.

### Phase 2 — Outline (1 session)
1. Use `outline_chapters(n=24, three_act=True)` to get the spine.
2. Assign each plot beat to a chapter.
3. For each chapter: write a 100-200 word synopsis (what happens, who POV, end hook).
4. Save as `outline.md`. **Do not start prose until the outline is solid.**

### Phase 3 — Per-Chapter Writing (1 chapter per session)
For each chapter:
1. **Re-read**: `bible.json` + the previous chapter's last 500 words.
2. **Re-read**: the chapter's synopsis in `outline.md`.
3. **Write**: target ≈3,300 words (for 80k / 24 chapters).
4. **Check** via `consistency_check(bible, chapter)`. Fix any flags.
5. **Update bible**: append new characters / plot beats / timeline events.
6. **Save**: `chapters/ch{NN}.md`. Append a 1-line summary to `notes/revision_log.md`.

### Phase 4 — Read-Through & Revision (1 session per act)
1. After every ~8 chapters (1 act), read straight through.
2. Flag: voice drift, pacing, foreshadowing that didn't pay off.
3. Revise in place. Update `bible.json` if any rule changed.

### Phase 5 — Assembly
1. Concatenate `chapters/ch*.md` in order into `final.md`.
2. Add front matter (title page, copyright, dedication).
3. Word-count check: target 80,000 ±5%.

## Word-Budget Math

| Total | Chapters | Words/chapter | Sessions |
|---|---|---|---|
| 80,000 | 24 | 3,333 | ~28 |
| 80,000 | 30 | 2,667 | ~34 |
| 80,000 | 20 | 4,000 | ~24 |

Per session: ≤4,000 words of new prose + re-reads. **Never write 2 chapters
in one session** — quality drops fast after ~5,000 words.

## Three-Act Outline (24 chapters)

`outline_chapters(24, three_act=True)` produces:
- Act I (ch 1-6): Hook, inciting incident, plot point 1.
- Act II-a (ch 7-12): Rising action, midpoint revelation.
- Act II-b (ch 13-18): Stakes raise, all-is-lost moment.
- Act III (ch 19-24): Climax, resolution, denouement.

## Consistency Checklist (per chapter)
- [ ] Every named character matches the bible (age, role, voice).
- [ ] No timeline contradiction (dates, seasons, ages).
- [ ] No world-rule violation (magic cost, physics, social rules).
- [ ] Foreshadowing from earlier chapters pays off (or is intentionally deferred).
- [ ] POV stays consistent within a scene.
- [ ] No character introduced without being added to the bible.
- [ ] Word count within ±10% of chapter target.
- [ ] Chapter ends with a hook (cliffhanger / question / turn).

## Voice & Style Guidelines (move into `notes/voice_style.md`)
- Pick 3 adjectives for the narrative voice (e.g., "spare, ironic, cinematic").
- Read aloud the first and last paragraph of every chapter.
- Avoid: adverb stacking, cliché openers ("It was a dark and stormy night"),
  filter words ("she saw", "he felt") when a direct description works.
- Dialogue: each character should have a distinct rhythm and vocabulary.

## Pacing Targets
- Open (ch 1-3): hook by ch 1 page 5, inciting incident by ch 3.
- Midpoint (ch 12): a reversal that re-frames the goal.
- All-is-lost (ch 17-18): lowest point for the protagonist.
- Climax (ch 22-23): the protagonist's want vs need collide.
- Resolution (ch 24): new equilibrium; promise of theme fulfilled.

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Bible ignored | Always `Bible.load()` before writing |
| Voice drift | Re-read notes/voice_style.md every session |
| Foreshadowing lost | Track in PlotPoint foreshadowed_by / payed_off_in |
| Sagging middle | Midpoint must be a true reversal, not filler |
| Rushed ending | Reserve ≥3 chapters for Act III |
| Mary Sue protagonist | Give a real flaw that costs something |
| Deus ex machina | Every solution must be set up ≥2 chapters earlier |
| Context overflow | Never load all chapters at once; re-read only what's needed |

## Quality Heuristics (final pass)
- Cut 10% — every book has filler. Aim to delete ~8,000 words.
- Vary sentence length: long, short, fragment.
- Concrete over abstract: "rain hit the tin roof" > "the weather was bad".
- End scenes on action / image, not exposition.
- Show, don't tell — but know when to tell (transitions, time skips).
