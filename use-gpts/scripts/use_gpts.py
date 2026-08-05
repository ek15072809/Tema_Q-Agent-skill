"""use_gpts.py — Helpers for delegating sub-tasks to external LLM web apps.

Standard-library only (no extra pip deps). Provides:
  * TARGETS                 — supported external LLM sites + best-effort selectors.
  * build_prompt(...)       — wrap a task into a structured prompt for external LLMs.
  * sanitize(text)          — strip obvious secrets / PII before pasting.
  * delegation_plan(task)   — return a structured plan dict.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Literal


# ---- Supported targets (selectors are best-effort; sites change often) ---

TARGETS: dict[str, dict] = {
    "chatgpt": {
        "url": "https://chatgpt.com/",
        "input_selector": "textarea#prompt-textarea, div[contenteditable=true]",
        "send_selector": "button[data-testid='send-button']",
        "stop_selector": "button[data-testid='stop-button']",
        "best_for": "general long-form, code, math (GPT-4 / o1)",
        "max_context": "128k+ tokens",
    },
    "claude": {
        "url": "https://claude.ai/",
        "input_selector": "div[contenteditable=true][prosemirror]",
        "send_selector": "button[aria-label='Send Message']",
        "stop_selector": "button[aria-label='Stop Response']",
        "best_for": "long-context analysis (200k tokens), careful writing",
        "max_context": "200k tokens",
    },
    "gemini": {
        "url": "https://gemini.google.com/",
        "input_selector": "rich-textarea textarea, textarea",
        "send_selector": "button[aria-label='Send message']",
        "stop_selector": "button[aria-label='Stop']",
        "best_for": "multimodal (image + text), Google-flavored search",
        "max_context": "1M tokens (Gemini 1.5 Pro)",
    },
    "perplexity": {
        "url": "https://www.perplexity.ai/",
        "input_selector": "textarea[auto-focus]",
        "send_selector": "button[type='submit']",
        "stop_selector": "button[aria-label*='Stop']",
        "best_for": "real-time web research with citations",
        "max_context": "n/a (search-based)",
    },
}


# ---- Prompt wrapping -----------------------------------------------------

def build_prompt(*,
                 role: str,
                 goal: str,
                 context: str = "",
                 task: str,
                 format_: str = "markdown prose",
                 length: str = "",
                 language: str = "match the user's input language",
                 constraints: str = "",
                 ) -> str:
    """Build a structured prompt for an external LLM.

    External LLMs answer better when given explicit structure. This wrapper
    enforces ROLE / CONTEXT / TASK / FORMAT / CONSTRAINTS.
    """
    parts: list[str] = [
        f"ROLE: You are {role}.",
        f"GOAL: {goal}",
    ]
    if context:
        parts.append(f"CONTEXT:\n{context}")
    parts.append(f"TASK: {task}")
    parts.append(f"FORMAT: {format_}")
    if length:
        parts.append(f"LENGTH: {length}")
    parts.append(f"LANGUAGE: {language}")
    if constraints:
        parts.append(f"CONSTRAINTS: {constraints}")
    parts.append("OUTPUT: Return only the final deliverable — no preamble.")
    return "\n\n".join(parts)


# ---- Sanitizer -----------------------------------------------------------

# Patterns to redact before pasting to external LLMs.
_SECRET_PATTERNS: list[tuple[str, str, str]] = [
    # (name, regex, replacement)
    ("API_KEY",        r"\b(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35}|gh[pousr]_[A-Za-z0-9]{36})\b",
     "[REDACTED_API_KEY]"),
    ("BEARER_TOKEN",   r"\b(Bearer\s+[A-Za-z0-9\-._~+\/]{40,})\b", "[REDACTED_BEARER]"),
    ("JWT",            r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b",
     "[REDACTED_JWT]"),
    ("CONN_STRING",    r"(mongodb|postgres|postgresql|redis|amqp)://[^\s\"']+",
     "[REDACTED_CONN_STRING]"),
    ("EMAIL",          r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
     "[REDACTED_EMAIL]"),
    ("PHONE_JP",       r"\b0\d{1,4}-\d{1,4}-\d{3,4}\b", "[REDACTED_PHONE]"),
    ("PHONE_US",       r"\b\+?1?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    ("CREDIT_CARD",    r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED_CC]"),
    ("IP",             r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[REDACTED_IP]"),
]


def sanitize(text: str, redact_email: bool = True,
             redact_phone: bool = True) -> str:
    """Redact obvious secrets / PII before pasting to an external LLM.

    Conservative: catches the most common leak patterns. Does NOT catch
    arbitrary source-code identifiers — sanitize those manually.
    """
    out = text
    for name, pattern, repl in _SECRET_PATTERNS:
        if name == "EMAIL" and not redact_email:
            continue
        if name in ("PHONE_JP", "PHONE_US") and not redact_phone:
            continue
        out = re.sub(pattern, repl, out)
    return out


# ---- Delegation plan -----------------------------------------------------

Target = Literal["chatgpt", "claude", "gemini", "perplexity"]


@dataclass
class DelegationPlan:
    task: str
    target: Target
    url: str
    prompt: str
    expected_format: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "target": self.target,
            "url": self.url,
            "prompt": self.prompt,
            "expected_format": self.expected_format,
            "notes": self.notes,
        }


def delegation_plan(*,
                    task: str,
                    context: str = "",
                    target: Target = "chatgpt",
                    role: str = "an expert assistant",
                    goal: str = "",
                    format_: str = "markdown prose",
                    length: str = "",
                    language: str = "match the user's input language",
                    constraints: str = "",
                    ) -> DelegationPlan:
    """Build a complete delegation plan ready to execute via browser tool."""
    if target not in TARGETS:
        raise ValueError(f"Unknown target {target!r}; pick from {list(TARGETS)}")
    if not goal:
        goal = f"complete the task: {task[:80]}"
    sanitized_context = sanitize(context)
    prompt = build_prompt(
        role=role, goal=goal, context=sanitized_context,
        task=task, format_=format_, length=length,
        language=language, constraints=constraints,
    )
    return DelegationPlan(
        task=task,
        target=target,
        url=TARGETS[target]["url"],
        prompt=prompt,
        expected_format=format_,
        notes=[
            f"Best for: {TARGETS[target]['best_for']}",
            "Sanitize secrets before pasting (run sanitize()).",
            "Wait for the stop button to disappear before extracting.",
            "Cite source URL + date in the final output.",
        ],
    )


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    plan = delegation_plan(
        task="Summarize the attached 50-page technical report into a 1-page executive brief.",
        context="""
        Author: alice@example.com, phone 03-1234-5678.
        API key for the internal system: sk-1234567890abcdefghij.
        Connection: postgres://user:pass@10.0.0.5:5432/db
        """,
        target="claude",
        role="a senior technical writer",
        goal="produce a 1-page executive brief",
        format_="markdown with H2 sections",
        length="≈500 words",
        language="English",
    )
    print("=== Delegation Plan ===")
    print(f"Target:  {plan.target}  →  {plan.url}")
    print(f"Task:    {plan.task}")
    print()
    print("=== Prompt (sanitized) ===")
    print(plan.prompt)
    print()
    print("=== Notes ===")
    for n in plan.notes:
        print(f"  - {n}")
