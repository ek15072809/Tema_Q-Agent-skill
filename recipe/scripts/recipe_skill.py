"""recipe_skill.py — Helpers for nutritionally balanced meal planning.

Standard-library only. Provides:
  * DRIs            — Dietary Reference Intakes (JP MHLW 2020 + US NASEM).
  * MACRO_RATIOS    — recommended macro splits by goal.
  * FoodItem        — per-100g nutrition facts.
  * Meal            — list of FoodItems + recipe metadata.
  * MealPlan        — full day of meals + profile.
  * compute_totals  — sum a MealPlan into a NutritionTotal.
  * evaluate        — compare totals vs DRI target; flag deficits/surpluses.
  * shopping_list   — dedupe ingredients, sum quantities.
  * format_plan_md  — render the plan as Markdown.

Numbers below are simplified reference values for planning. Always cross-check
against authoritative sources (USDA / MHLW) before clinical use.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


# ---- Dietary Reference Intakes ------------------------------------------

# Simplified — covers sedentary adults and children. For full data, websearch
# the source (MHLW 2020 / NASEM DRI) and update.

DRIs: dict[str, dict[str, dict]] = {
    "JP": {  # MHLW 2020, sedentary
        "male_18_29":   {"kcal": 2300, "protein_g": 60, "fat_g": 77,  "carb_g": 288,
                          "fiber_g": 18, "sodium_mg": 3000, "calcium_mg": 800, "iron_mg": 7},
        "male_30_49":   {"kcal": 2300, "protein_g": 60, "fat_g": 77,  "carb_g": 288,
                          "fiber_g": 19, "sodium_mg": 3000, "calcium_mg": 800, "iron_mg": 7.5},
        "male_50_69":   {"kcal": 2400, "protein_g": 60, "fat_g": 80,  "carb_g": 300,
                          "fiber_g": 19, "sodium_mg": 3000, "calcium_mg": 700, "iron_mg": 7.5},
        "female_18_29": {"kcal": 1700, "protein_g": 50, "fat_g": 57,  "carb_g": 213,
                          "fiber_g": 17, "sodium_mg": 3000, "calcium_mg": 650, "iron_mg": 6},
        "female_30_49": {"kcal": 1800, "protein_g": 50, "fat_g": 60,  "carb_g": 225,
                          "fiber_g": 17, "sodium_mg": 3000, "calcium_mg": 650, "iron_mg": 6.5},
        "female_50_69": {"kcal": 1800, "protein_g": 50, "fat_g": 60,  "carb_g": 225,
                          "fiber_g": 17, "sodium_mg": 3000, "calcium_mg": 650, "iron_mg": 6.5},
        "child_6_7":    {"kcal": 1400, "protein_g": 33, "fat_g": 47,  "carb_g": 175,
                          "fiber_g": 12, "sodium_mg": 2200, "calcium_mg": 600, "iron_mg": 5},
        "child_10_11":  {"kcal": 1800, "protein_g": 50, "fat_g": 60,  "carb_g": 225,
                          "fiber_g": 14, "sodium_mg": 2400, "calcium_mg": 700, "iron_mg": 7},
    },
    "US": {  # NASEM, sedentary (estimated EER)
        "male_19_30":   {"kcal": 2400, "protein_g": 56, "fat_g": 80,  "carb_g": 300,
                          "fiber_g": 34, "sodium_mg": 2300, "calcium_mg": 1000, "iron_mg": 8},
        "male_31_50":   {"kcal": 2400, "protein_g": 56, "fat_g": 80,  "carb_g": 300,
                          "fiber_g": 31, "sodium_mg": 2300, "calcium_mg": 1000, "iron_mg": 8},
        "female_19_30": {"kcal": 1900, "protein_g": 46, "fat_g": 63,  "carb_g": 238,
                          "fiber_g": 28, "sodium_mg": 2300, "calcium_mg": 1000, "iron_mg": 18},
        "female_31_50": {"kcal": 1900, "protein_g": 46, "fat_g": 63,  "carb_g": 238,
                          "fiber_g": 25, "sodium_mg": 2300, "calcium_mg": 1000, "iron_mg": 18},
    },
}


# ---- Macro splits by goal ------------------------------------------------

MACRO_RATIOS: dict[str, dict[str, float]] = {
    # calories-from-macro fractions
    "maintain": {"carb": 0.50, "protein": 0.20, "fat": 0.30},
    "lose":     {"carb": 0.40, "protein": 0.30, "fat": 0.30},
    "gain":     {"carb": 0.45, "protein": 0.30, "fat": 0.25},
    "keto":     {"carb": 0.05, "protein": 0.25, "fat": 0.70},
}

# Calories per gram
KCAL_PER_G = {"carb": 4, "protein": 4, "fat": 9, "fiber": 2}


# ---- Data classes --------------------------------------------------------

@dataclass
class FoodItem:
    name: str
    quantity_g: float
    kcal: float        # per 100g
    protein_g: float   # per 100g
    fat_g: float       # per 100g
    carb_g: float      # per 100g
    fiber_g: float = 0.0   # per 100g
    sodium_mg: float = 0.0 # per 100g
    calcium_mg: float = 0.0
    iron_mg: float = 0.0
    source_url: str = ""

    def scaled(self) -> dict[str, float]:
        f = self.quantity_g / 100.0
        return {
            "kcal":       self.kcal * f,
            "protein_g":  self.protein_g * f,
            "fat_g":      self.fat_g * f,
            "carb_g":     self.carb_g * f,
            "fiber_g":    self.fiber_g * f,
            "sodium_mg":  self.sodium_mg * f,
            "calcium_mg": self.calcium_mg * f,
            "iron_mg":    self.iron_mg * f,
        }


@dataclass
class Meal:
    name: str               # "Breakfast" / "Lunch" / "Dinner" / "Snack"
    recipe_title: str
    items: list[FoodItem] = field(default_factory=list)
    method: list[str] = field(default_factory=list)
    source_url: str = ""

    def totals(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for item in self.items:
            for k, v in item.scaled().items():
                out[k] = out.get(k, 0.0) + v
        return out


@dataclass
class MealPlan:
    profile: dict           # age, sex, country, goal, allergies, etc.
    target: dict            # from DRIs[group]
    meals: list[Meal] = field(default_factory=list)


# ---- Computations --------------------------------------------------------

def compute_totals(plan: MealPlan) -> dict[str, float]:
    out: dict[str, float] = {}
    for meal in plan.meals:
        for k, v in meal.totals().items():
            out[k] = out.get(k, 0.0) + v
    return out


def evaluate(plan: MealPlan, tolerance_pct: float = 10.0) -> dict[str, dict]:
    """Compare actual totals vs DRI target.

    Returns {nutrient: {target, actual, pct, status}}.
    status: 'OK' (within ±tolerance), 'LOW', 'HIGH'.
    """
    actual = compute_totals(plan)
    out: dict[str, dict] = {}
    for nutrient, target_val in plan.target.items():
        if nutrient not in actual:
            continue
        a = actual[nutrient]
        if target_val == 0:
            pct = 0.0
        else:
            pct = (a - target_val) / target_val * 100
        if abs(pct) <= tolerance_pct:
            status = "OK"
        elif pct < 0:
            status = "LOW"
        else:
            status = "HIGH"
        out[nutrient] = {
            "target": target_val,
            "actual": round(a, 1),
            "pct": round(pct, 1),
            "status": status,
        }
    return out


# ---- Shopping list -------------------------------------------------------

def shopping_list(plan: MealPlan) -> dict[str, float]:
    """Dedupe ingredients and sum quantities (grams)."""
    out: dict[str, float] = {}
    for meal in plan.meals:
        for item in meal.items:
            out[item.name] = out.get(item.name, 0.0) + item.quantity_g
    return out


# ---- Markdown rendering --------------------------------------------------

def format_plan_md(plan: MealPlan) -> str:
    lines: list[str] = ["# Meal Plan", ""]
    p = plan.profile
    lines.append(f"## Profile")
    lines.append(f"- Age/Sex: {p.get('age','n/a')} {p.get('sex','n/a')}")
    lines.append(f"- Country: {p.get('country','n/a')}")
    lines.append(f"- Goal: {p.get('goal','maintain')}")
    lines.append(f"- Target kcal: {plan.target.get('kcal','n/a')}")
    if p.get("allergies"):
        lines.append(f"- Allergies/dislikes: {', '.join(p['allergies'])}")
    lines.append("")

    # Targets table
    lines.append("## Targets vs Actual")
    lines.append("| Nutrient | Target | Actual | Status |")
    lines.append("|---|---|---|---|")
    eval_ = evaluate(plan)
    for nut, row in eval_.items():
        lines.append(f"| {nut} | {row['target']} | {row['actual']} | {row['status']} ({row['pct']:+.1f}%) |")
    lines.append("")

    # Meals
    for meal in plan.meals:
        t = meal.totals()
        lines.append(f"## {meal.name} ({t.get('kcal', 0):.0f} kcal)")
        lines.append(f"**{meal.recipe_title}**")
        lines.append("")
        lines.append("Ingredients:")
        for it in meal.items:
            lines.append(f"- {it.name}: {it.quantity_g}g")
        if meal.method:
            lines.append("")
            lines.append("Method:")
            for i, step in enumerate(meal.method, 1):
                lines.append(f"{i}. {step}")
        if meal.source_url:
            lines.append("")
            lines.append(f"Source: {meal.source_url}")
        lines.append("")

    # Shopping list
    lines.append("## Shopping List")
    for name, grams in shopping_list(plan).items():
        lines.append(f"- [ ] {name} {grams:.0f}g")
    lines.append("")

    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    # Build a simple 1-meal plan to verify computations.
    rice = FoodItem(
        name="White rice (cooked)", quantity_g=200,
        kcal=168, protein_g=2.7, fat_g=0.3, carb_g=36.8,
        fiber_g=0.4, sodium_mg=1, calcium_mg=10, iron_mg=0.2,
        source_url="https://www.mext.go.jp/",
    )
    chicken = FoodItem(
        name="Chicken breast", quantity_g=150,
        kcal=165, protein_g=31, fat_g=3.6, carb_g=0,
        fiber_g=0, sodium_mg=74, calcium_mg=15, iron_mg=1,
        source_url="https://fdc.nal.usda.gov/",
    )
    broccoli = FoodItem(
        name="Broccoli", quantity_g=100,
        kcal=34, protein_g=2.8, fat_g=0.4, carb_g=6.6,
        fiber_g=2.6, sodium_mg=33, calcium_mg=47, iron_mg=0.7,
        source_url="https://fdc.nal.usda.gov/",
    )

    dinner = Meal(
        name="Dinner",
        recipe_title="Grilled chicken with rice and broccoli",
        items=[rice, chicken, broccoli],
        method=[
            "Cook rice according to package directions.",
            "Season chicken breast with salt and pepper, grill 6 min per side.",
            "Steam broccoli for 4 min until bright green.",
            "Plate everything together; serve immediately.",
        ],
        source_url="https://www.allrecipes.com/",
    )

    plan = MealPlan(
        profile={"age": 30, "sex": "male", "country": "JP",
                  "goal": "maintain", "allergies": []},
        target=DRIs["JP"]["male_30_49"],
        meals=[dinner],
    )

    print(format_plan_md(plan))
    print("\n--- Totals ---")
    print(compute_totals(plan))
    print("\n--- Shopping list ---")
    print(shopping_list(plan))
