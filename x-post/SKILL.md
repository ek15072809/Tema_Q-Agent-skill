---
name: x-post
description: Analyze and rewrite X (Twitter) posts to maximize reach and engagement, based on the actual xai-org/x-algorithm source. Optimizes for the engagement-probability heads the live Phoenix ranker uses, not legacy hand-engineered weights.
---

# X-Post Skill

## Overview
Improve a drafted X post (or write one from a brief) using the **actual
`xai-org/x-algorithm` source code** (the live "For You" ranker, May 2026).
The algorithm has moved from hand-engineered feature weights to a learned
transformer ("Phoenix") that predicts a vector of engagement probabilities.
We optimize for those heads, not for legacy cargo-culted weights.

## Bundled Helper Module
**`skill/x-post/scripts/x_post.py`** (stdlib only):
- `Post` dataclass — text + media + thread flag.
- `ENGAGEMENT_HEADS` — the positive probability heads Phoenix predicts.
- `NEGATIVE_HEADS` — the negative heads (any one of these is catastrophic).
- `LEGACY_WEIGHTS` — the OLD twitter/the-algorithm-ml recap weights, for reference only.
- `analyze_post(post)` — flag patterns that lower P(positive heads) or raise P(negative heads).
- `rewrite_post(post, goal='conversation')` — apply evidence-based improvements.
- `format_critique_md(...)` — Markdown critique + rewrite.
- `RECOMMENDATIONS` — the durable, source-verified reach levers.

```python
import sys; sys.path.insert(0, "skill/x-post/scripts")
from x_post import (Post, ENGAGEMENT_HEADS, NEGATIVE_HEADS, LEGACY_WEIGHTS,
                     analyze_post, rewrite_post, format_critique_md, RECOMMENDATIONS)
```
Run `python skill/x-post/scripts/x_post.py` for a worked sample.

## How the Live Algorithm Actually Works (xai-org/x-algorithm)

