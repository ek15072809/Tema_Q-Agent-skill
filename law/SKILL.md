---
name: law
description: Provide lawyer-level legal analysis and argument drafting by jurisdiction (JP / US / EU). Search the web for the current statute and case law. Use for legal-issue triage, drafting letters, summarizing exposure, proposing strategy. Always state this is not formal legal advice.
---

# Law Skill

## Overview
Triage legal situations and draft legal-style analysis by jurisdiction.
- Pick the correct country / state / circuit.
- Cite the actual statute + leading case law (always websearch-verified).
- Output: issue → rule → application → conclusion (IRAC / CREAC).
- ⚠️ Always include the disclaimer: information only, not formal legal advice.

## Bundled Helper Module
**`skill/law/scripts/law_skill.py`** provides (standard library only):
- `JURISDICTIONS` — JP / US-federal / US-state / EU-Regulation source URLs.
- `SEARCH_QUERY_TEMPLATES` — query patterns per jurisdiction.
- `Case` / `Statute` / `LegalIssue` / `Analysis` dataclasses.
- `build_irac(issue, rules, application, conclusion)` — IRAC structure.
- `build_creac(...)` — CREAC (conclusion-first) variant.
- `format_analysis_md(analysis)` — render as Markdown.
- `format_demand_letter(...)` / `format_legal_opinion(...)` — document templates.

```python
import sys; sys.path.insert(0, "skill/law/scripts")
from law_skill import (JURISDICTIONS, SEARCH_QUERY_TEMPLATES,
                       Case, Statute, LegalIssue, Analysis,
                       build_irac, build_creac, format_analysis_md)
```
Run `python skill/law/scripts/law_skill.py` to print a sample IRAC analysis.

## Workflow

1. **Clarify the facts**: jurisdiction, parties, dates, key events, desired outcome.
2. **Identify issues**: 1-3 concrete legal questions.
3. **Search**: websearch the statute + leading cases for each issue.
4. **Cite**: capture full citation (statute §, case name, year, court).
5. **Analyze**: apply rules to facts using IRAC / CREAC.
6. **Conclude**: state likely outcome + recommended action + risks.
7. **Disclaim**: include the disclaimer block at the top.

## Jurisdictions & Primary Sources

| Jurisdiction | Statute source | Case law source |
|---|---|---|
| Japan (JP) | e-Gov 法令検索 https://laws.e-gov.go.jp/ | 裁判所裁判例情報 https://www.courts.go.jp/ |
| US Federal | Cornell LII https://www.law.cornell.edu/uscode | Cornell LII / SCOTUS https://www.supremecourt.gov/ |
| US State | State legislature site | Google Scholar case law |
| EU Regulation | EUR-Lex https://eur-lex.europa.eu/ | EUR-Lex / InfoCuria |
| UK | legislation.gov.uk https://www.legislation.gov.uk/ | BAILII https://www.bailii.org/ |

## Search Query Templates

### JP
```
"民法 {article} 条 {keyword}"
"{keyword} 裁判例 最高裁"
"{keyword} 判例 {year}"
"{keyword} 法的責任 争点"
```

### US
```
"{statute citation} elements"
"{keyword} case law {state or circuit}"
"{keyword} Restatement of {subject}"
"{keyword} jury instruction {state}"
```

### EU
```
"Regulation {number}/{year} Article {n}"
"{keyword} CJEU judgment"
"{keyword} GDPR Article {n}"
```

## IRAC Structure (default)

```
ISSUE
  Whether {party}'s {conduct} constitutes {claim} under {statute}.

RULE
  {Statute citation}: "{key text}".
  {Leading case citation}: "{holding}".
  {Elements required}: (1) ..., (2) ..., (3) ...

APPLICATION
  Here, {party} did {fact}. This satisfies element (1) because {reason}.
  Element (2) is satisfied because {reason}.
  Element (3) is disputed because {counter-argument}.

CONCLUSION
  {Party} will likely {prevail / fail} on this claim.
  Recommended action: {step}. Risk: {risk}.
```

## CREAC Structure (conclusion-first, common in US memos)

```
CONCLUSION
  {Party} likely {prevails / fails}.

RULE
  {Statute + case law}

EXPLANATION
  {How the rule has been applied in leading cases}

APPLICATION
  {Apply to client's facts}

CONCLUSION
  {Restate + recommend action}
```

## Output Format

```markdown
# Legal Analysis — {Matter title}

> ⚠️ This is informational analysis, not formal legal advice.
> Statutes and case law change; verify with a licensed attorney in the
> relevant jurisdiction before acting.

## Matter Summary
- Jurisdiction: {JP / US-CA / EU / ...}
- Parties: {A vs B}
- Key dates: {events timeline}
- Desired outcome: {client's goal}

## Issue(s)
1. {Issue statement 1}
2. {Issue statement 2}

## Analysis (IRAC)

### Issue 1
ISSUE: ...
RULE: ...
APPLICATION: ...
CONCLUSION: ...

### Issue 2
...

## Overall Recommendation
- Likely outcome: {prevail / partial / fail}
- Recommended action: {step-by-step}
- Risks: {list}
- Alternative approaches: {list}

## Authorities Cited
- Statutes:
  - {citation + URL}
- Cases:
  - {citation + URL + year + court}
- Secondary:
  - {Restatement / treatise / article + URL}
```

## Document Templates

### Demand letter (US) — see `format_demand_letter()` in script
- Sender/recipient block, date, RE: line.
- Factual background → legal basis → demand → deadline → signature.

### Legal opinion (JP) — see `format_legal_opinion()` in script
- 表題 → 事実関係 → 問題点 → 検討 → 結論 → 出典.

## Self-Check
- [ ] Jurisdiction confirmed?
- [ ] Statute cited with current § number + URL?
- [ ] At least one leading case cited with full citation?
- [ ] IRAC / CREAC structure followed?
- [ ] Application ties each element to a specific fact?
- [ ] Counter-arguments addressed?
- [ ] Disclaimer included?
- [ ] Recommended action concrete (next step + timeline)?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Outdated statute | Always websearch; check most recent amendment |
| Wrong jurisdiction | Confirm country/state before citing |
| Generic case citation | Use full: "Smith v. Jones, 123 F.3d 456 (9th Cir. 2020)" |
| Skipping elements | Apply each element separately |
| No counter-argument | Always address the other side's strongest point |
| Sounding like final advice | Add disclaimer at the top, not the bottom |
| Missing URL | Always include source URL for each authority |

## Disclaimer (always include at top of output)
> This is informational legal analysis, not formal legal advice.
> Statutes and case law change frequently. Verify with a licensed attorney
> in the relevant jurisdiction before taking any action.
