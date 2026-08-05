"""note_skill.py — Helpers for generating note.com articles.

Workflow this module supports:
  1. Agent searches note.com for popular articles on the user's theme.
  2. Agent fills a PopularNote dataclass for each article found.
  3. analyze_popular_notes() extracts common patterns from a list.
  4. Agent writes a NoteArticle using the analysis as guidance.
  5. render_article_md() formats the final article.
  6. check_note_compliance() validates note.com format rules.

This module deliberately does NOT include hardcoded "winning title templates" —
the agent must derive patterns from real, freshly-searched popular notes.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from typing import Sequence


# ---- Data structures -----------------------------------------------------

@dataclass
class PopularNote:
    """Metadata for a popular note.com article found via search.

    Fill these fields after webfetch-ing the article URL.
    """
    url: str
    title: str
    title_len: int = 0
    lead: str = ""                   # first ~50 chars of the body
    body_chars: int = 0              # total character count
    heading_count: int = 0           # number of ## ### headings
    image_count: int = 0
    hashtags: list[str] = field(default_factory=list)
    likes: int | None = None         # if visible

    def __post_init__(self) -> None:
        if not self.title_len:
            self.title_len = len(self.title)


@dataclass
class NoteArticle:
    """The article the agent will produce."""
    title: str
    lead: str                          # ≤50 chars, shows on X shares
    body_md: str                       # full body in note-compatible Markdown
    cover_brief: str                   # textual brief for the cover image
    hashtags: list[str] = field(default_factory=list)


@dataclass
class PatternReport:
    """Result of analyze_popular_notes()."""
    avg_title_len: float
    avg_body_chars: float
    avg_heading_count: float
    avg_image_count: float
    avg_hashtag_count: float
    common_hashtags: list[str]         # top hashtags by frequency
    title_structures: list[str]        # observed structures (free text)
    notes: list[PopularNote]           # the source notes


# ---- Pattern analysis ----------------------------------------------------

def _detect_title_structures(titles: Sequence[str]) -> list[str]:
    """Detect common structural cues from a list of titles.

    Returns a de-duplicated list of observed cues (e.g. "number-included",
    "question", "brackets", "before-after", "confession").
    """
    cues: set[str] = set()
    for t in titles:
        s = t.strip()
        if any(ch.isdigit() for ch in s):
            cues.add("number-included")
        if s.endswith("?") or s.endswith("？"):
            cues.add("question")
        if "【" in s or "[" in s:
            cues.add("brackets")
        if "→" in s or "から" in s:
            cues.add("before-after")
        if "失敗" in s or "やらかし" in s or "できなかった" in s:
            cues.add("confession")
        if "初心者" in s or "はじめて" in s or "入門" in s:
            cues.add("beginner-targeted")
        if "月" in s and ("円" in s or "万" in s):
            cues.add("income-amount")
        if "選" in s or "つ" in s:
            cues.add("list-count")
    return sorted(cues)


def analyze_popular_notes(notes: Sequence[PopularNote]) -> PatternReport:
    """Extract common patterns from a list of popular notes.

    Pass at least 3 notes for meaningful statistics. With fewer, the
    averages are still computed but title_structures may be sparse.
    """
    n = len(notes)
    if n == 0:
        raise ValueError("Cannot analyze an empty list of notes")

    all_tags: list[str] = []
    for note in notes:
        all_tags.extend(note.hashtags)
    tag_counter = Counter(all_tags)
    common = [tag for tag, _ in tag_counter.most_common(10)]

    return PatternReport(
        avg_title_len=sum(x.title_len for x in notes) / n,
        avg_body_chars=sum(x.body_chars for x in notes) / n,
        avg_heading_count=sum(x.heading_count for x in notes) / n,
        avg_image_count=sum(x.image_count for x in notes) / n,
        avg_hashtag_count=sum(len(x.hashtags) for x in notes) / n,
        common_hashtags=common,
        title_structures=_detect_title_structures([x.title for x in notes]),
        notes=list(notes),
    )


def format_pattern_report(r: PatternReport) -> str:
    """Render a PatternReport as Markdown for inclusion in the agent's output."""
    lines = [
        "## Pattern Analysis Report",
        "",
        f"- Notes analyzed: {len(r.notes)}",
        f"- Avg title length: {r.avg_title_len:.1f} chars",
        f"- Avg body length:  {r.avg_body_chars:.0f} chars",
        f"- Avg heading count: {r.avg_heading_count:.1f}",
        f"- Avg image count:  {r.avg_image_count:.1f}",
        f"- Avg hashtag count: {r.avg_hashtag_count:.1f}",
        f"- Title structures observed: {', '.join(r.title_structures) or 'none'}",
        f"- Common hashtags: {', '.join(r.common_hashtags) or 'none'}",
        "",
        "### Source URLs",
    ]
    for note in r.notes:
        lines.append(f"- {note.url} — {note.title}")
    return "\n".join(lines)


# ---- Article rendering ---------------------------------------------------

