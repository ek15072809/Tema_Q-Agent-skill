---
name: mail
description: Draft emails and letters in Japanese or American business / personal style. Choose tone, format (subject + greeting + body + closing), and conventions appropriate to the recipient's country. Use for any email or letter composition task.
---

# Mail Skill

## Overview
Compose emails and letters in **JP** or **US** style.
- Business email / Personal email / Formal letter / Cover letter / Thank-you note / Apology.
- Detect language: Hiragana/Katakana → JP, else US (unless user overrides).
- Output as plain text (copy-paste ready). No file generation needed.

## Workflow
1. **Clarify**: country (JP/US), channel (email/letter), relationship (boss/colleague/client/friend), purpose, key points.
2. **Pick template** below.
3. **Draft** using the structural rules.
4. **Self-check** against the checklist.
5. Output as a single code block.

## JP Business Email

### Structure (mandatory order)
```
件名：[分類] 具体的内容 — 自社名/氏名

宛先氏名 様

（自社名）
（自部署名）
（氏名）は申します。

本文（結びつけの挨拶 → 本題 → 要件 → 結び）

─────────────────
氏名
会社名
部署名
電話 / Email
```

### Opening greetings (季節の挨拶)
- 春（3-5月）: 「桜花の候」「春暖の候」
- 夏（6-8月）: 「盛夏の候」「猛暑の候」
- 秋（9-11月）: 「秋涼の候」「錦秋の候」
- 冬（12-2月）: 「厳寒の候」「新春の候」
Generic: 「貴社におかれましては益々ご清栄のこととお慶び申し上げます」

### Closings
- 「何卒よろしくお願い申し上げます。」
- 「まずは略儀ながら書中をもちましてご挨拶申し上げます。」

### Subject-line conventions
- `[分類]` prefix: `[ご返信]` `[お知らせ]` `[ご提案]` `[お詫び]` `[依頼]`
- Keep ≤30 chars; specific over generic.

## JP Personal Email

### Structure
```
件名：用件を一行で

宛先氏名 さん

挨拶 → 本題 → 近況 → 結び

─────────────────
氏名
```
- Opening: 「お久しぶりです」「こんにちは」「お疲れ様です」
- Closing: 「それではまた」「ご無沙汰しております」

## JP Formal Letter (手紙)

### Structure
```
前略 / 拝啓

宛先氏名 様

頭語の挨拶（季節）
本文
結びの言葉（敬具 / かしこ）

─────────────────
差出人氏名
```
- 頭語: 拝啓 / 前略 / 謹啓 / 拝復
- 結語: 敬具 / 早々 / かしこ（女性用）
- 一筆啓上: 「一筆啓上いたします」for short notes

## US Business Email

### Structure
```
Subject: [Action verb] [Specific topic] — [Optional tag]

Hi [First name], / Dear Mr./Ms. [Last name],

[Opening — context or warmth]
[Body — clear paragraphs, one idea each]
[Call to action / next step]

Best regards,
[First name] [Last name]
[Title]
[Company]
```

### Subject-line conventions
- Start with a verb: "Request for", "Update on", "Action required", "Invitation to"
- Be specific: "Q3 budget review — Action needed by Fri"
- Tags: `[Action]`, `[FYI]`, `[Urgent]`, `[Update]`

### Salutations
- First contact, formal: `Dear Mr./Ms. [Last name],`
- Established: `Hi [First name],`
- Group: `Hi team,` / `Dear all,`
- Avoid gendered honorifics if unsure (use full name).

### Closings
- Formal: `Sincerely,` / `Respectfully,`
- Business standard: `Best regards,` / `Best,`
- Casual: `Thanks,` / `Cheers,`

## US Formal Letter

### Structure (block format)
```
[Your Name]
[Your Address]
[City, State ZIP]
[Email / Phone]

[Date]

[Recipient Name]
[Recipient Title]
[Company]
[Address]

Dear [Mr./Ms./Dr.] [Last name]:

[Opening paragraph — purpose]
[Body paragraphs — supporting details]
[Closing paragraph — call to action]

Sincerely,

[Signature]

[Your Name]
```

## Tone Quick Reference

| Situation | JP | US |
|---|---|---|
| Apology | 深くお詫び申し上げます | I sincerely apologize |
| Request | お願いできれば幸いです | I would appreciate it if |
| Thanks | 誠にありがとうございます | Thank you very much |
| Refusal | お断りせざるを得ません | Unfortunately, I'm unable to |
| Follow-up | 念のため再度ご連絡いたします | Just following up on |

## Reply (返信) Workflow
1. Quote essential context in 1 line (US) or 「お世話になっております」+ context (JP).
2. Answer every question in order — number them if 2+.
3. Explicitly mark unanswered items ("regarding X, I will check and reply by Y").
4. End with clear next step + timeline.

## Self-Check
- [ ] Country style matches recipient (JP keigo / US directness).
- [ ] Subject is specific and ≤30 chars (JP) / starts with verb (US).
- [ ] Salutation matches relationship.
- [ ] Closing matches formality.
- [ ] Body answers every question / states every required point.
- [ ] No machine-translation smell (avoid "I am writing to inform you that" repeated).
- [ ] Signature block complete.

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| JP keigo level wrong | Match client (sonkeigo for client, kenjougo for self) |
| US subject too vague | Use action verb + specific topic |
| Mixed JP/US styles | Pick one style per email |
| No clear call to action | End with explicit next step + deadline |
| Forgetting signature | Always include contact block |
| Reply missing items | Number the questions and answer in order |
