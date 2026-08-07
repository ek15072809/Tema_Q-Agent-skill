---
name: brainstorming
description: Turn vague ideas into concrete designs through structured questioning and alternative exploration. Use for any product / feature / project ideation where the user's initial idea is ambiguous.
---

# Brainstorming Skill

## Overview
Convert a fuzzy idea into a concrete, decision-ready design.
Core loop: **clarify → diverge → converge → decide**.

## Bundled Helper Module
**`skill/brainstorming/scripts/brainstorming.py`** (stdlib only):
- `Idea` dataclass — captures the user's raw idea + clarifications.
- `CLARIFICATION_QUESTIONS` — 8 questions that resolve 80% of ambiguity.
- `ALTERNATIVE_LENSES` — 7 lenses to generate alternative approaches.
- `build_clarification_block(idea)` — render questions for the user.
- `generate_alternatives(idea, n=3)` — produce N structured alternatives.
- `evaluate_alternatives(alts, criteria)` — score alternatives against criteria.
- `format_design_doc(idea, alts, decision)` — Markdown design doc.

```python
import sys; sys.path.insert(0, "skill/brainstorming/scripts")
from brainstorming import (Idea, CLARIFICATION_QUESTIONS, ALTERNATIVE_LENSES,
                           build_clarification_block, generate_alternatives,
                           evaluate_alternatives, format_design_doc)
```
Run `python skill/brainstorming/scripts/brainstorming.py` to see a full sample.

## Workflow

### Phase 1 — Capture & Clarify
1. Capture the raw idea verbatim.
2. Apply `CLARIFICATION_QUESTIONS` — ask up to 8 questions, batched.
3. Use `question` tool once with multiple questions (not 8 separate turns).
4. After answers, build an `Idea` object with all clarifications filled.

### Phase 2 — Diverge (Generate Alternatives)
Use `ALTERNATIVE_LENSES` to look at the idea from 7 angles:
- **Inversion** — what's the opposite approach?
- **Constraint removal** — what if budget/time/skill were unlimited?
- **Constraint addition** — what if you had 1 week and $0?
- **Audience shift** — what if a different user was the target?
- **Analog** — how would a chef / architect / musician solve this?
- **Reduction** — what's the smallest viable version?
- **Expansion** — what's the 10× version?

For each lens, generate 1 alternative via `generate_alternatives(idea, n=3)`.

### Phase 3 — Converge (Evaluate)
Pick 3-5 evaluation criteria with the user:
- Impact (1-5)
- Effort (1-5, lower = better)
- Risk (1-5, lower = better)
- Novelty (1-5)
- Fit with constraints (1-5)

Run `evaluate_alternatives(alts, criteria)`. Surface the top scorer.

### Phase 4 — Decide & Document
1. Pick the winning alternative (or hybrid).
2. State explicitly what was rejected and why.
3. Produce the design doc via `format_design_doc(...)`.

## Output Format

```markdown
# Design Doc — {title}

## Original Idea
{raw user text}

## Clarified Scope
- Problem: ...
- Audience: ...
- Constraints: ...
- Success metric: ...

## Alternatives Considered
### A1: {name}
- Lens: ...
- Description: ...
- Pros / Cons: ...

### A2: ...
### A3: ...

## Evaluation
| Alt | Impact | Effort | Risk | Novelty | Fit | Total |
|---|---|---|---|---|---|---|
| A1 | 4 | 3 | 2 | 4 | 5 | 18 |
| A2 | 5 | 4 | 3 | 3 | 4 | 17 |

## Decision
**Selected: A1 (hybrid with A2's onboarding flow)**
- Rejected: A3 (too risky given timeline)
- Reason: ...

## Next Steps
1. ...
2. ...
3. ...

## Open Questions
- ...
```

## Self-Check
- [ ] Raw idea captured verbatim?
- [ ] All 8 clarification questions asked (or fewer if answered up front)?
- [ ] At least 3 alternatives generated using different lenses?
- [ ] Evaluation criteria agreed with user?
- [ ] Decision explicit, with rejection reason?
- [ ] Next steps are concrete and ordered?
- [ ] Open questions listed (don't pretend everything is resolved)?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Skipping clarification | Phase 1 is mandatory — never diverge on a vague idea |
| All alternatives similar | Force different lenses; pick opposites deliberately |
| Picking highest score blindly | Surface trade-offs; sometimes #2 is the right call |
| No rejection reason | Always say what was rejected and why |
| Vague next steps | Each step must have an owner + verb + deliverable |
| Pretending no open questions | Always list what's still unknown |