def render_article_md(article: NoteArticle) -> str:
    """Render the article as a single Markdown string with metadata blocks."""
    lines = [
        f"# {article.title}",
        "",
        f"> {article.lead}",
        "",
        "---",
        "",
        article.body_md,
        "",
        "---",
        "",
        "## まとめ",
        "",
        "（3行で要点をまとめる）",
        "",
        "---",
        "",
        "スキ・コメント・フォローいただけると励みになります！",
        "",
        "---",
        "",
        "**カバー画像案:** " + article.cover_brief,
        "",
        "**ハッシュタグ:** " + " ".join(f"#{t}" for t in article.hashtags),
    ]
    return "\n".join(lines)


# ---- Cover image brief ---------------------------------------------------

def cover_image_brief(theme: str,
                      tone: str = "editorial",
                      palette: tuple[str, ...] = ("#FAFAF7", "#1A1A1A", "#D4502A")
                      ) -> str:
    """Return a textual brief for the 1280×670 cover image.

    The agent should refine this brief based on the actual article content
    and the patterns observed in popular notes (colors, typography style).
    """
    bg, text, accent = palette
    return (
        f"Cover image (1280×670px, ratio 1.91:1). "
        f"Theme: {theme}. Tone: {tone}. "
        f"Suggested palette: bg {bg}, text {text}, accent {accent}. "
        f"Keep text large & legible at thumbnail size. "
        f"Avoid stock-photo clichés. Prefer a single bold typographic treatment."
    )


# ---- Compliance check ----------------------------------------------------

# note.com does NOT support these Markdown features.
# Patterns are intentionally simple — they catch the common mistakes.
NON_SUPPORTED_PATTERNS: list[tuple[str, str]] = [
    ("h1_hash",     r"(?m)^# [^#]"),            # '# heading' is not supported
    ("h4_plus",     r"(?m)^####+ "),            # h4-h6 not supported
    ("image_md",    r"!\[[^\]]*\]\([^)]*\)"),   # ![](url) does not work
    ("table_pipe",  r"^\|.*\|.*\|"),             # tables not supported
    ("checklist",   r"^- \[ \] "),               # checklist not supported
]


def check_note_compliance(md: str) -> list[str]:
    """Return list of compliance issues found in *md*.

    Empty list means the Markdown is compatible with note.com's editor.
    This catches the most common mistakes; it does not guarantee full
    compatibility (e.g., center-alignment cannot be detected from text).
    """
    import re
    issues: list[str] = []
    for name, pattern in NON_SUPPORTED_PATTERNS:
        if re.search(pattern, md, re.MULTILINE):
            issues.append(name)
    return issues


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    # Simulate the analysis phase with a few PopularNote instances.
    notes = [
        PopularNote(
            url="https://note.com/example/n/abc123",
            title="たった3ヶ月でフォロワー1万人。note×X運用の裏側を公開",
            title_len=27,
            lead="note×X運用で3ヶ月。何を変えたか、全部書きます。",
            body_chars=1850,
            heading_count=6,
            image_count=3,
            hashtags=["note", "ライティング", "note運用", "初心者向け"],
            likes=320,
        ),
        PopularNote(
            url="https://note.com/example/n/def456",
            title="noteで月5万円稼ぐまでにやった5つのこと",
            title_len=20,
            lead="副業noteで月5万円。失敗談も含めて全部書きます。",
            body_chars=1620,
            heading_count=5,
            image_count=2,
            hashtags=["note", "副業", "稼ぐ", "note運用"],
            likes=210,
        ),
        PopularNote(
            url="https://note.com/example/n/ghi789",
            title="【初心者向け】読まれるnote記事の書き方7選",
            title_len=22,
            lead="初心者でも読まれる記事が書ける。具体的な手順を解説。",
            body_chars=2100,
            heading_count=8,
            image_count=4,
            hashtags=["note", "ライティング", "初心者向け", "SEO"],
            likes=450,
        ),
    ]

    report = analyze_popular_notes(notes)
    print(format_pattern_report(report))
    print("\n--- Compliance check (sample article) ---")

    article = NoteArticle(
        title="検索駆動でnote記事を書く方法",
        lead="人気記事を検索→分析→執筆の流れを完全可視化。",
        body_md=(
            "## なぜ検索から始めるのか\n\n"
            "人気記事のパターンを知らずに書くのは当てずっぽう。\n\n"
            "## 手順\n\n"
            "- websearchで人気記事を5〜10件取得\n"
            "- 各記事のタイトル・文字数・見出し数を記録\n"
            "- 共通パターンを抽出\n"
            "- それを参考に執筆\n\n"
            "[画像挿入: フロー図（推奨1280×670px）]\n"
        ),
        cover_brief=cover_image_brief("note執筆フロー"),
        hashtags=["note", "ライティング", "note運用"],
    )

    md = render_article_md(article)
    issues = check_note_compliance(md)
    print("Issues:", issues if issues else "none (clean)")
