---
name: target-company
description: Find target companies for your product, score lead quality, and propose a concrete outreach strategy. Use for B2B sales prospecting — input your product info, get prioritized accounts + tailored outreach.
---

# Target-Company Skill

## Overview
B2B sales prospecting pipeline:
1. Take your product description.
2. Search the web for candidate companies matching the ICP.
3. Score each lead (A/B/C/D) using fit + intent + accessibility signals.
4. Propose a tailored outreach strategy per A/B lead.

## Bundled Helper Module
**`skill/target-company/scripts/target_company.py`** (stdlib only):
- `Product` / `ICP` / `Lead` / `OutreachPlan` dataclasses.
- `ICRITERIA` — fit / intent / accessibility scoring rubric.
- `score_lead(lead, icp)` — returns grade A/B/C/D + breakdown.
- `rank_leads(leads, icp)` — sort by score, group by grade.
- `build_outreach(lead, channel)` — draft skeleton email/LinkedIn message.
- `format_pipeline_md(...)` — full Markdown pipeline report.

```python
import sys; sys.path.insert(0, "skill/target-company/scripts")
from target_company import (Product, ICP, Lead, OutreachPlan,
                            score_lead, rank_leads, build_outreach,
                            format_pipeline_md)
```
Run `python skill/target-company/scripts/target_company.py` for a worked sample.

## Workflow

### Phase 1 — Product & ICP Definition
1. Capture the product: what it does, who it's for, pricing, differentiator.
2. Derive the ICP (Ideal Customer Profile):
   - Industry / sector
   - Company size (employees, revenue)
   - Geography
   - Tech stack signals (e.g., uses Salesforce, has a careers page)
   - Trigger events (funding, hiring, leadership change, product launch)
3. Build a `Product` and `ICP` object.

### Phase 2 — Candidate Search
For each ICP dimension, run websearch:
```
"{industry} companies {size} {geography}"
"site:linkedin.com/company {industry} {size}"
"recently funded {industry} {geography} {year}"
"{industry} hiring {role} {geography}"
```
Target: 20-50 candidates. Capture name, URL, size, industry, recent news.

### Phase 3 — Lead Scoring
For each candidate, fill a `Lead` and call `score_lead(lead, icp)`.
Grading rubric:
- **A** (≥80): strong fit + active intent + accessible contact. Outreach now.
- **B** (60-79): good fit, intent unclear. Nurture.
- **C** (40-59): partial fit. Park.
- **D** (<40): poor fit. Skip.

### Phase 4 — Outreach Strategy
For each A/B lead:
1. Find the right contact (LinkedIn / company "team" page / guess email).
2. Identify a trigger event to anchor the message.
3. Draft a 3-touch sequence (email → LinkedIn → follow-up email).
4. Personalize: reference the trigger, the product's specific value to them.

## Scoring Rubric (`ICRITERIA`)

| Category | Signal | Points |
|---|---|---|
| Fit | Industry match | 0-20 |
| Fit | Company size in ICP range | 0-15 |
| Fit | Geography match | 0-10 |
| Fit | Tech stack signal present | 0-10 |
| Intent | Recent funding round | 0-15 |
| Intent | Hiring for relevant role | 0-10 |
| Intent | Recent product launch / expansion | 0-10 |
| Accessibility | Public contact email / form | 0-5 |
| Accessibility | LinkedIn outreach possible | 0-3 |
| Accessibility | Referral path identified | 0-2 |
| **Max** | | **100** |

## Outreach Templates (3-touch)

### Touch 1 — Email (cold)
```
Subject: {trigger event} — quick idea for {team}

Hi {first},

Saw {trigger: e.g., your Series B announcement}. Congrats.

{Product} helps {role} {verb} {outcome}. {One-line differentiator}.
Worth a 15-min call next week?

— {sender}
```

### Touch 2 — LinkedIn (3 days later)
```
Hi {first} — sent you a note about {trigger} last week.
If email got buried, happy to share the one-pager here.
Either way, thanks for the work you're doing at {company}.
```

### Touch 3 — Follow-up email (5 days later)
```
Subject: re: {original subject}

Hi {first} — circling back. If timing's off, no worries;
happy to reconnect in Q4. If a 10-min call makes sense,
here's my calendar: {link}.
```

## Output Format

```markdown
# Sales Pipeline — {product name}

## Product
- What: ...
- For: ...
- Price: ...
- Differentiator: ...

## ICP
- Industry: ...
- Size: ...
- Geography: ...
- Tech signals: ...
- Triggers: ...

## Candidate Pipeline
| # | Company | Industry | Size | Score | Grade | Trigger |
|---|---|---|---|---|---|---|
| 1 | Acme | SaaS | 200 | 85 | A | Series B |
| 2 | Beta | Fintech | 50 | 72 | B | Hiring |
| ... | | | | | | |

## A-Leads — Outreach This Week

### 1. Acme (score 85)
- Trigger: Series B announced 2025-07-15
- Contact: Jane Doe, VP Eng (LinkedIn)
- Sequence:
  1. Email (template above, personalized with trigger)
  2. LinkedIn (day +3)
  3. Follow-up email (day +8)
- Personalization angle: ...

### 2. ...

## B-Leads — Nurture
- ...

## C-Leads — Park
- ...

## Sources
- {search-result URLs}
```

## Self-Check
- [ ] ICP defined before search (not reverse-engineered)?
- [ ] ≥20 candidates searched?
- [ ] Each lead scored against rubric (not gut feel)?
- [ ] A-leads have a specific trigger event?
- [ ] Outreach messages personalized (not template-only)?
- [ ] Contact identified for each A/B lead?
- [ ] Sources cited?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Scoring on gut feel | Use the rubric; record each signal's points |
| Skipping intent signals | Trigger events double conversion vs cold |
| Generic outreach | Personalize with the specific trigger |
| No contact identified | Find a name before drafting; don't send to "info@" |
| Treating C-leads as A-leads | Don't waste time on poor fits |
| No sources cited | Always include the search URL for each candidate |
