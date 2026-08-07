"""target_company.py — B2B sales prospecting pipeline helpers.

Standard-library only. Provides:
  * Product / ICP / Lead / OutreachPlan dataclasses.
  * ICRITERIA                       — scoring rubric (max 100).
  * score_lead(lead, icp)           — returns grade A/B/C/D + breakdown.
  * rank_leads(leads, icp)          — sort by score, group by grade.
  * build_outreach(lead, channel)   — skeleton email / LinkedIn message.
  * format_pipeline_md(...)         — full Markdown pipeline report.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


# ---- Data classes --------------------------------------------------------

@dataclass
class Product:
    name: str
    what: str               # 1-line description
    target_user: str        # role / persona
    price: str              # "$X/mo" or "enterprise"
    differentiator: str     # 1-line unique value
    url: str = ""


@dataclass
class ICP:
    industry: list[str] = field(default_factory=list)
    min_employees: int = 0
    max_employees: int = 0
    geography: list[str] = field(default_factory=list)
    tech_signals: list[str] = field(default_factory=list)  # e.g., "uses Salesforce"
    triggers: list[str] = field(default_factory=list)      # e.g., "recently funded"


@dataclass
class Lead:
    company: str
    url: str = ""
    industry: str = ""
    employees: int = 0
    geography: str = ""
    tech_signals: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)      # observed triggers
    contact_name: str = ""
    contact_role: str = ""
    contact_linkedin: str = ""
    contact_email: str = ""
    notes: str = ""


@dataclass
class ScoredLead:
    lead: Lead
    score: int
    grade: str              # A / B / C / D
    breakdown: dict[str, int]
    top_trigger: str = ""


@dataclass
class OutreachPlan:
    lead: Lead
    sequence: list[dict] = field(default_factory=list)
    personalization_angle: str = ""


# ---- Scoring rubric ------------------------------------------------------

ICRITERIA: dict[str, dict] = {
    # category: {signal: max_points}
    "fit": {
        "industry_match": 20,
        "size_in_range": 15,
        "geography_match": 10,
        "tech_signal_present": 10,
    },
    "intent": {
        "recent_funding": 15,
        "hiring_relevant_role": 10,
        "recent_product_launch": 10,
    },
    "accessibility": {
        "public_contact": 5,
        "linkedin_outreach": 3,
        "referral_path": 2,
    },
}
MAX_SCORE = sum(sum(cat.values()) for cat in ICRITERIA.values())  # 100


# ---- Scoring -------------------------------------------------------------

def score_lead(lead: Lead, icp: ICP) -> ScoredLead:
    """Score a lead against the ICP. Returns grade A/B/C/D + breakdown."""
    bd: dict[str, int] = {}

    # Fit
    bd["industry_match"] = 20 if lead.industry in icp.industry else 0
    if icp.min_employees <= lead.employees <= icp.max_employees:
        bd["size_in_range"] = 15
    elif lead.employees == 0:
        bd["size_in_range"] = 5   # unknown — partial credit
    else:
        bd["size_in_range"] = 0
    bd["geography_match"] = 10 if lead.geography in icp.geography else 0
    matching_tech = [t for t in lead.tech_signals if t in icp.tech_signals]
    bd["tech_signal_present"] = 10 if matching_tech else 0

    # Intent
    bd["recent_funding"] = 15 if any("fund" in t.lower() for t in lead.triggers) else 0
    bd["hiring_relevant_role"] = 10 if any("hir" in t.lower() for t in lead.triggers) else 0
    bd["recent_product_launch"] = 10 if any(
        ("launch" in t.lower() or "expand" in t.lower() or "announce" in t.lower())
        for t in lead.triggers
    ) else 0

    # Accessibility
    bd["public_contact"] = 5 if lead.contact_email else 0
    bd["linkedin_outreach"] = 3 if lead.contact_linkedin else 0
    bd["referral_path"] = 2 if lead.notes.lower().startswith("referral:") else 0

    total = sum(bd.values())
    if total >= 80:
        grade = "A"
    elif total >= 60:
        grade = "B"
    elif total >= 40:
        grade = "C"
    else:
        grade = "D"

    top_trigger = lead.triggers[0] if lead.triggers else ""
    return ScoredLead(lead=lead, score=total, grade=grade,
                       breakdown=bd, top_trigger=top_trigger)


def rank_leads(leads: list[Lead], icp: ICP) -> dict[str, list[ScoredLead]]:
    """Score and group leads by grade. Returns {'A': [...], 'B': [...], ...}."""
    scored = [score_lead(l, icp) for l in leads]
    scored.sort(key=lambda s: -s.score)
    out: dict[str, list[ScoredLead]] = {"A": [], "B": [], "C": [], "D": []}
    for s in scored:
        out[s.grade].append(s)
    return out


# ---- Outreach ------------------------------------------------------------

Channel = Literal["email", "linkedin", "followup"]


def build_outreach(lead: Lead,
                   channel: Channel,
                   sender_name: str = "[your name]",
                   product: Product | None = None,
                   calendar_link: str = "[calendar link]") -> OutreachPlan:
    """Build a skeleton outreach message for the given channel.

    The message is a template — the agent must personalize the {placeholders}
    before sending.
    """
    trigger = lead.triggers[0] if lead.triggers else "your recent work"
    first = (lead.contact_name.split()[0] if lead.contact_name else "[first]")
    company = lead.company

    if channel == "email":
        msg = (
            f"Subject: {trigger} — quick idea for {lead.contact_role or 'your team'}\n\n"
            f"Hi {first},\n\n"
            f"Saw {trigger}. Congrats.\n\n"
            f"{product.what if product else '[product one-liner]'} "
            f"helps {product.target_user if product else '[role]'} "
            f"{('achieve ' + product.differentiator) if product else '[outcome]'}.\n"
            f"Worth a 15-min call next week?\n\n"
            f"— {sender_name}"
        )
    elif channel == "linkedin":
        msg = (
            f"Hi {first} — sent you a note about {trigger} last week. "
            f"If email got buried, happy to share the one-pager here. "
            f"Either way, thanks for the work you're doing at {company}."
        )
    else:  # followup
        msg = (
            f"Subject: re: {trigger} — quick idea\n\n"
            f"Hi {first} — circling back. If timing's off, no worries; "
            f"happy to reconnect next quarter. If a 10-min call makes sense, "
            f"here's my calendar: {calendar_link}."
        )

    return OutreachPlan(
        lead=lead,
        sequence=[{"channel": channel, "message": msg}],
        personalization_angle=f"Anchor on trigger: {trigger}",
    )


# ---- Markdown pipeline report -------------------------------------------

def format_pipeline_md(product: Product, icp: ICP,
                        scored: dict[str, list[ScoredLead]]) -> str:
    lines = [
        f"# Sales Pipeline — {product.name}",
        "",
        "## Product",
        f"- What: {product.what}",
        f"- For: {product.target_user}",
        f"- Price: {product.price}",
        f"- Differentiator: {product.differentiator}",
        "",
        "## ICP",
        f"- Industry: {', '.join(icp.industry) or '—'}",
        f"- Size: {icp.min_employees}-{icp.max_employees} employees",
        f"- Geography: {', '.join(icp.geography) or '—'}",
        f"- Tech signals: {', '.join(icp.tech_signals) or '—'}",
        f"- Triggers: {', '.join(icp.triggers) or '—'}",
        "",
        "## Candidate Pipeline",
        "| # | Company | Industry | Size | Score | Grade | Trigger |",
        "|---|---|---|---|---|---|---|",
    ]
    n = 0
    for grade in ("A", "B", "C", "D"):
        for s in scored.get(grade, []):
            n += 1
            lines.append(f"| {n} | {s.lead.company} | {s.lead.industry} | "
                         f"{s.lead.employees} | {s.score} | {s.grade} | "
                         f"{s.top_trigger or '—'} |")
    lines.append("")

    for grade in ("A", "B"):
        leads = scored.get(grade, [])
        if not leads:
            continue
        section = "Outreach This Week" if grade == "A" else "Nurture"
        lines.append(f"## {grade}-Leads — {section}")
        for i, s in enumerate(leads, 1):
            lines.append(f"### {i}. {s.lead.company} (score {s.score})")
            lines.append(f"- Trigger: {s.top_trigger or 'none identified'}")
            lines.append(f"- Contact: {s.lead.contact_name} "
                         f"({s.lead.contact_role}) "
                         f"{s.lead.contact_linkedin or s.lead.contact_email}")
            lines.append(f"- Personalization angle: anchor on the trigger above")
            lines.append("")

    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    product = Product(
        name="Acme CRM",
        what="A lightweight CRM for sales-led startups",
        target_user="VP Sales at 50-200 person SaaS companies",
        price="$29/user/mo",
        differentiator="set up in <10 min, no implementation team needed",
    )
    icp = ICP(
        industry=["SaaS", "Fintech"],
        min_employees=50, max_employees=500,
        geography=["US", "Japan"],
        tech_signals=["uses Salesforce", "uses HubSpot"],
        triggers=["recently funded", "hiring AE"],
    )
    leads = [
        Lead(company="Acme", url="https://acme.com", industry="SaaS",
             employees=200, geography="US",
             tech_signals=["uses Salesforce"],
             triggers=["Series B announced 2025-07-15", "hiring AE"],
             contact_name="Jane Doe", contact_role="VP Eng",
             contact_linkedin="https://linkedin.com/in/janedoe",
             contact_email="jane@acme.com"),
        Lead(company="Beta", url="https://beta.com", industry="Fintech",
             employees=80, geography="Japan",
             triggers=["hiring SDR"],
             contact_name="Taro Yamada", contact_role="Head of Sales",
             contact_linkedin="https://linkedin.com/in/taroy"),
        Lead(company="Gamma", url="https://gamma.com", industry="Retail",
             employees=2000, geography="US",
             triggers=[],
             contact_email="info@gamma.com"),
    ]
    scored = rank_leads(leads, icp)
    print(format_pipeline_md(product, icp, scored))

    print("\n--- Sample outreach (Acme, email) ---")
    plan = build_outreach(leads[0], "email", product=product)
    print(plan.sequence[0]["message"])
