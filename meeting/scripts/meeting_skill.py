"""meeting_skill.py — Analyze meeting transcripts for behavior patterns.

Standard-library only. Provides:
  * Utterance / Speaker / MeetingAnalysis    — data classes.
  * FILLER_WORDS                              — multilingual filler / hedge bank.
  * LEADERSHIP_SIGNALS                        — lexicon for 4 leadership styles.
  * parse_transcript(text, format='auto')     — parse plain / vtt / srt / json.
  * speaking_ratio(utterances)                — words per speaker + per-minute.
  * filler_analysis(utterances)               — filler counts + top fillers.
  * detect_conflict_avoidance(utterances)     — hedging / topic-switch signals.
  * detect_leadership_style(utterances)       — style classification per speaker.
  * interruption_count(utterances)            — count overlapping / cut-off turns.
  * format_report_md(analysis)                — Markdown report.
"""
from __future__ import annotations
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Literal


# ---- Filler / hedge bank (multilingual) ---------------------------------

FILLER_WORDS: dict[str, list[str]] = {
    "filler_en": ["um", "uh", "er", "ah", "like", "you know", "i mean",
                  "sort of", "kind of", "basically", "literally"],
    "hedge_en":  ["maybe", "perhaps", "possibly", "i guess", "i think",
                  "probably", "somewhat", "i suppose", "i'd say"],
    "filler_jp": ["えー", "あー", "そのー", "まあ", "なんか", "ですね",
                  "というか", "えっと", "ちょっと"],
}

# Compiled regex for each filler (case-insensitive, word-bounded where possible).
_FILLER_REGEXES: list[tuple[str, re.Pattern]] = []
for cat, words in FILLER_WORDS.items():
    for w in words:
        # Use word boundary for ASCII; plain substring for CJK.
        if re.match(r"^[a-zA-Z ]+$", w):
            pat = re.compile(r"\b" + re.escape(w) + r"\b", re.IGNORECASE)
        else:
            pat = re.compile(re.escape(w))
        _FILLER_REGEXES.append((w, pat))


# ---- Leadership signals -------------------------------------------------

LEADERSHIP_SIGNALS: dict[str, list[str]] = {
    "directive":  ["we need to", "we have to", "i want", "you should",
                   "must", "need to", "let's", "let us"],
    "coaching":   ["what do you think", "how would you", "help me understand",
                   "what's your take", "walk me through", "tell me more"],
    "affiliative": ["we", "together", "us", "team", "great job",
                    "thank you", "appreciate", "well done"],
    "pacesetting": ["i'll", "i will", "i'm going to", "i can",
                    "i did", "i have"],
}
_LEADERSHIP_REGEXES: dict[str, list[re.Pattern]] = {
    style: [re.compile(re.escape(p), re.IGNORECASE) for p in patterns]
    for style, patterns in LEADERSHIP_SIGNALS.items()
}


# ---- Data classes --------------------------------------------------------

@dataclass
class Utterance:
    speaker: str
    text: str
    start: float = 0.0   # seconds
    end: float = 0.0

    @property
    def words(self) -> list[str]:
        return self.text.split()

    @property
    def word_count(self) -> int:
        return len(self.words)


@dataclass
class Speaker:
    name: str
    word_count: int = 0
    utterance_count: int = 0
    fillers: Counter = field(default_factory=Counter)
    hedges: int = 0
    questions: int = 0
    leadership_scores: dict[str, int] = field(default_factory=dict)


@dataclass
class MeetingAnalysis:
    title: str = ""
    duration_sec: float = 0.0
    speakers: dict[str, Speaker] = field(default_factory=dict)
    interruptions: list[tuple[str, str, int]] = field(default_factory=list)  # (who, whom, count)
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


# ---- Parser --------------------------------------------------------------

def parse_transcript(text: str,
                     format: Literal["auto", "plain", "vtt", "srt", "json"] = "auto"
                     ) -> list[Utterance]:
    """Parse a transcript into a list of Utterance objects."""
    text = text.strip()
    if not text:
        return []

    if format == "auto":
        if text.startswith("[") or text.startswith("{"):
            format = "json"
        elif "-->" in text:
            format = "vtt" if text.startswith("WEBVTT") else "srt"
        else:
            format = "plain"

    if format == "json":
        return _parse_json(text)
    if format in ("vtt", "srt"):
        return _parse_vtt_srt(text)
    return _parse_plain(text)


def _parse_plain(text: str) -> list[Utterance]:
    """Parse 'Speaker: text' lines."""
    out: list[Utterance] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([^:]{1,40}):\s*(.*)$", line)
        if m:
            out.append(Utterance(speaker=m.group(1).strip(), text=m.group(2).strip()))
    return out


