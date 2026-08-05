"""skill_maker.py — Scaffold a new skill directory with SKILL.md + supporting files.

Usage:
    python skill_maker.py <skill-name> [--description "..."] [--out ./skill]

Creates:
    <out>/<skill-name>/
    ├── SKILL.md         (from TEMPLATE.md, with name + description filled in)
    ├── references.md    (empty stub)
    └── scripts/
        └── .gitkeep
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


# ---- Default SKILL.md template -------------------------------------------

SKILL_MD_TEMPLATE = """\
---
name: {name}
description: {description}
---

# {title}

## Overview
<1–2 sentences on what this skill does>

## Required Libraries
```bash
pip install <package>
```

## Base Template

```python
# Tested, runnable code goes here
import xxx

def main():
    pass

if __name__ == '__main__':
    main()
```

## Workflow

1. **Clarify requirements**: <what to ask>
2. **Design**: <what to decide>
3. **Implement**: save script to `/home/z/my-project/scripts/gen_{name}.py`
4. **Run**: `python scripts/gen_{name}.py`
5. **Verify**: <checklist>

## Output Spec

- Script path: `/home/z/my-project/scripts/`
- Output path: `/home/z/my-project/download/`
- Filename convention: `<category>_{name}_<date>.<ext>`

## Common Pitfalls

| Pitfall | Cause | Fix |
|---|---|---|
| <pitfall 1> | <cause> | <fix> |
| <pitfall 2> | <cause> | <fix> |

## Best Practices

- <point 1>
- <point 2>
- <point 3>
"""


REFERENCES_STUB = """\
# Reference — {name}

Move long-form details here so SKILL.md stays under ~300 lines.

## Cheatsheet
<!-- tables, comparisons, command lists -->

## Deep Dives
<!-- step-by-step deep dives for advanced use cases -->
"""


# ---- Helpers --------------------------------------------------------------

def slugify(name: str) -> str:
    """Normalize a skill name: lowercase, kebab-case, ASCII-only."""
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        raise ValueError(f"Invalid skill name: {name!r}")
    return s


def title_case(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


# ---- Scaffold -------------------------------------------------------------

def scaffold(name: str,
             description: str,
             out_dir: str | Path = ".") -> Path:
    slug = slugify(name)
    title = title_case(slug)
    if not description:
        description = (
            f"Use when the user asks to {slug.replace('-', ' ')}. "
            f"Produces <output>. Built with <library>."
        )

    base = Path(out_dir) / slug
    if base.exists():
        raise FileExistsError(f"Directory already exists: {base}")
    (base / "scripts").mkdir(parents=True, exist_ok=True)

    (base / "SKILL.md").write_text(
        SKILL_MD_TEMPLATE.format(
            name=slug,
            description=description,
            title=title,
        ),
        encoding="utf-8",
    )
    (base / "references.md").write_text(
        REFERENCES_STUB.format(name=title),
        encoding="utf-8",
    )
    (base / "scripts" / ".gitkeep").write_text("")
    return base


# ---- CLI ------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a new skill directory.")
    ap.add_argument("name", help="Skill name (will be kebab-cased)")
    ap.add_argument("--description", "-d", default="",
                    help="One-line description for the YAML frontmatter")
    ap.add_argument("--out", "-o", default=".",
                    help="Output directory (default: current dir)")
    args = ap.parse_args(argv)

    try:
        path = scaffold(args.name, args.description, args.out)
    except (ValueError, FileExistsError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created skill scaffold:")
    for p in sorted(path.rglob("*")):
        print(f"  {p.relative_to(path.parent)}")
    print(f"\nNext steps:")
    print(f"  1. Edit {path}/SKILL.md")
    print(f"  2. Add scripts under {path}/scripts/")
    print(f"  3. Test by activating /{path.name} in Tema_Q-Agent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
