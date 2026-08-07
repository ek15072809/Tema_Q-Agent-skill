"""x_post.py — Analyze and rewrite X (Twitter) posts.

Based on the actual xai-org/x-algorithm source (the live "For You" ranker).
The algorithm is now a learned transformer ("Phoenix") that predicts a vector
of engagement probabilities. We optimize for those heads, not legacy weights.

Standard-library only. Provides:
  * ENGAGEMENT_HEADS     — positive probability heads Phoenix predicts.
  * NEGATIVE_HEADS       — negative heads (any one is catastrophic).
  * LEGACY_WEIGHTS       — OLD twitter/the-algorithm-ml recap weights (reference only).
  * RECOMMENDATIONS      — durable, source-verified reach levers.
  * Post                 — text + media + thread flag.
  * analyze_post(post)   — flag patterns that hurt engagement probabilities.
  * rewrite_post(post, goal)  — apply evidence-based improvements.
  * format_critique_md(...)   — Markdown critique + rewrite.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


X_CHAR_LIMIT = 280


# ---- Engagement heads (positive) — maximize these probabilities ---------
# Source: xai-org/x-algorithm/README.md (Phoenix Scorer).

ENGAGEMENT_HEADS: list[str] = [
    "like",
    "reply",
    "repost",
    "quote",
    "click",
    "profile_click",
    "video_view",
    "photo_expand",
    "share",
    "dwell",
    "follow_author",
]

# The single highest historical weight (legacy recap) was reply_engaged_by_author = 75.
# This is the "two-way reply chain" signal — author replies back to a replier.
LEGACY_HIGHEST_SIGNAL = "reply_engaged_by_author"


# ---- Negative heads — minimize these (any one is catastrophic) ----------

NEGATIVE_HEADS: list[dict] = [
    {"name": "report",                "legacy_weight": -369,
     "note": "One report wipes out ~30+ replies. Avoid anything reportable."},
    {"name": "negative_feedback_v2",  "legacy_weight": -74,
     "note": "'Show less' / 'Not interested' clicks. Triggered by spammy / bait content."},
    {"name": "block_author",          "legacy_weight": None,
     "note": "User blocks the author after seeing the post."},
    {"name": "mute_author",           "legacy_weight": None,
     "note": "User mutes the author."},
    {"name": "not_interested",        "legacy_weight": None,
     "note": "Per-user dismissal."},
]


# ---- Legacy weights (twitter/the-algorithm-ml, March 2023) — REFERENCE ONLY
# Do NOT cargo-cult these. Phoenix (live) is a learned transformer.

LEGACY_WEIGHTS: dict[str, float] = {
    "reply_engaged_by_author": 75.0,
    "good_profile_click":      12.0,
    "reply":                   13.5,
    "good_click":              11.0,
    "favorite":                 0.5,
    "retweet":                  1.0,
    "video_playback50":         0.005,
    "negative_feedback_v2":   -74.0,
    "report":                -369.0,
}


# ---- Hard filters (posts that get excluded entirely) --------------------

HARD_FILTERS: list[str] = [
    "AgeFilter — too old (eligibility window; no fixed half-life)",
    "DedupConversationFilter — collapses thread branches; don't over-thread",
    "VFFilter — deleted, spam, gore, PTOS (policy violations)",
    "Self-posts (your own posts are not recommended back to you)",
    "Blocked / muted authors",
    "Muted keywords (per-user)",
    "Previously-seen posts",
    "Paywalled-ineligible (paywalled posts excluded from For You)",
]


# ---- Myths vs confirmed truths ------------------------------------------

MYTHS: list[dict] = [
    {"myth": "External link in body is penalized",
     "truth": "FALSE at feature level. is_open_linked is tracked as POSITIVE engagement. "
              "Links lose only indirectly (fewer dwell/click-throughs)."},
    {"myth": "'RT if' / engagement bait is banned by a rule",
     "truth": "UNCONFIRMED in open code. Punishment is indirect: triggers negative_feedback (-74) "
              "or report (-369)."},
    {"myth": "Reply = 13.5 weight, retweet = 1.0",
     "truth": "LEGACY — from twitter/the-algorithm-ml (March 2023). No longer the live system. "
              "Phoenix is a learned transformer."},
    {"myth": "SimClusters / TwHIN / tweepcred matter",
     "truth": "LEGACY — replaced by learned Phoenix embeddings."},
    {"myth": "Recency has a fixed half-life multiplier",
     "truth": "FALSE — the transformer learns temporal relevance."},
]


# ---- Source-verified recommendations ------------------------------------

RECOMMENDATIONS: list[str] = [
    "Optimize for conversation, not vanity metrics. Replies (esp. author-engaged) historically carried 10-75x the weight of a like. End posts with a genuine question.",
    "Make the author likely to reply back. Two-way reply chains are the single highest-weighted positive signal. If you're the author, plan to engage in the first hour.",
    "Reward dwell & media. dwell, video_view, photo_expand are positive heads. Video (30s+) and strong images help. Long-form text that earns a 2+ min read also helps.",
    "Avoid reportable / annoying patterns. One report (-369) wipes out ~30+ replies. No spammy bait, no aggressive 'RT if,' nothing policy-borderline.",
    "Don't over-thread. DedupConversationFilter collapses thread branches. One strong root post beats many fragmented replies.",
    "Stop optimizing link placement as a 'penalty.' It isn't one. But put the payoff in-body so dwell happens before any outbound click.",
    "Abandon legacy-weight cargo-culting. The live system learns from engagement history via embeddings. Maximize positive-engagement probability, minimize negative.",
]


# ---- Patterns the analyzer flags ----------------------------------------
# Each pattern targets a specific engagement head.

POSITIVE_PATTERNS: list[dict] = [
    {"id": "no_engagement_hook", "head": "reply",
     "check": lambda t: "?" not in t and not re.search(r"\b(what do you|how do you|your take|tell me)\b", t, re.I),
     "msg": "No engagement hook → low P(reply). End with a genuine question or invitation."},
    {"id": "no_first_person", "head": "reply",
     "check": lambda t: not re.search(r"\b(I|we|my|our|me)\b", t, re.I),
     "msg": "No first-person pronoun → feels impersonal, lowers P(reply)."},
    {"id": "no_media", "head": "dwell",
     "check": lambda t: True,  # media tracked separately
     "msg": "No media attached. dwell / video_view / photo_expand are positive heads — add an image or 30s+ video."},
    {"id": "too_short", "head": "dwell",
     "check": lambda t: len(t) < 80,
     "msg": "Very short post → low P(dwell). Add a specific detail or example to extend dwell time."},
    {"id": "no_specific_detail", "head": "dwell",
     "check": lambda t: not re.search(r"\d+", t) and not re.search(r"\b(yesterday|last week|in 20\d{2}|just now)\b", t, re.I),
     "msg": "No specific detail (number, date, name) → generic feel lowers P(dwell)."},
]

NEGATIVE_PATTERNS: list[dict] = [
    {"id": "rt_if_bait", "head": "negative_feedback_v2",
     "check": lambda t: bool(re.search(r"\bRT if\b", t, re.I)),
     "msg": "'RT if' pattern — triggers negative_feedback (-74) and risk of report (-369)."},
    {"id": "vague_outrage", "head": "negative_feedback_v2",
     "check": lambda t: any(p in t.lower() for p in
                          ["read the room", "do better", "this is a take",
                           "imagine being", "y'all really", "literally shaking"]),
     "msg": "Vague outrage bait — risks negative_feedback (-74) and report (-369)."},
    {"id": "engagement_bait", "head": "negative_feedback_v2",
     "check": lambda t: bool(re.search(r"\b(like if|retweet if|reply if|comment if)\b", t, re.I)),
     "msg": "Engagement bait ('like if', 'retweet if') — triggers negative_feedback."},
    {"id": "all_caps_shouting", "head": "negative_feedback_v2",
     "check": lambda t: len(re.findall(r"\b[A-Z]{4,}\b", t)) > 2,
     "msg": "Too many all-caps words (>2) — feels like shouting, raises P(negative_feedback)."},
    {"id": "policy_borderline", "head": "report",
     "check": lambda t: any(w in t.lower() for w in
                          ["kill yourself", "go die", "subhuman", "rm -rf",
                           "child porn", "csam"]),
     "msg": "Policy-borderline content — RISK OF REPORT (-369). Do not post."},
]

HARD_FILTER_RISKS: list[dict] = [
    {"id": "over_threaded", "filter": "DedupConversationFilter",
     "check": lambda t: t.count("🧵") > 0 or bool(re.search(r"\bthread\b.*\b1/\d+\b", t, re.I)),
     "msg": "Over-threaded — DedupConversationFilter may collapse branches. Make the root post stand alone."},
    {"id": "paywalled_signal", "filter": "paywalled-ineligible",
     "check": lambda t: "subscribers only" in t.lower() or "paywall" in t.lower(),
     "msg": "Paywalled posts are excluded from the For You feed for non-subscribers."},
]


# ---- Data class ----------------------------------------------------------

@dataclass
class Post:
    text: str
    media: list[str] = field(default_factory=list)  # ["image"] / ["video"] / ["image","image",...]
    is_thread: bool = False
    hashtags: list[str] = field(default_factory=list)


@dataclass
class Analysis:
    positive_issues: list[str]      # lower P(positive heads)
    negative_issues: list[str]      # raise P(negative heads)
    hard_filter_risks: list[str]    # may get filtered out entirely
    char_count: int
    over_limit: bool


# ---- Analysis ------------------------------------------------------------

def analyze_post(post: Post) -> Analysis:
    """Flag patterns that hurt engagement probabilities or risk hard filters."""
    pos_issues: list[str] = []
    neg_issues: list[str] = []
    hf_risks: list[str] = []

    # Positive patterns (lower P(positive heads)).
    for p in POSITIVE_PATTERNS:
        if p["id"] == "no_media":
            if not post.media:
                pos_issues.append(f"[{p['head']}] {p['msg']}")
        elif p["check"](post.text):
            pos_issues.append(f"[{p['head']}] {p['msg']}")

    # Negative patterns (raise P(negative heads)).
    for p in NEGATIVE_PATTERNS:
        if p["check"](post.text):
            neg_issues.append(f"[{p['head']}] {p['msg']}")

    # Hard filter risks.
    for p in HARD_FILTER_RISKS:
        if p["check"](post.text):
            hf_risks.append(f"[{p['filter']}] {p['msg']}")

    return Analysis(
        positive_issues=pos_issues,
        negative_issues=neg_issues,
        hard_filter_risks=hf_risks,
        char_count=len(post.text),
        over_limit=len(post.text) > X_CHAR_LIMIT,
    )


# ---- Rewrite -------------------------------------------------------------

def rewrite_post(post: Post, goal: str = "conversation") -> Post:
    """Apply evidence-based improvements. Returns a new Post.

    goal: 'conversation' (default — maximize P(reply)) / 'dwell' (maximize P(dwell) via media + length) / 'balanced'.
    """
    text = post.text

    # 1. Remove engagement bait (raises P(negative_feedback)).
    text = re.sub(r"\b(RT if|like if|retweet if|reply if|comment if)\b[^.!?]*", "", text, flags=re.I).strip()

    # 2. Remove vague outrage phrases.
    for phrase in ["read the room", "do better", "this is a take",
                    "imagine being", "y'all really", "literally shaking"]:
        text = re.sub(re.escape(phrase), "", text, flags=re.I).strip()

    # 3. Cap all-caps words to ≤2.
    caps = re.findall(r"\b[A-Z]{4,}\b", text)
    if len(caps) > 2:
        for word in caps[2:]:
            text = text.replace(word, word.capitalize(), 1)

    # 4. If conversation goal and no question, add a genuine one.
    if goal in ("conversation", "balanced") and "?" not in text:
        text = text.rstrip(".!") + ". What's your experience been?"

    # 5. If dwell goal and very short, suggest expansion.
    if goal == "dwell" and len(text) < 120:
        text += " (would love to hear specifics — drop a reply.)"

    # 6. If over-threaded flag, neutralize it.
    text = text.replace("🧵", "").strip()
    text = re.sub(r"\b1/\d+\b", "", text).strip()

    return Post(text=text, media=post.media, is_thread=False,
                hashtags=re.findall(r"#\w+", text))


# ---- Markdown critique ---------------------------------------------------

def format_critique_md(original: Post, analysis: Analysis,
                        rewritten: Post) -> str:
    lines = [
        "# X-Post Critique & Rewrite",
        "",
        "## Original Post",
        f"> {original.text}",
        f"- Characters: {analysis.char_count}/{X_CHAR_LIMIT}",
        f"- Media: {len(original.media)} item(s)",
        "",
        "## Critique (against the live xai-org/x-algorithm)",
        "",
        "### Patterns that lower P(positive heads)",
    ]
    if analysis.positive_issues:
        for m in analysis.positive_issues:
            lines.append(f"- {m}")
    else:
        lines.append("- (none — clean)")
    lines.append("")

    lines.append("### Patterns that raise P(negative heads)")
    if analysis.negative_issues:
        for m in analysis.negative_issues:
            lines.append(f"- {m}")
    else:
        lines.append("- (none — clean)")
    lines.append("")

    lines.append("### Hard-filter risks")
    if analysis.hard_filter_risks:
        for m in analysis.hard_filter_risks:
            lines.append(f"- {m}")
    else:
        lines.append("- (none — clean)")
    lines.append("")

    lines.append("## Rewritten Post")
    lines.append(f"> {rewritten.text}")
    lines.append(f"- Characters: {len(rewritten.text)}/{X_CHAR_LIMIT}")
    lines.append(f"- Media: {len(rewritten.media)} item(s)")
    lines.append("")

    lines.append("## Author Engagement Plan (first 60 minutes)")
    lines.append("- Reply to the first 3-5 responses personally.")
    lines.append("- Quote-tweet a thoughtful reply to extend the thread.")
    lines.append("- This maximizes P(reply_engaged_by_author) — historically the highest-weighted signal.")
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    bad_post = Post(
        text=("RT if you agree! 'Read the room' — this is a take. "
              "Our AMAZING NEW PRODUCT is the BEST THING EVER!!! "
              "y'all really need to wake up. 1/7 🧵"),
    )
    analysis = analyze_post(bad_post)
    rewritten = rewrite_post(bad_post, goal="conversation")
    print(format_critique_md(bad_post, analysis, rewritten))

    print("\n--- Reference: engagement heads (maximize P) ---")
    print(", ".join(ENGAGEMENT_HEADS))
    print("\n--- Reference: negative heads (minimize P) ---")
    for n in NEGATIVE_HEADS:
        w = n["legacy_weight"]
        print(f"  {n['name']:<25} weight={w if w is not None else 'n/a':<6} — {n['note']}")
    print("\n--- Reference: hard filters ---")
    for hf in HARD_FILTERS:
        print(f"  - {hf}")
    print("\n--- Reference: myths to stop believing ---")
    for m in MYTHS:
        print(f"  MYTH: {m['myth']}")
        print(f"  TRUTH: {m['truth']}\n")
