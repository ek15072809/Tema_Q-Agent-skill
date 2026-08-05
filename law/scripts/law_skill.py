"""law_skill.py — Helpers for structured legal analysis by jurisdiction.

Standard-library only. Provides:
  * JURISDICTIONS              — primary-source URLs by jurisdiction.
  * SEARCH_QUERY_TEMPLATES    — websearch patterns per jurisdiction.
  * Statute / Case / LegalIssue / Analysis dataclasses.
  * build_irac(...)           — IRAC structure builder.
  * build_creac(...)          — CREAC (conclusion-first) builder.
  * format_analysis_md(...)   — render analysis as Markdown.
  * format_demand_letter(...) — US-style demand letter template.
  * format_legal_opinion(...) — JP-style legal opinion template.
"""
from __future__ import annotations
from dataclasses import dataclass, field


# ---- Jurisdictions & primary sources -------------------------------------

JURISDICTIONS: dict[str, dict] = {
    "JP": {
        "statute_url": "https://laws.e-gov.go.jp/",
        "case_url":    "https://www.courts.go.jp/app/hanrei_jp/list1",
        "search_tips": "Use e-Gov for current statute text; courts.go.jp for case law.",
    },
    "US-federal": {
        "statute_url": "https://www.law.cornell.edu/uscode/text",
        "case_url":    "https://www.law.cornell.edu/supremecourt/text",
        "search_tips": "Cornell LII for USC; SCOTUS for federal constitutional questions.",
    },
    "US-state": {
        "statute_url": "Search the state legislature site",
        "case_url":    "https://scholar.google.com/scholar_courts",
        "search_tips": "Each state has its own legislature site; Google Scholar for state case law.",
    },
    "EU": {
        "statute_url": "https://eur-lex.europa.eu/",
        "case_url":    "https://curia.europa.eu/juris/",
        "search_tips": "EUR-Lex for regulations/directives; InfoCuria for CJEU judgments.",
    },
    "UK": {
        "statute_url": "https://www.legislation.gov.uk/",
        "case_url":    "https://www.bailii.org/",
        "search_tips": "legislation.gov.uk for Acts/SIs; BAILII for case law.",
    },
}


SEARCH_QUERY_TEMPLATES: dict[str, list[str]] = {
    "JP": [
        "{statute} {article} 条 {keyword}",
        "{keyword} 裁判例 最高裁",
        "{keyword} 判例 {year}",
        "{keyword} 法的責任 争点",
    ],
    "US-federal": [
        "{statute citation} elements",
        "{keyword} case law {circuit}",
        "{keyword} Restatement of {subject}",
        "{keyword} jury instruction",
    ],
    "US-state": [
        "{state} {statute} {keyword}",
        "{keyword} case law {state}",
        "{keyword} {state} elements",
    ],
    "EU": [
        "Regulation {number}/{year} Article {n}",
        "{keyword} CJEU judgment",
        "{keyword} GDPR Article {n}",
    ],
    "UK": [
        "{Act name} {section} {keyword}",
        "{keyword} case law England Wales",
        "{keyword} {year} EWCA",
    ],
}


# ---- Data classes --------------------------------------------------------

@dataclass
class Statute:
    citation: str          # e.g., "Civil Code Art. 709" or "42 U.S.C. § 1983"
    text: str              # key excerpt
    url: str = ""

@dataclass
class Case:
    citation: str          # e.g., "Smith v. Jones, 123 F.3d 456 (9th Cir. 2020)"
    holding: str           # 1-2 sentence summary
    year: int = 0
    court: str = ""
    url: str = ""

@dataclass
class LegalIssue:
    statement: str         # "Whether X's conduct constitutes Y under Z."
    statutes: list[Statute] = field(default_factory=list)
    cases: list[Case] = field(default_factory=list)
    elements: list[str] = field(default_factory=list)

