---
name: skill-maker
description: Meta-skill for developing new skills. Guides the design, authoring, testing, and publishing of SKILL.md-format skills. Use whenever the user asks to create a new skill.
---

# Skill Maker Skill

## Overview
This skill creates new skills. Follows the Claude Agent Skills–compatible format (SKILL.md + YAML frontmatter).

## Bundled Scaffolder Script
**`skill/skill-maker/scripts/skill_maker.py`** scaffolds a new skill directory:

```bash
python skill/skill-maker/scripts/skill_maker.py my-skill \
    --description "Use when ..." \
    --out ./skill
```

Creates:
```
my-skill/
├── SKILL.md         (filled in with name + description)
├── references.md    (empty stub)
└── scripts/.gitkeep
```
Run with no args to see usage.

## Skill Directory Structure

```
skill/<name>/
├── SKILL.md          # required, main instruction file
├── references.md     # optional, detailed reference
├── scripts/          # optional, runnable scripts
│   └── *.py
└── templates/        # optional, user-editable templates
    └── *.txt
```

## SKILL.md Format (required)

```markdown
---
name: skill-name
description: 1–2 sentences on when and how to use. Keep ≤120 chars — shown in the system prompt index.
---

# Skill Name

## Overview
1–2 sentences on what this skill does.

## Required Libraries / Tools
\`\`\`bash
pip install xxx
\`\`\`

## Workflow
1. Clarify requirements
2. Design
3. Implement
4. Verify

## Templates
Concrete examples in code blocks.

## Common Pitfalls
Table of pitfall → fix.
```

## Design Principles

### 1. Writing the Description
- **Mandatory**: state the trigger condition (when to use)
- **Mandatory**: state capability in one sentence
- **Recommended**: ≤120 chars (gets truncated in the system prompt)
- **Forbidden**: vague phrases ("advanced", "useful")

**Good**:
> Generate advanced Microsoft Word (.docx) files with python-docx. Includes TOC, styles, tables, images, headers/footers, sections, formulas. Use for any real document-generation task.

**Bad**:
> A skill to conveniently create Word documents.

### 2. Writing the Body

#### Required Sections
1. **Overview**: what it does, 1–2 sentences
2. **Required tools**: `pip install` etc.
3. **Base template**: copy-pasteable code
4. **Workflow**: numbered steps
5. **Output flow**: file-save paths included
6. **Common pitfalls**: table form

#### Efficiency Rules
- **Minimize context**: be concise, skip redundant explanation
- **Concrete code**: prefer working examples over abstract description
- **Use tables**: pitfall fixes, comparisons, cheatsheets
- **Bullets**: increase information density
- **Split files**: move long content into `references.md`

#### Forbidden Patterns
- Long paragraph explanations (3+ lines of prose)
- Abstract principles only (no examples)
- Repetition of the same content
- Unnecessary preface / closing
- Excessive emoji / decoration

### 3. When to Split Files

| Content | Location |
|---|---|
| Core flow + base template | `SKILL.md` |
| Detailed reference / cheatsheet | `references.md` |
| Runnable scripts | `scripts/*.py` |
| User-editable templates | `templates/*` |

Rule of thumb: if `SKILL.md` exceeds **~300 lines**, split.

## Authoring Workflow

### Step 1: Requirements
- [ ] Skill name (kebab-case)
- [ ] Purpose (one sentence)
- [ ] Trigger condition (when to use)
- [ ] Input (what the user provides)
- [ ] Output (what is produced)
- [ ] Required tools / libraries

### Step 2: Structure Design
- [ ] List required sections
- [ ] Design code templates
- [ ] Decide on file split
- [ ] Decide on references.md

### Step 3: Author SKILL.md
- [ ] YAML frontmatter
- [ ] Overview
- [ ] Required tools
- [ ] Base template (tested code)
- [ ] Advanced patterns
- [ ] Workflow
- [ ] Output flow (explicit paths)
- [ ] Common pitfalls (table)

### Step 4: Test
- [ ] Run `/skill-name` in another project
- [ ] Verify it works as expected
- [ ] Verify the LLM interprets instructions correctly
- [ ] Verify context size is reasonable

### Step 5: Deploy
```
/home/z/my-project/skill/<name>/SKILL.md
```

## Description Self-Check Questions

When creating a new skill, ask:
1. **When to use**: what user request triggers it?
2. **What it does**: what specifically does it produce / run?
3. **How it's built**: which libraries / tools does it use?
4. **Who it's for**: who is the output for (end user / developer)?

Condense all four answers into the description.

## Quality Checklist

### Required
- [ ] YAML frontmatter has `name` and `description`
- [ ] Description states trigger explicitly
- [ ] Overview section exists
- [ ] Concrete code examples exist
- [ ] File output path is explicit
- [ ] Pitfalls section exists

### Recommended
- [ ] Workflow is numbered and clear
- [ ] Tables for high information density
- [ ] Long content split into `references.md`
- [ ] Scripts saved to `/home/z/my-project/scripts/`
- [ ] Output saved to `/home/z/my-project/download/`

## Template (copy to start)

Copy `TEMPLATE.md` and edit for the new skill.

## Advanced Skill Design

### Multi-File Coordination
```
skill/data-pipeline/
├── SKILL.md            # main (flow definition)
├── references.md       # detailed options
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
└── templates/
    └── config.yaml
```

Referenced from SKILL.md:
```
See `references.md` for detailed extraction options.
Run the extraction script `scripts/extract.py`.
```

### Lazy Loading
SKILL.md is always loaded; references.md only when needed.
→ Keep SKILL.md minimal, push details to references.md.

## Publishing (GitHub)

```bash
# Repo layout
skill-registry/
├── art/
│   └── SKILL.md
├── docx/
│   └── SKILL.md
└── README.md

# Zip for distribution
cd skill-registry
zip -r skills.zip */SKILL.md */*.md
```

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Vague description | Make trigger condition concrete |
| Body too long | Split into references.md |
| Code doesn't run | Mandatory real test |
| File paths unclear | Always specify paths under `/home/z/my-project/` |
| LLM confused | Use clear section headings |
| Context bloat | Use tables / bullets, avoid prose |