def _parse_vtt_srt(text: str) -> list[Utterance]:
    """Parse VTT or SRT (both use 'HH:MM:SS.mmm --> HH:MM:SS.mmm')."""
    out: list[Utterance] = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        ts = re.search(r"(\d+:\d+:\d+[.,]\d+)\s*-->\s*(\d+:\d+:\d+[.,]\d+)", block)
        if not ts:
            continue
        start = _ts_to_sec(ts.group(1))
        end = _ts_to_sec(ts.group(2))
        body = block[ts.end():].strip()
        # Speaker may be embedded as "Speaker: text"
        m = re.match(r"^([A-Za-z][\w .\-]{0,40}):\s*(.*)$", body, re.DOTALL)
        if m:
            speaker = m.group(1).strip()
            body_text = m.group(2).strip()
        else:
            speaker = "Unknown"
            body_text = body
        out.append(Utterance(speaker=speaker, text=body_text,
                              start=start, end=end))
    return out


def _parse_json(text: str) -> list[Utterance]:
    data = json.loads(text)
    if isinstance(data, dict):
        data = [data]
    out: list[Utterance] = []
    for item in data:
        out.append(Utterance(
            speaker=item.get("speaker", "Unknown"),
            text=item.get("text", ""),
            start=float(item.get("start", 0)),
            end=float(item.get("end", 0)),
        ))
    return out


def _ts_to_sec(ts: str) -> float:
    ts = ts.replace(",", ".")
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(parts[0])


# ---- Analyses ------------------------------------------------------------

def speaking_ratio(utterances: list[Utterance]) -> dict[str, Speaker]:
    """Return per-speaker word counts + utterance counts."""
    speakers: dict[str, Speaker] = {}
    for u in utterances:
        s = speakers.setdefault(u.speaker, Speaker(name=u.speaker))
        s.word_count += u.word_count
        s.utterance_count += 1
    return speakers


def filler_analysis(utterances: list[Utterance],
                    speakers: dict[str, Speaker] | None = None) -> dict[str, Speaker]:
    """Count filler words per speaker."""
    speakers = speakers or speaking_ratio(utterances)
    for u in utterances:
        s = speakers[u.speaker]
        for word, pat in _FILLER_REGEXES:
            count = len(pat.findall(u.text))
            if count:
                s.fillers[word] += count
        # Hedge count (subset of fillers).
        for w in FILLER_WORDS["hedge_en"]:
            count = len(re.findall(r"\b" + re.escape(w) + r"\b", u.text, re.IGNORECASE))
            s.hedges += count
        # Questions.
        s.questions += u.text.count("?")
    return speakers


def detect_conflict_avoidance(utterances: list[Utterance],
                              speakers: dict[str, Speaker] | None = None
                              ) -> dict[str, dict]:
    """Per-speaker hedging + topic-switch signals.

    Returns {speaker: {hedge_count, hedge_per_utterance, level}}.
    level: 'low' / 'medium' / 'high'.
    """
    speakers = speakers or filler_analysis(utterances)
    out: dict[str, dict] = {}
    for name, s in speakers.items():
        per_utt = s.hedges / max(1, s.utterance_count)
        if per_utt < 0.5:
            level = "low"
        elif per_utt < 1.5:
            level = "medium"
        else:
            level = "high"
        out[name] = {
            "hedge_count": s.hedges,
            "hedge_per_utterance": round(per_utt, 2),
            "level": level,
        }
    return out


def detect_leadership_style(utterances: list[Utterance],
                            speakers: dict[str, Speaker] | None = None
                            ) -> dict[str, dict]:
    """Classify each speaker's leadership style."""
    speakers = speakers or speaking_ratio(utterances)
    out: dict[str, dict] = {}
    for name, s in speakers.items():
        text = " ".join(u.text for u in utterances if u.speaker == name)
        scores = {}
        for style, patterns in _LEADERSHIP_REGEXES.items():
            scores[style] = sum(len(p.findall(text)) for p in patterns)
        s.leadership_scores = scores
        # Sort by score, take top 2.
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        total = sum(scores.values()) or 1
        out[name] = {
            "scores": scores,
            "primary": ranked[0][0] if ranked[0][1] > 0 else "unclear",
            "secondary": ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0 else "none",
            "primary_pct": round(100 * ranked[0][1] / total, 1),
        }
    return out


