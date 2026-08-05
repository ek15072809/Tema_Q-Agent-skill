---
name: TEMPLATE
description: Template for creating a new skill. Copy this file to <skill-name>/SKILL.md and edit.
---

# <Skill Name>

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

## Advanced Patterns

### Pattern 1: <use case>
```python
# code example
```

### Pattern 2: <use case>
```python
# code example
```

## Workflow

1. **Clarify requirements**: <what to ask>
2. **Design**: <what to decide>
3. **Implement**: save to `/home/z/my-project/scripts/gen_<name>.py`
4. **Run**: `python scripts/gen_<name>.py`
5. **Verify**: <checklist>

## Output Spec

- Script path: `/home/z/my-project/scripts/`
- Output path: `/home/z/my-project/download/`
- Filename convention: `<category>_<name>_<date>.<ext>`

## Common Pitfalls

| Pitfall | Cause | Fix |
|---|---|---|
| <pitfall 1> | <cause> | <fix> |
| <pitfall 2> | <cause> | <fix> |

## Best Practices

- <point 1>
- <point 2>
- <point 3>
