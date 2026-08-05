---
name: use-gpts
description: Delegate complex sub-tasks to external LLM web apps (ChatGPT, Claude.ai, Gemini, Perplexity) by driving the Tema_Q-Agent `--browser` tool. Use only when --browser mode is active and the task would consume too many context tokens to do locally.
---

# Use-GPTs Skill

## Overview
When the agent runs in `--browser` mode, this skill drives an external LLM
web app to offload sub-tasks that would otherwise burn the local context
window (long-form writing, deep analysis, multi-step research).

Supported targets:
- ChatGPT — https://chatgpt.com/
- Claude.ai — https://claude.ai/
- Gemini — https://gemini.google.com/
- Perplexity — https://www.perplexity.ai/

## When to Use (and when NOT to)

| Use it | Do NOT use it |
|---|---|
| Long-form draft (≥2000 words) | Simple lookup, definition, translation |
| Deep multi-source research | Tasks the local model already does well |
| Code review of large files | Anything confidential / sensitive |
| Image-based analysis (when target supports vision) | Tasks needing a verifiable source trail |
| Tasks where the local model is too weak (math, niche domain) | Anything inside a private codebase |

**Confidentiality rule**: never paste secrets, credentials, PII, or
unpublished source code into external LLM sites. Sanitize first.

## Bundled Helper Module
**`skill/use-gpts/scripts/use_gpts.py`** provides:
- `TARGETS` — supported external sites with their selectors (best-effort, sites change).
- `build_prompt(task, context)` — wraps the user task with a clear instruction header.
- `sanitize(text)` — strips obvious secrets / PII patterns before pasting.
- `delegation_plan(task)` — returns a structured plan (target, prompt, expected_format).

```python
import sys; sys.path.insert(0, "skill/use-gpts/scripts")
from use_gpts import TARGETS, build_prompt, sanitize, delegation_plan
```
Run `python skill/use-gpts/scripts/use_gpts.py` to print a sample plan.

## Workflow

1. **Decide** if external delegation is justified (see table above).
2. **Plan**: pick the target site (see TARGETS), draft the prompt, sanitize input.
3. **Open**: use the `browser` tool to navigate to the target URL.
4. **Authenticate**: if not logged in, pause and ask the user to log in once
   (sessions persist within the Chromium profile for the session).
5. **Submit prompt**: type the prompt into the chat input box, press Enter.
6. **Wait**: poll the page every 5-10s until the response stream completes
   (look for the absence of a "stop generating" button).
7. **Extract**: snapshot the page text; isolate the assistant's reply.
8. **Post-process**: trim boilerplate, format as Markdown, cite the source URL + date.
9. **Hand back**: return the response to the parent task. Do not claim authorship.

## Browser Tool Cheatsheet

The `browser` tool (Tema_Q-Agent v4+) exposes these actions:
```
browser(action="navigate", url="https://chatgpt.com/")
browser(action="snapshot")                     # returns page text
browser(action="click", selector="textarea")
browser(action="type", selector="textarea", text="...")
browser(action="click", selector="button[data-testid='send-button']")
browser(action="close")
```
**CSS selectors change frequently.** Always snapshot first and adapt.

## Per-Target Notes

### ChatGPT (https://chatgpt.com/)
- Input: `textarea#prompt-textarea` or `div[contenteditable=true]` (varies).
- Send: `button[data-testid="send-button"]` or press Enter (model-dependent).
- Wait for completion: the "Stop generating" button disappears.
- Best for: general long-form, code, math (GPT-4 / o1).

### Claude.ai (https://claude.ai/)
- Input: `div[contenteditable=true][prosemirror]` (typically).
- Send: `button[aria-label="Send Message"]` or Enter.
- Wait: the "Stop" button disappears; the latest message bubble stops growing.
- Best for: long-context analysis (100k+ tokens), careful writing.

### Gemini (https://gemini.google.com/)
- Input: `rich-textarea` or `textarea` (varies by account type).
- Send: `button[aria-label="Send message"]` or `mat-icon` with text "send".
- Best for: multimodal (image + text), Google-flavored search.

### Perplexity (https://www.perplexity.ai/)
- Input: `textarea[auto-focus]`.
- Send: Enter or the submit button.
- Best for: real-time web research with citations.
- Always preserve the source URLs from the response.

## Prompt Wrapping
External LLMs do best with explicit structure. Always wrap:

```
ROLE: You are a {role}. Your goal: {goal}.
CONTEXT: {sanitized context}
TASK: {concrete task}
FORMAT: {bullet list / prose / JSON / markdown table}
CONSTRAINTS: {length, tone, language, things to avoid}
OUTPUT: {final deliverable only — no preamble}
```

## Self-Check
- [ ] Justified? (would otherwise consume too much local context)
- [ ] Sanitized? (no secrets, PII, unpublished code)
- [ ] Target picked? (right model for the task)
- [ ] Prompt wrapped with ROLE/CONTEXT/TASK/FORMAT?
- [ ] User notified of delegation? (transparency)
- [ ] Source URL + date captured in output?
- [ ] Response trimmed of boilerplate?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Selector not found | Snapshot first; sites change their DOM |
| Pasted secret | Run `sanitize()` before pasting |
| Stream not complete | Wait for "stop" button to disappear |
| Wrong language reply | Add `LANGUAGE: {lang}` to prompt wrapper |
| Output too long | Add `LENGTH: {N} words max` to prompt |
| Claims local authorship | Always cite source URL + date |
| Login wall | Ask user to log in once; session persists |

## Confidentiality — what NEVER to paste
- API keys, OAuth tokens, bearer tokens
- Database connection strings
- Customer PII (names, emails, phone, addresses)
- Unpublished financial figures
- Internal-only source code (sanitize variable names / comments)
- Anything covered by an NDA

When in doubt: **sanitize first, or do it locally.**
