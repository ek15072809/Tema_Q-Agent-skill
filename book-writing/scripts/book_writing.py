"""book_writing.py — Helpers for writing an ≈80k-word novel without quality collapse.

Standard-library only. Provides:
  * Character / WorldRule / PlotPoint / Chapter / Book dataclasses.
  * Bible — JSON-serializable state (the single source of truth across sessions).
  * Bible.load(path) / Bible.save(path) — persist between chapters.
  * outline_chapters(n, three_act=True) — generate a balanced chapter arc.
  * word_count_target(total, n) — per-chapter target.
  * consistency_check(bible, chapter) — flag character / timeline / plot issues.
  * format_bible_md(bible) — render the bible as Markdown.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal


# ---- Data classes --------------------------------------------------------

@dataclass
class Character:
    name: str
    age: int = 0
    role: str = ""              # protagonist / antagonist / mentor / ...
    voice: str = ""             # 2-3 adjectives describing speech
    want: str = ""              # external goal
    need: str = ""              # internal lesson
    flaw: str = ""              # the thing that costs them
    arc: str = ""               # how they change
    introduced_in_chapter: int = 0
    notes: str = ""


@dataclass
class WorldRule:
    name: str                   # e.g., "Magic costs sleep"
    description: str
    introduced_in_chapter: int = 0


@dataclass
class PlotPoint:
    title: str                  # short name, e.g., "Inciting incident"
    description: str
    chapter: int                # where it occurs
    kind: str = ""              # hook / inciting / midpoint / climax / resolution
    foreshadowed_by: list[str] = field(default_factory=list)  # titles of earlier points
    payed_off_in: list[str] = field(default_factory=list)     # titles of later points


@dataclass
class Chapter:
    number: int
    title: str = ""
    synopsis: str = ""
    pov_character: str = ""
    word_count: int = 0
    end_hook: str = ""          # the cliffhanger / question / turn at chapter end
    notes: str = ""
    file_path: str = ""         # path to the chapter file


@dataclass
class Book:
    title: str
    author: str = ""
    logline: str = ""
    genre: str = ""
    audience: str = ""
    target_words: int = 80_000
    chapter_count: int = 24


# ---- Bible (single source of truth) -------------------------------------

@dataclass
class Bible:
    book: Book
    characters: list[Character] = field(default_factory=list)
    world_rules: list[WorldRule] = field(default_factory=list)
    plot_points: list[PlotPoint] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)  # [{ch, date, event}]
    voice_style: str = ""       # 3 adjectives describing the narrative voice

    # ---- persistence ----

    def to_dict(self) -> dict:
        return {
            "book": asdict(self.book),
            "characters": [asdict(c) for c in self.characters],
            "world_rules": [asdict(w) for w in self.world_rules],
            "plot_points": [asdict(p) for p in self.plot_points],
            "chapters": [asdict(c) for c in self.chapters],
            "timeline": self.timeline,
            "voice_style": self.voice_style,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Bible":
        return cls(
            book=Book(**d.get("book", {})),
            characters=[Character(**c) for c in d.get("characters", [])],
            world_rules=[WorldRule(**w) for w in d.get("world_rules", [])],
            plot_points=[PlotPoint(**p) for p in d.get("plot_points", [])],
            chapters=[Chapter(**c) for c in d.get("chapters", [])],
            timeline=d.get("timeline", []),
            voice_style=d.get("voice_style", ""),
        )

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
                     encoding="utf-8")
        return p

    @classmethod
    def load(cls, path: str | Path) -> "Bible":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


# ---- Outline generator ---------------------------------------------------

def outline_chapters(n: int = 24,
                     three_act: bool = True) -> list[Chapter]:
    """Generate a balanced chapter arc with structural beats pre-assigned.

    For three_act=True and n=24: classic Hollywood 3-act structure.
    Falls back to even split if n is not divisible cleanly.
    """
    if n < 6:
        raise ValueError("Need at least 6 chapters for a meaningful arc.")
    chapters: list[Chapter] = []

    if three_act:
        # Act I: 25%, Act II: 50%, Act III: 25%
        act1 = max(3, n // 4)
        act3 = max(3, n // 4)
        act2 = n - act1 - act3
        beats = {
            1: ("Hook", "hook"),
            act1: ("Inciting incident", "inciting"),
            act1 + act2 // 4: ("First pinch point", "rising"),
            act1 + act2 // 2: ("Midpoint reversal", "midpoint"),
            act1 + 3 * act2 // 4: ("Second pinch point", "rising"),
            act1 + act2: ("All is lost", "all-is-lost"),
            n - 1: ("Climax", "climax"),
            n: ("Resolution", "resolution"),
        }
    else:
        # Even split, no structural labels
        beats = {
            1: ("Opening", "hook"),
            n // 2: ("Midpoint", "midpoint"),
            n: ("Ending", "resolution"),
        }

    for i in range(1, n + 1):
        title, kind = beats.get(i, ("Continuation", "rising"))
        chapters.append(Chapter(
            number=i,
            title=title,
            synopsis="",
            notes=f"[{kind}]" if i in beats else "",
        ))
    return chapters


def word_count_target(total_words: int = 80_000,
                       chapter_count: int = 24) -> int:
    """Per-chapter word target."""
    return total_words // chapter_count


# ---- Consistency check ---------------------------------------------------

def consistency_check(bible: Bible, chapter: Chapter) -> list[str]:
    """Flag obvious issues in a freshly-written chapter.

    Conservative: looks for character names mentioned in the synopsis that
    are not in the bible, missing end hooks, and timeline conflicts.
    """
    issues: list[str] = []
    known_names = {c.name for c in bible.characters}

    # Crude name detection: capitalized words in synopsis (excluding sentence starts).
    import re
    words = re.findall(r"\b[A-Z][a-z]+\b", chapter.synopsis)
    sentence_starts = {w.split()[0] for w in chapter.synopsis.split(". ") if w}
    suspects = {w for w in words if w not in known_names and w not in sentence_starts}
    # Filter common false positives.
    common = {"The", "A", "An", "It", "He", "She", "They", "We", "I", "You",
              "But", "And", "Or", "So", "Then", "When", "Where", "What", "Why",
              "How", "Who", "This", "That", "These", "Those"}
    suspects -= common
    if suspects:
        issues.append(
            f"Possible unknown character(s) in chapter {chapter.number} "
            f"synopsis: {sorted(suspects)}. Add to bible or rename."
        )

    if not chapter.end_hook:
        issues.append(f"Chapter {chapter.number} has no end hook — readers may not turn the page.")

    if chapter.word_count and chapter.word_count < 1500:
        issues.append(f"Chapter {chapter.number} is short ({chapter.word_count} words). Consider expanding or merging.")

    # Plot point foreshadowing audit.
    for pp in bible.plot_points:
        if pp.chapter == chapter.number and pp.foreshadowed_by:
            # Look for earlier chapters that should have set this up.
            earlier = [c for c in bible.chapters if c.number < chapter.number]
            if len(earlier) < len(pp.foreshadowed_by):
                issues.append(
                    f"Plot point '{pp.title}' (ch {chapter.number}) claims "
                    f"{len(pp.foreshadowed_by)} foreshadowing(s) but only "
                    f"{len(earlier)} earlier chapters exist."
                )

    return issues


# ---- Markdown rendering --------------------------------------------------

def format_bible_md(bible: Bible) -> str:
    lines: list[str] = [
        f"# Bible — {bible.book.title}",
        "",
        f"**Logline:** {bible.book.logline}",
        f"**Genre:** {bible.book.genre}  |  **Audience:** {bible.book.audience}",
        f"**Target:** {bible.book.target_words:,} words across "
        f"{bible.book.chapter_count} chapters",
        f"**Voice:** {bible.voice_style or '(not set)'}",
        "",
        "## Characters",
    ]
    for c in bible.characters:
        lines.append(f"### {c.name} ({c.role})")
        lines.append(f"- Age: {c.age}  |  Introduced: ch {c.introduced_in_chapter}")
        lines.append(f"- Want: {c.want}")
        lines.append(f"- Need: {c.need}")
        lines.append(f"- Flaw: {c.flaw}")
        lines.append(f"- Voice: {c.voice}")
        lines.append(f"- Arc: {c.arc}")
        lines.append("")

    lines.append("## World Rules")
    for w in bible.world_rules:
        lines.append(f"- **{w.name}** (ch {w.introduced_in_chapter}): {w.description}")
    lines.append("")

    lines.append("## Plot Points")
    for p in bible.plot_points:
        lines.append(f"- **{p.title}** (ch {p.chapter}, {p.kind}): {p.description}")
        if p.foreshadowed_by:
            lines.append(f"  - Foreshadowed by: {', '.join(p.foreshadowed_by)}")
        if p.payed_off_in:
            lines.append(f"  - Pays off in: {', '.join(p.payed_off_in)}")
    lines.append("")

    lines.append("## Chapters")
    for c in bible.chapters:
        lines.append(f"- Ch {c.number}: {c.title} — {c.synopsis[:80]}")
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    book = Book(
        title="The Last Lighthouse",
        logline="A lighthouse keeper discovers her light is the last thing keeping a sea monster asleep.",
        genre="Literary fantasy",
        audience="Adult",
        target_words=80_000,
        chapter_count=24,
    )
    bible = Bible(
        book=book,
        voice_style="spare, atmospheric, present-tense",
        characters=[
            Character(
                name="Mira", age=42, role="protagonist",
                voice="clipped, ironic, avoids emotion",
                want="to be left alone",
                need="to let someone in",
                flaw="isolationism",
                arc="From hermit to guardian of a community",
                introduced_in_chapter=1,
            ),
            Character(
                name="The Stranger", age=50, role="catalyst",
                voice="warm, cryptic",
                want="to warn Mira",
                need="to be believed",
                flaw="cannot speak plainly",
                arc="Sacrifices himself so Mira can warn the town",
                introduced_in_chapter=3,
            ),
        ],
        world_rules=[
            WorldRule(name="The Light", description="The lighthouse beam keeps the Leviathan asleep. If it goes out for >1 night, it wakes.",
                       introduced_in_chapter=1),
            WorldRule(name="The Tide", description="Spring tides amplify the Leviathan's influence; people act stranger on those nights.",
                       introduced_in_chapter=4),
        ],
        plot_points=[
            PlotPoint(title="Hook", description="Mira finds a body washed up, clutching a chunk of lighthouse lens.",
                       chapter=1, kind="hook"),
            PlotPoint(title="Inciting incident", description="The Stranger arrives, warns her the light is failing.",
                       chapter=6, kind="inciting",
                       foreshadowed_by=["Hook"]),
            PlotPoint(title="Midpoint reversal", description="Mira learns her father knew and chose to die to keep the secret.",
                       chapter=12, kind="midpoint"),
            PlotPoint(title="All is lost", description="The light goes out. The Leviathan stirs.",
                       chapter=18, kind="all-is-lost"),
            PlotPoint(title="Climax", description="Mira relights the beam using the Stranger's sacrifice.",
                       chapter=23, kind="climax"),
            PlotPoint(title="Resolution", description="Mira opens the lighthouse to the town.",
                       chapter=24, kind="resolution"),
        ],
        chapters=outline_chapters(24, three_act=True),
    )

    # Save and reload to verify round-trip.
    out_path = "/tmp/book_bible_demo.json"
    bible.save(out_path)
    loaded = Bible.load(out_path)

    print("=== Bible Markdown ===")
    print(format_bible_md(loaded))

    # Simulate writing chapter 1.
    ch1 = loaded.chapters[0]
    ch1.synopsis = "Mira walks the beach at dawn. She finds a body clutching a chunk of lighthouse lens. The Stranger watches from the cliff."
    ch1.end_hook = "The Stranger starts walking down toward her."
    ch1.word_count = 3350
    print("\n=== Consistency check (ch 1) ===")
    issues = consistency_check(loaded, ch1)
    print("Issues:", issues if issues else "none (clean)")