Pipeline (from the repo's README):
```
Query Hydration
  → Candidate Sourcing       (Thunder = in-network; Phoenix Retrieval = OON two-tower ANN)
  → Candidate Hydration      (text, media, author, video duration, subscription)
  → Pre-Scoring Filters
  → Scoring                  (Phoenix Scorer → Weighted Scorer → Author Diversity → OON Scorer)
  → Selection                (top-K)
  → Post-Selection Filters
  → VFFilter                 (deleted / spam / gore)
```

The Phoenix scorer outputs a vector of engagement probabilities. The final
score is approximately:
```
score = Σ(weightᵢ × P(actionᵢ))
```
So **maximize P(positive heads), minimize P(negative heads)** — that's the
entire game. No more chasing a fixed `reply = 13.5` magic number.

## Engagement Heads (what to maximize)

| Positive head | Why it matters |
|---|---|
| `like` | baseline positive signal |
| `reply` | historically ~10× a like (legacy weight 13.5 vs 0.5) |
| `repost` | extends reach to followers-of-followers |
| `quote` | strong engagement; carries the post into a new context |
| `click` | a "good click" (link open) had legacy weight 11 |
| `profile_click` | "good_profile_click" had legacy weight 12 — author interest |
| `video_view` | media dwell signal; long videos do especially well |
| `photo_expand` | image dwell signal |
| `share` | DM share; private virality |
| `dwell` | time-on-post; matters more than people think |
| `follow_author` | converts the impression into a relationship |

**The single highest historical weight** was `reply_engaged_by_author` (75) —
i.e., a reply chain where the original author replies back. Two-way
conversations dominate everything else.

## Negative Heads (what to minimize — these are catastrophic)

| Negative head | Legacy weight | Impact |
|---|---|---|
| `report` | **−369** | one report ≈ −30+ replies |
| `negative_feedback_v2` | **−74** | "show less" / "not interested" clicks |
| `block_author` | large negative | blocks the author |
| `mute_author` | large negative | mutes the author |
| `not_interested` | negative | per-user dismissal |

**Conclusion**: nothing is worth risking a report. Avoid spammy bait,
policy-borderline content, and anything that triggers "show less."

## Hard Filters (Posts That Get Filtered Out Entirely)

- `AgeFilter` — too old (eligibility window, no fixed half-life)
- `DedupConversationFilter` — collapses thread branches; **don't over-thread**
- `VFFilter` — deleted, spam, gore, PTOS (policy violations)
- Self-posts (the algorithm doesn't recommend your own posts back to you)
- Blocked / muted authors
- Muted keywords (per-user)
- Previously-seen posts
- Paywalled-ineligible (Substack-style paywalled posts are excluded from For You)

## Myths to Stop Believing

| Myth | Truth |
|---|---|
| "External link in body is penalized" | **FALSE** at feature level. `is_open_linked` is tracked as a *positive* engagement. Links lose only indirectly (fewer dwell/click-throughs). |
| "RT if" / engagement bait is banned by a rule" | **UNCONFIRMED in open code.** No bait-detection rule is visible. Punishment is *indirect*: bait triggers `negative_feedback` (−74) or `report` (−369). |
| "Reply = 13.5 weight, retweet = 1.0" | **LEGACY** — these weights are from `twitter/the-algorithm-ml` (March 2023), no longer the live system. Phoenix is a learned transformer. |
| "SimClusters / TwHIN / tweepcred scores matter" | **LEGACY** — replaced by learned Phoenix embeddings. |
| "Recency has a fixed half-life multiplier" | **FALSE** — the transformer learns temporal relevance. |

## Source-Verified Reach Recommendations

1. **Optimize for conversation, not vanity metrics.** Replies (esp. author-engaged) historically carried 10–75× the weight of a like. End posts with a *genuine* question or invitation to reply.
2. **Make the author likely to reply back.** Two-way reply chains are the single highest-weighted positive signal. If you're the author, plan to engage with replies in the first hour.
3. **Reward dwell & media.** `dwell`, `video_view`, `photo_expand` are positive heads. Video (especially 30s+) and strong images help. Long-form text that earns a 2+ min read also helps.
4. **Avoid reportable / annoying patterns.** One report (−369) wipes out ~30+ replies. No spammy bait, no aggressive "RT if," nothing policy-borderline.
5. **Don't over-thread.** `DedupConversationFilter` collapses thread branches. One strong root post beats many fragmented replies.
6. **Stop optimizing link placement as a "penalty."** It isn't one. But put the *payoff* in-body so dwell happens before any outbound click.
7. **Abandon legacy-weight cargo-culting.** The live system learns from engagement history via embeddings. The durable truth is "maximize positive-engagement probability, minimize negative."

## Workflow

1. **Receive** the draft post (or a brief: topic + audience + goal).
2. **Analyze** via `analyze_post()`. Note the patterns flagged.
3. **Rewrite** via `rewrite_post()` (rule-based) then refine by hand.
4. **Verify** character count ≤ 280 (X limit for non-premium).
5. **Output** critique + rewritten post + variants.

## Output Format

```markdown
# X-Post Critique & Rewrite

## Original Post
> {original text}
- Characters: {N}/280
- Media: {none / 1 image / video}

## Critique (against the live xai-org/x-algorithm)

### Patterns that lower P(positive heads)
- {issue 1 — e.g., "no engagement hook → low P(reply)"}
- {issue 2}

### Patterns that raise P(negative heads)
- {issue 1 — e.g., "vague outrage language → risk of report/negative_feedback"}
- {issue 2}

### Hard-filter risks
- {issue 1 — e.g., "over-threaded → DedupConversationFilter may collapse"}

## Rewritten Post
> {rewritten text}
- Characters: {N}/280
- Changes: {bullet list of what changed and why}

## Variants
### Variant A (max conversation)
> {ends with a genuine question; designed to trigger reply chains}

### Variant B (max dwell / media)
> {long-form hook with video/image attached}

## Author Engagement Plan (first 60 minutes)
- Reply to the first 3-5 responses personally
- Quote-tweet a thoughtful reply to extend the thread
- This maximizes P(reply_engaged_by_author) — historically the highest-weighted signal

## Hashtag Strategy
- {0-1 specific hashtag, only if it adds context — not for reach}
```

## Self-Check
- [ ] Character count ≤ 280?
- [ ] At least one genuine engagement hook (question / invitation / cliffhanger)?
- [ ] Media attached (image or 30s+ video) when the message benefits from dwell?
- [ ] No spammy bait patterns ("RT if", "👇 link", vague outrage)?
- [ ] No policy-borderline content (the −369 report risk is not worth it)?
- [ ] Author available to reply in the first 60 min (the highest-weighted signal)?
- [ ] Not over-threaded (root post stands on its own)?
- [ ] Variants offered for different goals (conversation vs dwell)?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Chasing legacy weights (reply=13.5) | Optimize for engagement-probability heads, not magic numbers |
| Treating external links as a penalty | They aren't; but put the payoff in-body for dwell |
| Over-threading | One strong root post > many fragmented replies |
| Spammy engagement bait | Triggers negative_feedback (−74) or report (−369) |
| No author reply plan | Two-way reply chains dominate everything else |
| Generic corporate tone | Add first-person / specific detail; raises P(reply) |
| No engagement hook | End with a genuine question or open prompt |