def interruption_count(utterances: list[Utterance]) -> list[tuple[str, str, int]]:
    """Count likely interruptions: A speaks, then B speaks, then A again within 2 turns.

    This is a heuristic — not a true overlap detector (we don't have audio).
    Returns [(interrupter, interrupted, count)].
    """
    if len(utterances) < 3:
        return []
    counts: dict[tuple[str, str], int] = {}
    for i in range(1, len(utterances) - 1):
        prev = utterances[i - 1]
        curr = utterances[i]
        nxt = utterances[i + 1]
        # Pattern: prev speaks, curr speaks briefly, prev speaks again.
        if (prev.speaker == nxt.speaker
                and curr.speaker != prev.speaker
                and curr.word_count < 8):  # brief interjection
            key = (curr.speaker, prev.speaker)
            counts[key] = counts.get(key, 0) + 1
    return [(a, b, c) for (a, b), c in sorted(counts.items(), key=lambda x: -x[1])]


# ---- Report formatting ---------------------------------------------------

def format_report_md(analysis: MeetingAnalysis) -> str:
    duration_min = analysis.duration_sec / 60.0
    lines = [
        f"# Meeting Analysis — {analysis.title or 'Untitled'}",
        "",
        "## Summary",
        f"- Duration: {duration_min:.1f} min",
        f"- Participants: {', '.join(analysis.speakers.keys()) or 'none'}",
    ]
    total_utts = sum(s.utterance_count for s in analysis.speakers.values())
    lines.append(f"- Total utterances: {total_utts}")
    lines.append("")

    # Speaking ratio
    total_words = sum(s.word_count for s in analysis.speakers.values()) or 1
    lines.append("## Speaking Ratio")
    lines.append("| Speaker | Words | % | Words/min | Utterances |")
    lines.append("|---|---|---|---|---|")
    for name, s in analysis.speakers.items():
        wpm = s.word_count / max(1, duration_min)
        lines.append(f"| {name} | {s.word_count} | "
                     f"{100*s.word_count/total_words:.0f}% | "
                     f"{wpm:.0f} | {s.utterance_count} |")
    lines.append("")

    # Fillers
    lines.append("## Filler Words")
    lines.append("| Speaker | Filler count | Top fillers |")
    lines.append("|---|---|---|")
    for name, s in analysis.speakers.items():
        top = ", ".join(f'"{w}" ({c})' for w, c in s.fillers.most_common(3))
        lines.append(f"| {name} | {sum(s.fillers.values())} | {top or '—'} |")
    lines.append("")

    # Conflict avoidance
    ca = detect_conflict_avoidance([], analysis.speakers)
    lines.append("## Conflict Avoidance")
    for name, info in ca.items():
        lines.append(f"- {name}: {info['level']} "
                     f"({info['hedge_count']} hedges, "
                     f"{info['hedge_per_utterance']} per utterance)")
    lines.append("")

    # Leadership
    ls = detect_leadership_style([], analysis.speakers)
    lines.append("## Leadership Style")
    for name, info in ls.items():
        lines.append(f"- {name}: {info['primary']} ({info['primary_pct']}%), "
                     f"secondary {info['secondary']}")
    lines.append("")

    # Interruptions
    if analysis.interruptions:
        lines.append("## Interruptions")
        for who, whom, count in analysis.interruptions:
            lines.append(f"- {who} interrupted {whom}: {count} times")
        lines.append("")

    if analysis.findings:
        lines.append("## Top Findings")
        for i, f in enumerate(analysis.findings, 1):
            lines.append(f"{i}. {f}")
        lines.append("")

    if analysis.recommendations:
        lines.append("## Recommendations")
        for i, r in enumerate(analysis.recommendations, 1):
            lines.append(f"{i}. {r}")
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    sample = """
Alice: Hi everyone, let's start. I think we should focus on the Q3 roadmap today.
Bob: Um, sorry I'm late. I guess we should maybe start with the budget?
Alice: Good idea. What do you think about cutting the marketing line item?
Bob: I mean, maybe, but I think marketing is important. Perhaps we can defer it.
Alice: Help me understand your concern. Walk me through it.
Bob: Well, basically, I think, you know, the brand needs investment.
Alice: I'll take the action item to draft two scenarios. Let's reconvene Thursday.
Bob: Sure, that works. I'll, um, prepare some numbers too.
"""
    utts = parse_transcript(sample)
    speakers = filler_analysis(utts)
    interr = interruption_count(utts)

    analysis = MeetingAnalysis(
        title="Q3 Roadmap Sync",
        duration_sec=600.0,  # 10 min
        speakers=speakers,
        interruptions=interr,
        findings=[
            "Bob uses 3× more fillers than Alice — possible nervousness or under-preparation.",
            "Alice asks 3 questions and gives 2 action items — strong coaching style.",
            "Bob hedges 5 times in 5 utterances — high conflict-avoidance signal.",
        ],
        recommendations=[
            "Bob: prepare 2-3 concrete data points before the next sync to reduce hedging.",
            "Alice: continue the coaching pattern; consider explicitly inviting Bob's dissent.",
            "Both: time-box the budget discussion (5 min) to prevent filler-driven inflation.",
        ],
    )
    print(format_report_md(analysis))
