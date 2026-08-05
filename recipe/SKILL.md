---
name: recipe
description: Plan nutritionally balanced meals (daily / weekly). Search the web for verified nutritional data, compute totals against dietary targets (USDA / Japanese MHLW), and produce a printable meal plan with recipes. Use for any meal-planning or menu-design task.
---

# Recipe Skill

## Overview
Plan meals with **dietitian-level** nutritional rigor.
- Daily / weekly plans; per-person or family.
- Targets: calories, protein, fat, carbs, fiber, sodium, vitamins/minerals.
- Sources: USDA FoodData Central, Japanese MHLW Dietary Reference Intakes, recipe sites.
- Output: printable meal plan + shopping list + per-meal recipe.

## Bundled Helper Module
**`skill/recipe/scripts/recipe_skill.py`** provides (standard library only):
- `DRIs` — Dietary Reference Intakes (JP MHLW 2020, US NASEM 2019), key groups.
- `MACRO_RATIOS` — recommended macro splits by goal.
- `FoodItem` / `Meal` / `MealPlan` dataclasses.
- `compute_totals(plan)` — sum all meals into a nutrition total.
- `evaluate(plan, dri)` — compare totals vs DRI; return deficits/surpluses.
- `shopping_list(plan)` — dedupe ingredients, sum quantities.
- `format_plan_md(plan)` — render as Markdown.

```python
import sys; sys.path.insert(0, "skill/recipe/scripts")
from recipe_skill import (DRIs, MACRO_RATIOS, FoodItem, Meal, MealPlan,
                          compute_totals, evaluate, shopping_list, format_plan_md)
```
Run `python skill/recipe/scripts/recipe_skill.py` to print a sample plan + evaluation.

## Workflow

1. **Profile** — age, sex, weight (kg), height (cm), activity, goal (lose/maintain/gain), allergies, dislikes.
2. **Targets** — pick DRI from `DRIs`; adjust calories by goal (±10-20%); set macro split.
3. **Search** — `websearch` for recipes + per-100g nutrition data; cite sources.
4. **Compose** — pick breakfast/lunch/dinner/snacks; assemble MealPlan.
5. **Evaluate** — `evaluate(plan, dri)`. Fix any >±20% deviation.
6. **Output** — `format_plan_md(plan)` + shopping list + source URLs.

## Nutrition Sources

| Need | Source |
|---|---|
| Per-food nutrients (US) | https://fdc.nal.usda.gov/ |
| Per-food nutrients (JP) | https://www.mext.go.jp/ (日本食品標準成分表) |
| JP Dietary Reference Intakes | Japanese MHLW 「日本人の食事摂取基準（2020年版）」 |
| US Dietary Reference Intakes | NASEM DRI tables |
| Recipes | https://cookpad.com/, https://www.allrecipes.com/, https://www.ajinomoto.co.jp/recipe/ |

When using websearch, query patterns:
```
"{food name} nutrition 100g {USDA OR 標準成分表}"
"{recipe name} 栄養価 カロリー タンパク質"
"{age} {sex} {country} 推定エネルギー必要量"
```

## DRI Quick Reference (calories & protein)

### Japan (MHLW 2020), sedentary
| Group | kcal/day | Protein g/day |
|---|---|---|
| Male 18-29 | 2,300 | 60 |
| Male 30-49 | 2,300 | 60 |
| Male 50-69 | 2,400 | 60 |
| Female 18-29 | 1,700 | 50 |
| Female 30-49 | 1,800 | 50 |
| Female 50-69 | 1,800 | 50 |
| Child 6-7 | 1,400 | 33 |
| Child 10-11 | 1,800 | 50 |

### US (NASEM), sedentary (estimated EER)
| Group | kcal/day | Protein g/day |
|---|---|---|
| Male 19-30 | 2,400 | 56 |
| Male 31-50 | 2,400 | 56 |
| Female 19-30 | 1,900 | 46 |
| Female 31-50 | 1,900 | 46 |

For full data (incl. vitamins, minerals, activity factors), use the `DRIs` dict in `recipe_skill.py` or websearch.

## Macro Splits (`MACRO_RATIOS`)

| Goal | Carbs | Protein | Fat |
|---|---|---|---|
| maintain | 50% | 20% | 30% |
| lose | 40% | 30% | 30% |
| gain (muscle) | 45% | 30% | 25% |
| keto | 5% | 25% | 70% |

Calories per gram: carbs 4, protein 4, fat 9, alcohol 7, fiber 2.

## Evaluation Rules
- Target ±10% = optimal. ±10-20% = acceptable. >±20% = revise.
- Sodium: JP target ≤7.5g salt (≈3g sodium) / day; US ≤2,300mg sodium / day.
- Fiber: ≥18g/day (JP), ≥25-38g/day (US by age/sex).
- Always check 3+ micronutrients (iron, calcium, vitamin D most common deficits).

## Output Format

```markdown
# Meal Plan — {Name}, {YYYY-MM-DD}

## Profile
- Age/Sex: {age} {sex}
- Goal: {maintain/lose/gain} | Target kcal: {N}
- Allergies/dislikes: {list}

## Targets
| Macro | Target | Actual | Status |
|---|---|---|---|
| Calories | 2,300 kcal | 2,280 kcal | OK |
| Protein | 60g | 62g | OK |
| Fat | 77g | 70g | -9% OK |
| Carbs | 288g | 305g | +6% OK |
| Fiber | 18g | 22g | OK |
| Sodium | ≤3,000mg | 2,800mg | OK |

## Breakfast ({kcal} kcal)
{recipe title}
- Ingredients: ...
- Method: 3-5 steps
- Nutrition per serving: ...

## Lunch ...
## Dinner ...
## Snack ...

## Shopping List
- [ ] Rice 1kg
- [ ] Chicken breast 500g
- [ ] ...

## Sources
- USDA FoodData Central: {URL}
- MHLW DRI 2020: {URL}
- Recipe: {URL}
```

## Self-Check
- [ ] DRI picked for correct age/sex/country?
- [ ] Macro split matches goal?
- [ ] All 4 macros (incl. fiber) computed?
- [ ] Sodium checked?
- [ ] At least 3 micronutrients checked?
- [ ] Each meal has a recipe (not just "salad")?
- [ ] Allergies/dislikes respected?
- [ ] Source URLs cited for nutrition data?
- [ ] Shopping list deduped?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Wrong DRI country | Confirm country first; use `DRIs[country][group]` |
| Missing fiber | Add vegetables/legumes/whole grains |
| Sodium underestimated | Sauces/miso/soy sauce add up; check per-tablespoon |
| Generic "vegetable" | Specify the vegetable (nutrients differ wildly) |
| No micronutrients | Check iron, calcium, vitamin D at minimum |
| Recipe too vague | Include ingredient quantities + 3-5 step method |
| Allergies ignored | Re-check after composing each meal |
