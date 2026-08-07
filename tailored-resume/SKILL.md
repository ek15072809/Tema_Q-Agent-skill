---
name: tailored-resume
description: Parse a job posting, extract required skills / keywords, then highlight the most relevant experience from the applicant's history to produce a tailored resume. Use for any job application where the resume should match the posting.
---

# Tailored-Resume Skill

## Overview
Generate a resume tailored to a specific job posting.
1. Parse the posting → extract required skills, keywords, seniority signals.
2. Score the applicant's history against each requirement.
3. Reorder / emphasize the most relevant experience.
4. Output as Markdown (then convert to PDF/DOCX if requested).

## Bundled Helper Module
**`skill/tailored-resume/scripts/tailored_resume.py`** (stdlib only):
- `JobPosting` / `Applicant` / `Experience` / `Skill` dataclasses.
- `parse_job_posting(text)` — extract requirements, keywords, seniority.
- `score_applicant(applicant, posting)` — match score per requirement.
- `tailor_resume(applicant, posting)` — reorder experiences by relevance.
- `format_resume_md(applicant, posting)` — Markdown resume.
- `format_gap_report(applicant, posting)` — list missing requirements.

```python
import sys; sys.path.insert(0, "skill/tailored-resume/scripts")
from tailored_resume import (JobPosting, Applicant, Experience, Skill,
                              parse_job_posting, score_applicant,
                              tailor_resume, format_resume_md, format_gap_report)
```
Run `python skill/tailored-resume/scripts/tailored_resume.py` for a worked sample.

## Workflow

1. **Inputs** — job posting text + applicant's full history (Markdown / plain text).
2. **Parse posting** via `parse_job_posting()` → requirements + keywords + seniority.
3. **Score** via `score_applicant()` — match each requirement to experience.
4. **Tailor** via `tailor_resume()` — reorder, emphasize, optionally omit low-relevance roles.
5. **Gap report** via `format_gap_report()` — show missing requirements honestly.
6. **Output** — `format_resume_md()`. Offer PDF/DOCX conversion via the `pdf` or `docx` skill.

## Resume Structure (output)

```markdown
# {Name}
{role title} | {location} | {email} | {phone} | {linkedin}

## Professional Summary
{2-3 sentences that mirror the posting's language; lead with the most
relevant qualification; quantify impact.}

## Core Skills
{Group by category; list posting keywords first.}

## Professional Experience

### {Role} — {Company}                       {Month Year} – {Present/Month Year}
**{one-line summary that maps to the posting's requirements}**

- {achievement with metric, using posting keywords}
- {achievement with metric}
- {achievement with metric}

### {Previous Role} — {Company}              {dates}
...

## Education
{degree}, {school}, {year}

## Certifications
{cert list — only those relevant to the posting}
```

## Tailoring Rules

1. **Keyword density** — every required keyword should appear ≥1 time.
2. **Lead with relevance** — the role that best matches the posting goes first
   within each section (not strictly chronological if it hurts relevance).
3. **Quantify** — every bullet should have a number (% , $, time, count).
4. **Omit low-relevance** — if a role adds nothing to the posting, drop it
   (a 1-page resume beats a 2-page one).
5. **Mirror language** — if the posting says "stakeholder management",
   use that exact phrase, not "cross-functional coordination".
6. **Seniority match** — if posting asks for 5+ years and applicant has 3,
   lead with the most impressive impact to compensate.

## Scoring Rubric

| Signal | Points | Notes |
|---|---|---|
| Skill keyword match | 0-30 | 5 pts per exact match (cap 30) |
| Seniority match | 0-20 | 20 if ≥ posting's years, 10 if ±1 year, 0 if <2 yrs short |
| Industry match | 0-15 | 15 if same industry, 8 if adjacent |
| Quantified achievement | 0-15 | 5 pts per quantified bullet (cap 15) |
| Required tool experience | 0-10 | 2 pts per tool (cap 10) |
| Soft-skill language match | 0-10 | mirrors posting's phrasing |
| **Max** | **100** | ≥70 = strong fit, 50-69 = okay, <50 = stretch |

## Output Format

```markdown
# Tailored Resume — {Name} for {Company} {Role}

## Match Score: {N}/100 ({strong / okay / stretch})

## Resume
{full Markdown resume per structure above}

## Gap Report
- Missing: {requirement not in applicant's history}
- Weak: {requirement partially met}
- Suggestion: {how to address in cover letter or interview}
```

## Self-Check
- [ ] Posting parsed for all required skills + keywords?
- [ ] Every required keyword appears in the resume ≥1 time?
- [ ] Lead role is the most relevant (not just most recent)?
- [ ] Every bullet has a number?
- [ ] Resume ≤ 1 page (or 2 if senior)?
- [ ] Gap report included (don't hide weaknesses)?
- [ ] Language mirrors the posting?
- [ ] No typos in company / role names?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Generic resume (not tailored) | Re-run tailor_resume(); check keyword density |
| Chronological order only | Reorder by relevance within sections |
| No metrics | Add % / $ / time / count to every bullet |
| Hiding gaps | Include gap report — honesty beats hiding |
| Keyword stuffing | Use keywords in context, not as a list |
| Wrong company name | Verify spelling from the posting |
| Too long | Cut to 1 page; omit low-relevance roles |