@dataclass
class Analysis:
    matter_title: str
    jurisdiction: str
    parties: str
    facts: str
    desired_outcome: str
    issues: list[LegalIssue] = field(default_factory=list)
    overall_conclusion: str = ""
    recommended_actions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


# ---- IRAC / CREAC builders ----------------------------------------------

def build_irac(issue: LegalIssue, application: str, conclusion: str) -> str:
    """Build an IRAC block for a single issue."""
    rule_parts: list[str] = []
    for st in issue.statutes:
        rule_parts.append(f"Statute — {st.citation}: \"{st.text}\""
                          + (f" ({st.url})" if st.url else ""))
    for c in issue.cases:
        rule_parts.append(f"Case — {c.citation}: \"{c.holding}\""
                          + (f" ({c.url})" if c.url else ""))
    if issue.elements:
        rule_parts.append("Elements: " + "; ".join(
            f"({i+1}) {e}" for i, e in enumerate(issue.elements)
        ))
    rule = "\n".join(rule_parts)

    return (
        f"ISSUE\n  {issue.statement}\n\n"
        f"RULE\n  {rule}\n\n"
        f"APPLICATION\n  {application}\n\n"
        f"CONCLUSION\n  {conclusion}"
    )


def build_creac(issue: LegalIssue, explanation: str,
                application: str, conclusion: str) -> str:
    """Build a CREAC block (conclusion-first)."""
    rule_parts: list[str] = []
    for st in issue.statutes:
        rule_parts.append(f"Statute — {st.citation}: \"{st.text}\"")
    for c in issue.cases:
        rule_parts.append(f"Case — {c.citation}: \"{c.holding}\"")
    rule = "\n".join(rule_parts)

    return (
        f"CONCLUSION\n  {conclusion}\n\n"
        f"RULE\n  {rule}\n\n"
        f"EXPLANATION\n  {explanation}\n\n"
        f"APPLICATION\n  {application}\n\n"
        f"CONCLUSION\n  {conclusion}"
    )


# ---- Markdown rendering --------------------------------------------------

DISCLAIMER = (
    "> ⚠️ This is informational legal analysis, not formal legal advice. "
    "Statutes and case law change frequently. "
    "Verify with a licensed attorney in the relevant jurisdiction before acting."
)


def format_analysis_md(a: Analysis) -> str:
    lines: list[str] = [
        f"# Legal Analysis — {a.matter_title}",
        "",
        DISCLAIMER,
        "",
        "## Matter Summary",
        f"- Jurisdiction: {a.jurisdiction}",
        f"- Parties: {a.parties}",
        f"- Facts: {a.facts}",
        f"- Desired outcome: {a.desired_outcome}",
        "",
        "## Issues",
    ]
    for i, issue in enumerate(a.issues, 1):
        lines.append(f"{i}. {issue.statement}")
    lines.append("")

    lines.append("## Analysis (IRAC)")
    for i, issue in enumerate(a.issues, 1):
        lines.append("")
        lines.append(f"### Issue {i}")
        lines.append("```")
        lines.append(build_irac(issue,
                                 application="(application to facts)",
                                 conclusion="(likely outcome)"))
        lines.append("```")
    lines.append("")

    lines.append("## Overall Conclusion")
    lines.append(a.overall_conclusion or "(to be drafted)")
    lines.append("")

    if a.recommended_actions:
        lines.append("## Recommended Actions")
        for act in a.recommended_actions:
            lines.append(f"- {act}")
        lines.append("")

    if a.risks:
        lines.append("## Risks")
        for r in a.risks:
            lines.append(f"- {r}")
        lines.append("")

    lines.append("## Authorities Cited")
    if a.issues:
        lines.append("Statutes:")
        for issue in a.issues:
            for st in issue.statutes:
                lines.append(f"- {st.citation}" + (f" — {st.url}" if st.url else ""))
        lines.append("Cases:")
        for issue in a.issues:
            for c in issue.cases:
                lines.append(f"- {c.citation}" + (f" — {c.url}" if c.url else ""))
    return "\n".join(lines)


