---
name: meeting
description: Analyze meeting transcripts to extract behavior patterns — speaking ratio, filler words, conflict avoidance, leadership style. Use for 1-on-1s, team meetings, and post-meeting reviews.
---

# Meeting Skill

## Overview
Take a meeting transcript (any format) and surface behavioral patterns
the participants wouldn't notice themselves.
- Speaking ratio (per person, per minute)
- Filler words / verbal tics (frequency, type)
- Conflict-avoidance signals
- Leadership style indicators
- Question-to-statement ratio
- Interruption count

## Bundled Helper Module
**`skill/meeting/scripts/meeting_skill.py`** (stdlib only):
- `Utterance` / `Speaker` / `MeetingAnalysis` dataclasses.
- `FILLER_WORDS` — multilingual filler / hedge / tic bank.
- `LEADERSHIP_SIGNALS` — lexicon for 4 leadership styles.
- `parse_transcript(text, format='auto')` — parse plain / vtt / srt / json.
- `speaking_ratio(utterances)` — words per speaker + per-minute rate.
- `filler_analysis(utterances)` — counts + frequency per speaker.
- `detect_conflict_avoidance(utterances)` — hedging / topic-switch signals.
- `detect_leadership_style(utterances)` — classify each speaker.
- `interruption_count(utterances)` — count overlapping / cut-off turns.
- `format_report_md(analysis)` — Markdown report.

```python
import sys; sys.path.insert(0, "skill/meeting/scripts")
from meeting_skill import (Utterance, Speaker, MeetingAnalysis,
                           parse_transcript, speaking_ratio, filler_analysis,
                           detect_conflict_avoidance, detect_leadership_style,
                           interruption_count, format_report_md)
```
Run `python skill/meeting/scripts/meeting_skill.py` for a worked sample.

## Workflow

1. **Receive transcript** — accept plain text, VTT/SRT, or JSON.
2. **Parse** via `parse_transcript()`. Confirm speaker count.
3. **Compute metrics** (run all four analyses):
   - `speaking_ratio()` — who dominated?
   - `filler_analysis()` — verbal tics per speaker.
   - `detect_conflict_avoidance()` — hedging frequency.
   - `detect_leadership_style()` — style per speaker.
   - `interruption_count()` — overlap / cut-off count.
4. **Surface patterns** — call out the 3 most actionable findings.
5. **Recommendations** — 2-4 concrete behavior changes (not generic advice).
6. **Output** — `format_report_md()`.

## Transcript Formats Accepted

```
# Plain (auto-detected)
Alice: Hi everyone, let's start.
Bob: Sorry I'm late.

# VTT / SRT
00:00:01.000 --> 00:00:03.000
Alice: Hi everyone, let's start.

# JSON
[{"speaker": "Alice", "text": "Hi everyone", "start": 1.0, "end": 3.0}, ...]
```

## Filler / Hedge Bank (multilingual)

Categories tracked:
- Filler: `um, uh, er, ah, like, you know, I mean, sort of, kind of`
- Hedge: `maybe, perhaps, possibly, I guess, I think, probably, somewhat`
- JP: `えー, あー, そのー, まあ, なんか, ですね, というか`
- Tic detection: any word used 5+ times per minute by one speaker.

## Leadership Styles (4 archetypes)

| Style | Signals |
|---|---|
| Directive | imperative verbs, "we need to", "I want", few questions |
| Coaching | questions > statements, "what do you think", "help me understand" |
| Affiliative | names others, "we", "together", positive emotion words |
| Pacesetting | "I'll", first-person action verbs, high self-reference |

A speaker can be a hybrid; the analysis returns the dominant + secondary.

## Output Format

```markdown
# Meeting Analysis — {title}

## Summary
- Duration: {N} min
- Participants: {names}
- Total utterances: {N}

## Speaking Ratio
| Speaker | Words | % | Words/min |
|---|---|---|---|
| Alice | 540 | 60% | 90 |
| Bob | 360 | 40% | 60 |

## Filler Words
| Speaker | Filler count | Top fillers |
|---|---|---|
| Alice | 12 | "like" (5), "you know" (4) |
| Bob | 28 | "um" (15), "I guess" (8) |

## Conflict Avoidance
- Alice: low (2 hedges)
- Bob: high (14 hedges, 3 topic switches)

## Leadership Style
- Alice: Coaching (questions 60%, affiliative cues 20%)
- Bob: Pacesetting (high self-reference, low question ratio)

## Interruptions
- Alice interrupted Bob: 2 times
- Bob interrupted Alice: 0 times

## Top Findings
1. {most actionable finding}
2. {second}
3. {third}

## Recommendations
1. {concrete behavior change}
2. {concrete behavior change}
```

## Self-Check
- [ ] Transcript parsed correctly (speaker count matches)?
- [ ] All 5 analyses run?
- [ ] Top findings are specific (not "communicate better")?
- [ ] Recommendations are concrete behavior changes?
- [ ] Cultural context respected (JP indirect speech ≠ conflict avoidance)?
- [ ] No judgmental language about personality?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Misattributing utterances | Confirm speaker labels after parse |
| Counting "like" as filler when it's a verb | Use word-boundary regex |
| Over-interpreting short meetings | Require ≥5 min for style classification |
| Cultural bias | JP indirectness is politeness, not avoidance |
| Generic recommendations | Tie each rec to a specific finding |
| Personality labels | Describe behavior, not character |
