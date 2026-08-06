Tema_Q-Agent-skill
===================

A collection of skills for the Tema_Q Agent.
Each folder is one skill, made up of a SKILL.md (description) and a scripts folder (helper scripts).

Included Skills
----------------

- **art**  
  Skill for design decisions (color, typography, layout, UI/UX).
  Aims to avoid the generic "AI-made" look and produce output that feels human-made.

- **book-writing**  
  Writes long-form novels (approx. 80,000 words) without quality collapse.
  For fiction projects of 10,000+ words where consistency, character voice, and pacing must hold across many chapters.

- **docx**  
  Generates Microsoft Word (.docx) files using python-docx.
  Supports table of contents, styles, tables, images, headers/footers.

- **law**  
  Provides lawyer-level legal analysis and argument drafting by jurisdiction (JP / US / EU).
  Searches the web for current statutes and case law; used for legal-issue triage, drafting letters, and summarizing exposure.
  Always states this is not formal legal advice.

- **mail**  
  Drafts emails and letters in Japanese or American business/personal style.
  Chooses tone, format, and conventions appropriate to the recipient's country and relationship.

- **note**  
  Skill for writing articles for note.com.
  Searches popular articles in real time based on the user's theme, analyzes their patterns, and writes the article.
  Follows note.com's specific markdown formatting rules.

- **pdf**  
  Generates PDF files.
  Supports two paths: HTML to PDF (via Playwright/Chromium) and Office files (docx/pptx/xlsx) to PDF (via LibreOffice).

- **pptx**  
  Generates Microsoft PowerPoint (.pptx) files using python-pptx.
  Supports master layouts, tables, charts, and shapes.

- **recipe**  
  Plans nutritionally balanced meals (daily/weekly) with dietitian-level rigor.
  Searches the web for verified nutritional data and produces a printable meal plan with recipes and a shopping list.

- **skill-maker**  
  A meta-skill for creating new skills.
  Helps design, author, test, and publish skills in the SKILL.md format.

- **stock**
  Proposes concrete buy/sell strategies for Japanese and US stocks (ticker, price, entry day,
  take-profit/stop-loss lines, and rationale). Always includes a disclaimer that this is not investment advice.

- **use-gpts**  
  Delegates complex sub-tasks to external LLM web apps (ChatGPT, Claude.ai, Gemini, Perplexity) by driving the Tema_Q-Agent `--browser` tool.
  Used only when `--browser` mode is active and the task would otherwise consume too much local context.

- **xlsx**  
  Generates Microsoft Excel (.xlsx) files using openpyxl.
  Supports multiple sheets, formulas, charts, conditional formatting, and data validation.

Usage
-----

Please enter "/skill name" in the Tema_Q Agent.