# ---- Document templates --------------------------------------------------

def format_demand_letter(*,
                         sender_name: str, sender_addr: str,
                         recipient_name: str, recipient_addr: str,
                         date_str: str, re_line: str,
                         facts: str, legal_basis: str,
                         demand: str, deadline: str,
                         closing: str = "Sincerely,") -> str:
    """US-style demand letter template."""
    return f"""{sender_name}
{sender_addr}

{date_str}

{recipient_name}
{recipient_addr}

RE: {re_line}

Dear {recipient_name}:

This letter concerns {re_line}.

FACTUAL BACKGROUND
{facts}

LEGAL BASIS
{legal_basis}

DEMAND
{demand}

You have until {deadline} to comply. If you do not, we will pursue all
available legal remedies without further notice.

{closing}

{sender_name}
"""


def format_legal_opinion(*,
                         title: str, date_str: str,
                         prepared_by: str,
                         facts: str, issues: list[str],
                         analysis: str, conclusion: str,
                         sources: list[str]) -> str:
    """JP-style legal opinion template."""
    lines = [
        f"# {title}",
        "",
        f"日付: {date_str}",
        f"作成者: {prepared_by}",
        "",
        "## 1. 事実関係",
        facts,
        "",
        "## 2. 問題点",
    ]
    for i, iss in enumerate(issues, 1):
        lines.append(f"{i}. {iss}")
    lines += [
        "",
        "## 3. 検討",
        analysis,
        "",
        "## 4. 結論",
        conclusion,
        "",
        "## 5. 出典",
    ]
    for s in sources:
        lines.append(f"- {s}")
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    issue = LegalIssue(
        statement=("Whether Seller's failure to deliver goods by the contract "
                    "date constitutes a breach under the sale-of-goods statute."),
        statutes=[
            Statute(citation="UCC § 2-309",
                    text="Failure to deliver within a reasonable time is a breach.",
                    url="https://www.law.cornell.edu/ucc/2/2-309"),
        ],
        cases=[
            Case(citation="Held v. Mfg Co., 456 F.2d 222 (2d Cir. 1972)",
                  holding="A 30-day delay in delivery is a breach as a matter of law.",
                  year=1972, court="2d Cir.",
                  url="https://scholar.google.com/"),
        ],
        elements=[
            "existence of a valid contract",
            "seller failed to deliver within a reasonable time",
            "buyer suffered damages as a result",
        ],
    )

    a = Analysis(
        matter_title="Breach of Contract — Goods Delivery",
        jurisdiction="US-state",
        parties="Buyer (client) vs Seller",
        facts=("Contract dated 2025-01-15. Delivery due 2025-02-15. "
               "Seller delivered on 2025-03-20."),
        desired_outcome="Recover damages for late delivery.",
        issues=[issue],
        overall_conclusion="Buyer likely prevails on the breach claim.",
        recommended_actions=[
            "Send a demand letter citing UCC § 2-309 by 2025-04-15.",
            "Document all damages (lost sales, storage costs).",
            "Prepare for negotiation; seller may counterclaim.",
        ],
        risks=[
            "Force majeure defense if seller can show external cause.",
            "Mitigation duty: buyer must limit damages where possible.",
        ],
    )

    print(format_analysis_md(a))
    print("\n--- Demand letter excerpt ---")
    print(format_demand_letter(
        sender_name="Alice Chen", sender_addr="123 Main St, NY 10001",
        recipient_name="Bob Mfg Co.", recipient_addr="456 Industrial Way",
        date_str="2025-04-01",
        re_line="Breach of contract — late delivery of goods",
        facts="Contract 2025-01-15, delivery due 2025-02-15, actual 2025-03-20.",
        legal_basis="UCC § 2-309 imposes timely delivery; 30+ day delay is a breach.",
        demand="Pay $25,000 in damages within 30 days.",
        deadline="2025-05-01",
    ))
