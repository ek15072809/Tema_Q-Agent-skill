"""brainstorming.py — Helpers for structured ideation.

Standard-library only. Provides:
  * Idea                       — captures raw idea + clarifications.
  * CLARIFICATION_QUESTIONS    — 8 questions that resolve 80% of ambiguity.
  * ALTERNATIVE_LENSES         — 7 lenses to generate alternative approaches.
  * build_clarification_block  — render questions for the user.
  * generate_alternatives      — produce N structured alternatives.
  * evaluate_alternatives      — score alternatives against criteria.
  * format_design_doc          — Markdown design doc.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence


# ---- Question bank -------------------------------------------------------

CLARIFICATION_QUESTIONS: list[str] = [
    "What problem are you actually trying to solve? (state as a problem, not a solution)",
    "Who is the primary user / audience? (be specific: role, context, current behavior)",
    "What does success look like? (name a measurable outcome)",
    "What are the hard constraints? (time, budget, skills, legal, technical)",
    "What's the smallest version that would still be useful?",
    "What existing solutions have you tried or considered? Why did they fall short?",
    "What would make this fail? (worst-case scenario)",
    "Is this a one-off or a recurring need? (affects how much to invest)",
]


# ---- Lenses for divergence ----------------------------------------------

ALTERNATIVE_LENSES: dict[str, str] = {
    "inversion":            "What's the opposite approach? Flip the goal.",
    "constraint_removal":   "What if budget/time/skill were unlimited?",
    "constraint_addition":  "What if you had 1 week and $0?",
    "audience_shift":       "What if a different user was the target?",
    "analog":               "How would a chef / architect / musician solve this?",
    "reduction":            "What's the smallest viable version?",
    "expansion":            "What's the 10x version?",
}


# ---- Data classes --------------------------------------------------------

@dataclass
class Idea:
    title: str
    raw_text: str
    problem: str = ""
    audience: str = ""
    success_metric: str = ""
    constraints: str = ""
    smallest_useful: str = ""
    prior_attempts: str = ""
    failure_mode: str = ""
    recurrence: str = ""      # one-off / recurring


@dataclass
class Alternative:
    name: str
    lens: str
    description: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)


@dataclass
class EvalResult:
    alternative: Alternative
    scores: dict[str, int]        # criterion -> 1..5
    total: int


# ---- Builders ------------------------------------------------------------

def build_clarification_block(idea: Idea) -> str:
    """Render the 8 clarification questions, marking already-answered ones."""
    lines = ["## Clarification Questions", ""]
    answers = {
        "What problem are you actually trying to solve?": idea.problem,
        "Who is the primary user": idea.audience,
        "What does success look like": idea.success_metric,
        "What are the hard constraints": idea.constraints,
        "smallest version": idea.smallest_useful,
        "existing solutions": idea.prior_attempts,
        "would make this fail": idea.failure_mode,
        "one-off or a recurring": idea.recurrence,
    }
    for q in CLARIFICATION_QUESTIONS:
        answered = False
        for fragment, ans in answers.items():
            if fragment in q and ans:
                lines.append(f"- [x] {q}")
                lines.append(f"      → {ans}")
                answered = True
                break
        if not answered:
            lines.append(f"- [ ] {q}")
    return "\n".join(lines)


def generate_alternatives(idea: Idea,
                          lenses: Sequence[str] | None = None,
                          n: int = 3) -> list[Alternative]:
    """Produce N alternative approaches.

    lenses: subset of ALTERNATIVE_LENSES keys. If None, picks the first n.
    The description is a prompt for the agent to fill in — it is intentionally
    a placeholder so the agent must apply real thought, not just print strings.
    """
    if lenses is None:
        keys = list(ALTERNATIVE_LENSES.keys())[:n]
    else:
        keys = list(lenses)[:n]
    alts: list[Alternative] = []
    for k in keys:
        alts.append(Alternative(
            name=f"A{len(alts)+1}: {k.replace('_', ' ').title()}",
            lens=k,
            description=(f"Apply the '{k}' lens to the idea '{idea.title}'. "
                         f"Lens hint: {ALTERNATIVE_LENSES[k]} "
                         f"(agent: fill in 2-4 sentences of concrete approach)."),
        ))
    return alts


def evaluate_alternatives(alts: Sequence[Alternative],
                          criteria: Sequence[str]) -> list[EvalResult]:
    """Score each alternative against each criterion (1-5).

    Scores are placeholders (3 = neutral) — the agent must override them
    based on its actual analysis. The function exists to enforce structure,
    not to make the judgment.
    """
    out: list[EvalResult] = []
    for a in alts:
        scores = {c: 3 for c in criteria}
        out.append(EvalResult(
            alternative=a, scores=scores, total=sum(scores.values()),
        ))
    return out


# ---- Markdown rendering --------------------------------------------------

def format_design_doc(idea: Idea,
                      alts: Sequence[Alternative],
                      evals: Sequence[EvalResult] | None,
                      decision: str,
                      rejected: str = "",
                      next_steps: Sequence[str] | None = None,
                      open_questions: Sequence[str] | None = None) -> str:
    lines = [
        f"# Design Doc — {idea.title}",
        "",
        "## Original Idea",
        idea.raw_text,
        "",
        "## Clarified Scope",
        f"- Problem: {idea.problem or '(unanswered)'}",
        f"- Audience: {idea.audience or '(unanswered)'}",
        f"- Success metric: {idea.success_metric or '(unanswered)'}",
        f"- Constraints: {idea.constraints or '(unanswered)'}",
        f"- Smallest useful: {idea.smallest_useful or '(unanswered)'}",
        f"- Prior attempts: {idea.prior_attempts or '(unanswered)'}",
        f"- Failure mode: {idea.failure_mode or '(unanswered)'}",
        f"- Recurrence: {idea.recurrence or '(unanswered)'}",
        "",
        "## Alternatives Considered",
    ]
    for a in alts:
        lines.append(f"### {a.name}")
        lines.append(f"- Lens: {a.lens}")
        lines.append(f"- Description: {a.description}")
        if a.pros:
            lines.append("- Pros:")
            for p in a.pros:
                lines.append(f"  - {p}")
        if a.cons:
            lines.append("- Cons:")
            for c in a.cons:
                lines.append(f"  - {c}")
        lines.append("")

    if evals:
        criteria = list(evals[0].scores.keys())
        header = "| Alt | " + " | ".join(criteria) + " | Total |"
        sep = "|---|" + "---|" * (len(criteria) + 1)
        lines += ["## Evaluation", header, sep]
        for er in evals:
            row = f"| {er.alternative.name} | "
            row += " | ".join(str(er.scores[c]) for c in criteria)
            row += f" | {er.total} |"
            lines.append(row)
        lines.append("")

    lines += ["## Decision", f"**Selected: {decision}**"]
    if rejected:
        lines.append(f"- Rejected: {rejected}")
    lines.append("")

    if next_steps:
        lines.append("## Next Steps")
        for i, s in enumerate(next_steps, 1):
            lines.append(f"{i}. {s}")
        lines.append("")

    if open_questions:
        lines.append("## Open Questions")
        for q in open_questions:
            lines.append(f"- {q}")
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    idea = Idea(
        title="Mobile habit tracker",
        raw_text="I want to build an app that helps people form habits.",
        problem="People start habits but quit within 2 weeks; existing apps focus on streaks not recovery.",
        audience="Office workers 25-40 who've tried 2+ habit apps and quit.",
        success_metric="30-day retention > 40% (industry avg ~15%).",
        constraints="Solo dev, 3 months, $0 budget, no backend.",
        smallest_useful="A single daily check-in notification + 'restart without shame' button.",
        prior_attempts="Habitica (too gamified), Streaks (too punishing).",
        failure_mode="Users feel guilty when they break a streak and uninstall.",
        recurrence="recurring",
    )
    print(build_clarification_block(idea))
    print()
    alts = generate_alternatives(idea, n=4)
    for a in alts:
        a.pros = ["(agent fills in)"]
        a.cons = ["(agent fills in)"]
    evals = evaluate_alternatives(alts, ["Impact", "Effort", "Risk", "Novelty", "Fit"])
    doc = format_design_doc(
        idea, alts, evals,
        decision="A1: Inversion — reward restarts, not streaks",
        rejected="A4: Expansion (too ambitious for 3 months)",
        next_steps=[
            "Wireframe the 'restart' flow (1 week)",
            "Build a no-backend prototype with local storage (3 weeks)",
            "Recruit 5 users from the target audience for a 2-week diary study",
        ],
        open_questions=[
            "Should we ship iOS first or both?",
            "Pricing model — free, freemium, or paid?",
        ],
    )
    print(doc)
