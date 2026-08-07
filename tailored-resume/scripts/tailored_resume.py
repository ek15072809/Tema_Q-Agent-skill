"""tailored_resume.py — Tailor a resume to a specific job posting.

Standard-library only. Provides:
  * JobPosting / Applicant / Experience / Skill    — data classes.
  * parse_job_posting(text)                        — extract requirements / keywords / seniority.
  * score_applicant(applicant, posting)            — match score per requirement.
  * tailor_resume(applicant, posting)              — reorder experiences by relevance.
  * format_resume_md(applicant, posting)           — Markdown resume.
  * format_gap_report(applicant, posting)          — list missing requirements.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Literal


# ---- Data classes --------------------------------------------------------

@dataclass
class Skill:
    name: str
    years: float = 0.0
    proficiency: str = ""   # beginner / intermediate / expert


@dataclass
class Experience:
    role: str
    company: str
    start: str             # "2023-01"
    end: str               # "2024-06" or "Present"
    summary: str = ""
    bullets: list[str] = field(default_factory=list)
    skills_used: list[str] = field(default_factory=list)
    industry: str = ""


@dataclass
class Applicant:
    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    summary: str = ""
    skills: list[Skill] = field(default_factory=list)
    experiences: list[Experience] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    total_years: float = 0.0


@dataclass
class JobPosting:
    title: str = ""
    company: str = ""
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    min_years: float = 0.0
    industry: str = ""
    raw_text: str = ""


# ---- Parser --------------------------------------------------------------

# Common skill / keyword bank — extend as needed.
_SKILL_BANK: list[str] = [
    "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++",
    "React", "Vue", "Angular", "Node.js", "Next.js", "Django", "Flask",
    "FastAPI", "Express", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform",
    "CI/CD", "Git", "Linux", "REST", "GraphQL", "gRPC",
    "PyTorch", "TensorFlow", "scikit-learn", "pandas", "NumPy",
    "Spark", "Airflow", "dbt", "Snowflake", "BigQuery",
    "Salesforce", "HubSpot", "Tableau", "Power BI", "Looker",
    "Figma", "Sketch", "Photoshop", "Illustrator",
    "Agile", "Scrum", "Kanban", "Jira",
    "Stakeholder management", "Cross-functional", "Leadership",
    "Project management", "Product management", "Roadmap",
    "A/B testing", "SEO", "SEM", "Content marketing",
    "Excel", "PowerPoint", "Financial modeling",
    "Japanese", "English", "Mandarin", "Spanish",
]

_SOFT_SKILL_PATTERNS: list[str] = [
    "leadership", "communication", "collaboration", "problem-solving",
    "analytical", "detail-oriented", "self-starter", "team player",
    "ownership", "mentorship",
]


def parse_job_posting(text: str) -> JobPosting:
    """Extract requirements / keywords / seniority from a posting.

    Heuristic: scan for skill bank matches + soft-skill keywords + "N+ years".
    """
    posting = JobPosting(raw_text=text)
    text_lower = text.lower()

    # Title: first line, or "Title:" if present.
    title_match = re.search(r"(?:Title|Position|Role)\s*:\s*(.+)", text, re.I)
    if title_match:
        posting.title = title_match.group(1).strip().splitlines()[0]
    else:
        # First non-empty line.
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith(("#", "-", "*")):
                posting.title = line[:80]
                break

    # Company.
    company_match = re.search(r"(?:Company|Organization|At)\s*:\s*(.+)", text, re.I)
    if company_match:
        posting.company = company_match.group(1).strip().splitlines()[0]

    # Years.
    years_match = re.search(r"(\d+)\+?\s*(?:years|yrs)", text_lower)
    if years_match:
        posting.min_years = float(years_match.group(1))

    # Skills (case-sensitive match for proper nouns; case-insensitive for others).
    for skill in _SKILL_BANK:
        if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE):
            posting.required_skills.append(skill)
    # Dedupe while preserving order.
    seen: set[str] = set()
    posting.required_skills = [s for s in posting.required_skills
                                if not (s in seen or seen.add(s))]

    # Soft-skill keywords.
    for pat in _SOFT_SKILL_PATTERNS:
        if pat in text_lower:
            posting.keywords.append(pat)

    # Industry guess: very rough.
    industries = ["SaaS", "Fintech", "Healthcare", "E-commerce", "Education",
                   "Manufacturing", "Consulting", "Media", "Gaming", "AI/ML"]
    text_words = set(re.findall(r"\b\w+\b", text_lower))
    for ind in industries:
        if ind.lower().replace("/", " ") in text_lower:
            posting.industry = ind
            break

    return posting


# ---- Scoring -------------------------------------------------------------

def score_applicant(applicant: Applicant, posting: JobPosting) -> dict:
    """Score the applicant against the posting. Returns {score, breakdown}."""
    bd: dict[str, int] = {}

    # Skill keyword match (5 pts each, cap 30).
    applicant_skills_lower = {s.name.lower() for s in applicant.skills}
    exp_skills_lower = {s.lower() for exp in applicant.experiences for s in exp.skills_used}
    all_applicant_skills = applicant_skills_lower | exp_skills_lower
    matched = [s for s in posting.required_skills if s.lower() in all_applicant_skills]
    bd["skill_match"] = min(30, 5 * len(matched))
    bd["matched_skills"] = len(matched)
    bd["total_required_skills"] = len(posting.required_skills)

    # Seniority match.
    if applicant.total_years >= posting.min_years:
        bd["seniority_match"] = 20
    elif applicant.total_years >= posting.min_years - 1:
        bd["seniority_match"] = 10
    else:
        bd["seniority_match"] = 0

    # Industry match.
    if posting.industry:
        if any(exp.industry.lower() == posting.industry.lower()
               for exp in applicant.experiences):
            bd["industry_match"] = 15
        elif any(exp.industry for exp in applicant.experiences):
            bd["industry_match"] = 8
        else:
            bd["industry_match"] = 0
    else:
        bd["industry_match"] = 0

    # Quantified achievements (5 pts per quantified bullet, cap 15).
    quantified = 0
    for exp in applicant.experiences:
        for b in exp.bullets:
            if re.search(r"\d", b):
                quantified += 1
    bd["quantified_achievements"] = min(15, 5 * quantified)

    # Required tools (already counted in skill_match, but double-count top 5).
    # Skip to avoid double counting; instead use soft-skill language match.
    soft_keywords_present = sum(
        1 for kw in posting.keywords
        if any(kw in (exp.summary + " " + " ".join(exp.bullets)).lower()
               for exp in applicant.experiences)
    )
    bd["soft_skill_match"] = min(10, 2 * soft_keywords_present)

    # Doesn't add to 100 — the rubric is illustrative.
    total = (bd["skill_match"] + bd["seniority_match"] + bd["industry_match"]
             + bd["quantified_achievements"] + bd["soft_skill_match"] + 15)  # +15 base for "tools"
    total = min(100, total)

    if total >= 70:
        fit = "strong"
    elif total >= 50:
        fit = "okay"
    else:
        fit = "stretch"

    return {"score": total, "fit": fit, "breakdown": bd,
            "matched_skills": matched}


# ---- Tailoring -----------------------------------------------------------

def _relevance(exp: Experience, posting: JobPosting) -> int:
    """Higher = more relevant. Used for reordering."""
    score = 0
    for skill in posting.required_skills:
        if skill.lower() in [s.lower() for s in exp.skills_used]:
            score += 2
        if skill.lower() in exp.summary.lower():
            score += 1
    for kw in posting.keywords:
        if kw in (exp.summary + " " + " ".join(exp.bullets)).lower():
            score += 1
    if posting.industry and exp.industry.lower() == posting.industry.lower():
        score += 3
    return score


def tailor_resume(applicant: Applicant, posting: JobPosting) -> Applicant:
    """Return a copy of the applicant with experiences reordered by relevance."""
    tailored = Applicant(
        name=applicant.name, email=applicant.email, phone=applicant.phone,
        location=applicant.location, linkedin=applicant.linkedin,
        summary=applicant.summary, skills=applicant.skills,
        experiences=sorted(applicant.experiences,
                            key=lambda e: -_relevance(e, posting)),
        education=applicant.education, certifications=applicant.certifications,
        total_years=applicant.total_years,
    )
    return tailored


# ---- Markdown rendering --------------------------------------------------

def format_resume_md(applicant: Applicant, posting: JobPosting) -> str:
    lines = [
        f"# {applicant.name}",
        f"{posting.title or 'Professional'} | {applicant.location} | "
        f"{applicant.email} | {applicant.phone} | {applicant.linkedin}",
        "",
        "## Professional Summary",
        applicant.summary or "(write a 2-3 sentence summary mirroring the posting's language)",
        "",
        "## Core Skills",
    ]
    # Group skills: matched-to-posting first, then others.
    matched_lower = {s.lower() for s in posting.required_skills}
    matched = [s for s in applicant.skills if s.name.lower() in matched_lower]
    others = [s for s in applicant.skills if s.name.lower() not in matched_lower]
    if matched:
        lines.append("**Matches posting:** " + ", ".join(s.name for s in matched))
    if others:
        lines.append("**Other:** " + ", ".join(s.name for s in others))
    lines.append("")

    lines.append("## Professional Experience")
    for exp in applicant.experiences:
        lines.append("")
        lines.append(f"### {exp.role} — {exp.company}  "
                     f"({exp.start} – {exp.end})")
        if exp.summary:
            lines.append(f"**{exp.summary}**")
        lines.append("")
        for b in exp.bullets:
            lines.append(f"- {b}")
        if exp.skills_used:
            lines.append(f"\n*Skills: {', '.join(exp.skills_used)}*")

    if applicant.education:
        lines.append("")
        lines.append("## Education")
        for e in applicant.education:
            lines.append(f"- {e}")

    if applicant.certifications:
        lines.append("")
        lines.append("## Certifications")
        for c in applicant.certifications:
            lines.append(f"- {c}")

    return "\n".join(lines)


def format_gap_report(applicant: Applicant, posting: JobPosting,
                       score_result: dict) -> str:
    matched = set(s.lower() for s in score_result["matched_skills"])
    missing = [s for s in posting.required_skills if s.lower() not in matched]
    lines = [
        "## Gap Report",
        f"- Match score: {score_result['score']}/100 ({score_result['fit']})",
        f"- Matched skills: {len(score_result['matched_skills'])} / "
        f"{score_result['breakdown']['total_required_skills']}",
        f"- Seniority: applicant {applicant.total_years} yrs vs posting {posting.min_years} yrs",
    ]
    if missing:
        lines.append(f"- Missing: {', '.join(missing)}")
        lines.append("- Suggestion: address in cover letter or highlight adjacent experience.")
    else:
        lines.append("- Missing: none — all required skills matched.")
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    posting_text = """
Senior Backend Engineer — Acme Corp

