"""mail_skill.py — Helpers for composing JP / US emails and letters.

This module is intentionally dependency-free (standard library only).
It provides:
  * TONE_JP / TONE_US          — quick-lookup phrase tables.
  * build_jp_email(subject, recipient, body, sender) — returns a JP email string.
  * build_us_email(subject, recipient, body, sender) — returns a US email string.
  * JP_SEASONAL_GREETINGS      — date-aware seasonal opening (JP letters).
  * jp_seasonal_greeting(date) — pick the right phrase for a given date.
"""
from __future__ import annotations
from datetime import date
from typing import Literal


# ---- Tone phrase tables --------------------------------------------------

TONE_JP: dict[str, str] = {
    "apology":    "深くお詫び申し上げます。",
    "request":    "お願いできれば幸いです。",
    "thanks":     "誠にありがとうございます。",
    "refusal":    "お断りせざるを得ません。",
    "follow_up":  "念のため再度ご連絡いたします。",
    "introduce":  "自己紹介させていただきます。",
    "offer":      "ご提案させていただきます。",
    "confirm":    "ご確認のほどよろしくお願い申し上げます。",
}

TONE_US: dict[str, str] = {
    "apology":    "I sincerely apologize for any inconvenience.",
    "request":    "I would appreciate it if you could ...",
    "thanks":     "Thank you very much for ...",
    "refusal":    "Unfortunately, I'm unable to ...",
    "follow_up":  "Just following up on ...",
    "introduce":  "I wanted to introduce myself — ...",
    "offer":      "I'd like to propose ...",
    "confirm":    "Please let me know if this works for you.",
}


# ---- Seasonal greetings (JP formal letters / business emails) -----------
# Date ranges are approximate; the function picks the first match.

JP_SEASONAL_GREETINGS: list[tuple[tuple[int, int], tuple[int, int], str]] = [
    # (start_month, start_day), (end_month, end_day), phrase
    ((3,  1), (4, 20), "桜花の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((4, 21), (5, 31), "春暖の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((6,  1), (7, 20), "向夏の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((7, 21), (8, 31), "盛夏の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((9,  1), (9, 30), "初秋の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((10, 1), (10, 31), "秋涼の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((11, 1), (11, 30), "晩秋の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((12, 1), (12, 31), "師走の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((1,  1), (1, 15), "新春の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
    ((1, 16), (2, 28), "厳寒の候、貴社におかれましては益々ご清栄のこととお慶び申し上げます。"),
]


def jp_seasonal_greeting(d: date | None = None) -> str:
    """Return the seasonal greeting appropriate for *d* (today if None)."""
    d = d or date.today()
    for (sm, sd), (em, ed), phrase in JP_SEASONAL_GREETINGS:
        start = date(d.year, sm, sd)
        end = date(d.year, em, ed)
        # Handle year-wrap for early-January phrases.
        if start <= end:
            if start <= d <= end:
                return phrase
        else:
            # ranges that wrap (none here, but defensive)
            if d >= start or d <= end:
                return phrase
    # Fallback (should never be reached because of the year-wrap fallback).
    return ("貴社におかれましては益々ご清栄のこととお慶び申し上げます。")


# ---- Builders ------------------------------------------------------------

Country = Literal["JP", "US"]


def build_jp_email(*,
                   subject: str,
                   recipient: str,
                   body: str,
                   sender_name: str,
                   sender_company: str = "",
                   sender_dept: str = "",
                   sender_contact: str = "",
                   seasonal: bool = True) -> str:
    """Compose a JP business email as plain text."""
    today = date.today()
    greeting = jp_seasonal_greeting(today) if seasonal else ""
    # Strip a trailing 様 from recipient if present, then add it once.
    recip_clean = recipient.rstrip()
    if recip_clean.endswith("様"):
        recip_clean = recip_clean[:-1].rstrip()
    lines = [f"件名：{subject}", "", f"{recip_clean} 様", ""]
    if sender_company or sender_dept:
        lines.append(f"{sender_company}")
        lines.append(f"{sender_dept}")
    lines.append(f"{sender_name}は申します。")
    lines.append("")
    if greeting:
        lines.append(greeting)
        lines.append("")
    lines.append(body.strip())
    lines.append("")
    lines.append("何卒よろしくお願い申し上げます。")
    lines.append("")
    lines.append("─────────────────")
    lines.append(sender_name)
    if sender_company:
        lines.append(sender_company)
    if sender_dept:
        lines.append(sender_dept)
    if sender_contact:
        lines.append(sender_contact)
    return "\n".join(lines)


def build_us_email(*,
                   subject: str,
                   recipient_name: str,
                   body: str,
                   sender_first: str,
                   sender_last: str,
                   sender_title: str = "",
                   sender_company: str = "",
                   formality: str = "standard") -> str:
    """Compose a US business email as plain text.

    formality: 'formal' (Dear Mr./Ms.), 'standard' (Hi First), 'casual' (Hi).
    """
    if formality == "formal":
        salutation = f"Dear {recipient_name},"
    elif formality == "casual":
        salutation = "Hi,"
    else:
        salutation = f"Hi {recipient_name},"

    closing = "Best regards," if formality != "formal" else "Sincerely,"

    lines = [f"Subject: {subject}", "", salutation, "", body.strip(), "",
             closing, "", f"{sender_first} {sender_last}"]
    if sender_title:
        lines.append(sender_title)
    if sender_company:
        lines.append(sender_company)
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    print("=== JP seasonal greeting (today) ===")
    print(jp_seasonal_greeting())
    print()

    print("=== JP email ===")
    jp = build_jp_email(
        subject="[ご返信] 〇〇案件のお打ち合わせについて",
        recipient="株式会社〇〇 営業部 山田 太郎 様",
        body=("\n"
              "お世話になっております。\n"
              "ご提案いただいたスケジュールで承知いたしました。\n"
              "当日は資料を3部持参いたします。\n"),
        sender_name="佐藤 花子",
        sender_company="株式会社〇〇",
        sender_dept="マーケティング部",
        sender_contact="03-1234-5678 / hanako@example.com",
    )
    print(jp)
    print()

    print("=== US email ===")
    us = build_us_email(
        subject="Action requested: Q3 budget review by Fri",
        recipient_name="John",
        body=("\n"
              "Thanks for the draft you sent on Monday.\n\n"
              "Could you confirm the following before Friday:\n"
              "  1. Total headcount for Q3\n"
              "  2. Marketing allocation breakdown\n"
              "  3. Final approval from finance\n\n"
              "Happy to jump on a quick call if easier."),
        sender_first="Alice",
        sender_last="Chen",
        sender_title="VP, Operations",
        sender_company="Acme Inc.",
        formality="standard",
    )
    print(us)