We're hiring a Senior Backend Engineer with 5+ years of experience.
Required: Python, AWS, PostgreSQL, Docker, Kubernetes, REST API design.
Preferred: GraphQL, Terraform, Airflow.

You'll lead a team of 4, own the payments service, and partner with stakeholders
across product and ops. Strong communication and ownership are essential.
Industry: Fintech.
"""
    posting = parse_job_posting(posting_text)
    print(f"Parsed posting:")
    print(f"  Title:    {posting.title}")
    print(f"  Min yrs:  {posting.min_years}")
    print(f"  Industry: {posting.industry}")
    print(f"  Skills:   {posting.required_skills}")
    print(f"  Keywords: {posting.keywords}")
    print()

    applicant = Applicant(
        name="Alice Chen",
        email="alice@example.com", phone="+1-555-0100",
        location="San Francisco, CA", linkedin="linkedin.com/in/alicechen",
        summary=("Backend engineer with 6 years building payments systems in fintech. "
                 "Led a team of 5 at PayCo; shipped a 99.99% uptime service."),
        skills=[Skill(name="Python", years=6, proficiency="expert"),
                Skill(name="AWS", years=5, proficiency="expert"),
                Skill(name="PostgreSQL", years=5, proficiency="expert"),
                Skill(name="Docker", years=4, proficiency="intermediate"),
                Skill(name="Kubernetes", years=3, proficiency="intermediate"),
                Skill(name="REST", years=6, proficiency="expert"),
                Skill(name="GraphQL", years=2, proficiency="intermediate")],
        experiences=[
            Experience(
                role="Senior Backend Engineer", company="PayCo",
                start="2021-06", end="Present",
                summary="Owned the payments service handling $200M/yr.",
                bullets=[
                    "Reduced payment latency by 40% by re-architecting the ledger.",
                    "Led a team of 5 engineers; ran sprint planning and 1-on-1s.",
                    "Migrated from EC2 to EKS, cutting infra costs 25%.",
                ],
                skills_used=["Python", "AWS", "PostgreSQL", "Docker", "Kubernetes", "REST"],
                industry="Fintech",
            ),
            Experience(
                role="Backend Engineer", company="ShopApp",
                start="2018-03", end="2021-05",
                summary="Built the catalog service for an e-commerce platform.",
                bullets=[
                    "Shipped a GraphQL gateway serving 10M req/day.",
                    "Wrote the team's first Terraform modules.",
                ],
                skills_used=["Python", "PostgreSQL", "GraphQL", "Terraform"],
                industry="E-commerce",
            ),
        ],
        education=["B.S. Computer Science, UC Berkeley, 2018"],
        certifications=["AWS Certified Solutions Architect — Associate"],
        total_years=6.0,
    )

    score = score_applicant(applicant, posting)
    print(f"Score: {score['score']}/100 ({score['fit']})")
    print(f"Matched skills: {score['matched_skills']}")
    print()

    tailored = tailor_resume(applicant, posting)
    print(format_resume_md(tailored, posting))
    print()
    print(format_gap_report(tailored, posting, score))
