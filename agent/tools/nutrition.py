"""Precision food, nutrition, and supplement recommendations."""

from __future__ import annotations

from typing import Any

MEALS = [
    {
        "id": "oats",
        "name": "Oats + flax + cinnamon",
        "meta": "Low-GI · insulin-friendly · anti-inflammatory",
        "layers": ["metabolic", "inflammation", "hormones"],
        "priority": 90,
    },
    {
        "id": "eggs_greens",
        "name": "Eggs + greens + olive oil",
        "meta": "Protein-forward breakfast · steady glucose",
        "layers": ["metabolic", "cognition", "hormones"],
        "priority": 88,
    },
    {
        "id": "salmon",
        "name": "Salmon + roasted vegetables",
        "meta": "Omega-3 · triglyceride support · 3×/week target",
        "layers": ["metabolic", "inflammation", "cognition"],
        "priority": 92,
    },
    {
        "id": "lentil",
        "name": "Lentil soup + turmeric",
        "meta": "Fibre · low GI · gut-calming",
        "layers": ["metabolic", "inflammation"],
        "priority": 85,
    },
    {
        "id": "chicken_avocado",
        "name": "Chicken + avocado salad",
        "meta": "Protein + healthy fats · satiety",
        "layers": ["metabolic", "hormones"],
        "priority": 80,
    },
    {
        "id": "berry_smoothie",
        "name": "Berry smoothie (no dairy)",
        "meta": "Antioxidants · lower androgen load",
        "layers": ["hormones", "inflammation"],
        "priority": 75,
    },
]

FOOD_RULES = [
    {
        "id": "low_gi_protein",
        "title": "Low-GI protein at every meal",
        "why": "Targets insulin resistance driving androgen excess",
        "layers": ["metabolic", "hormones"],
        "when_gaps": ["insulin_resistance"],
    },
    {
        "id": "omega3_fish",
        "title": "Oily fish 3× per week",
        "why": "Supports triglycerides and inflammatory load",
        "layers": ["metabolic", "inflammation"],
        "when_gaps": ["cardiovascular", "insulin_resistance"],
    },
    {
        "id": "reduce_dairy_high_gi",
        "title": "Reduce dairy + high-GI carbs on inflammation days",
        "why": "Logged triggers correlate with symptom spikes",
        "layers": ["inflammation", "hormones"],
        "when_daily": {"inflammation": ["mild", "noticeable"]},
    },
    {
        "id": "iron_foods",
        "title": "Iron-aware meals (leafy greens + vitamin C pairing)",
        "why": "Ferritin low-normal — food-first before supplementing iron",
        "layers": ["cognition"],
        "when_gaps": ["iron_fatigue"],
    },
    {
        "id": "spearmint_tea",
        "title": "Spearmint tea (2 cups daily)",
        "why": "Evidence for lowering free testosterone in PCOS patterns",
        "layers": ["hormones"],
        "when_gaps": ["androgen_excess"],
    },
    {
        "id": "magnesium_foods",
        "title": "Magnesium-rich foods (pumpkin seeds, leafy greens)",
        "why": "Supports sleep, glucose handling, and recovery layer",
        "layers": ["cognition", "metabolic"],
        "when_layers_below": {"cognition": 65},
    },
]

SUPPLEMENTS = [
    {
        "name": "Myo-Inositol + D-Chiro (40:1)",
        "type": "supplement",
        "evidence": "Strong PCOS insulin + LH:FSH evidence base",
        "layers": ["hormones", "metabolic"],
        "when_gaps": ["insulin_resistance", "androgen_excess"],
        "note": "Discuss with clinician if already on metformin",
        "priority": 95,
    },
    {
        "name": "Vitamin D3 + K2",
        "type": "supplement",
        "evidence": "Replete insufficiency — linked to insulin, mood, bone",
        "layers": ["cognition", "metabolic", "hormones"],
        "when_gaps": ["vitamin_d"],
        "note": "Retest in 12 weeks",
        "priority": 90,
    },
    {
        "name": "Magnesium glycinate",
        "type": "supplement",
        "evidence": "Sleep, glucose handling, cramping — low risk",
        "layers": ["cognition", "metabolic"],
        "when_layers_below": {"cognition": 70},
        "note": "Evening dose often best tolerated",
        "priority": 82,
    },
    {
        "name": "NAC",
        "type": "supplement",
        "evidence": "May improve insulin sensitivity and SHBG",
        "layers": ["metabolic", "hormones"],
        "when_gaps": ["insulin_resistance"],
        "note": "Avoid high doses with asthma history",
        "priority": 78,
    },
    {
        "name": "Omega-3 (EPA/DHA)",
        "type": "supplement",
        "evidence": "Triglyceride-friendly; anti-inflammatory",
        "layers": ["metabolic", "inflammation"],
        "when_gaps": ["cardiovascular"],
        "note": "Food-first still primary",
        "priority": 80,
    },
    {
        "name": "Iron",
        "type": "supplement",
        "evidence": "Only if ferritin deficiency confirmed",
        "layers": ["cognition"],
        "when_gaps": ["iron_fatigue"],
        "note": "Do not self-start — confirm with GP first",
        "priority": 40,
    },
]

LIFESTYLE = [
    {
        "name": "Resistance training 3×/week",
        "layers": ["metabolic", "hormones"],
        "when_gaps": ["insulin_resistance"],
    },
    {
        "name": "Sleep regularity window (±30 min)",
        "layers": ["cognition", "metabolic"],
        "when_layers_below": {"cognition": 70},
    },
    {
        "name": "Reduce alcohol (4-week trial)",
        "layers": ["hormones", "metabolic", "inflammation"],
        "when_gaps": ["insulin_resistance", "androgen_excess"],
    },
]


def _gap_ids(gaps: list[dict[str, Any]]) -> set[str]:
    return {g["id"] for g in gaps}


def recommend_precision_nutrition(
    gaps: list[dict[str, Any]],
    layers: dict[str, dict[str, Any]],
    daily_log: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    gap_ids = _gap_ids(gaps)
    foods: list[dict[str, Any]] = []
    supplements: list[dict[str, Any]] = []
    lifestyle: list[dict[str, Any]] = []
    meals: list[dict[str, Any]] = []
    evidence: list[str] = []

    for rule in FOOD_RULES:
        match = False
        if rule.get("when_gaps") and gap_ids.intersection(rule["when_gaps"]):
            match = True
        when_daily = rule.get("when_daily", {})
        if when_daily.get("inflammation") and daily_log.get("inflammation") in when_daily["inflammation"]:
            match = True
        threshold = rule.get("when_layers_below", {})
        for layer_id, min_score in threshold.items():
            if layers.get(layer_id, {}).get("score", 100) < min_score:
                match = True
        if match:
            foods.append({k: v for k, v in rule.items() if k not in {"when_gaps", "when_daily", "when_layers_below"}})
            evidence.append(f"Food rule: {rule['title']}")

    layer_ids_needing_support = {lid for lid, data in layers.items() if data.get("score", 100) < 70}
    for meal in MEALS:
        if layer_ids_needing_support.intersection(meal["layers"]) or gap_ids.intersection({"insulin_resistance", "androgen_excess"}):
            meals.append(meal)
    meals.sort(key=lambda m: m["priority"], reverse=True)

    for supp in SUPPLEMENTS:
        match = False
        if supp.get("when_gaps") and gap_ids.intersection(supp["when_gaps"]):
            match = True
        for layer_id, min_score in supp.get("when_layers_below", {}).items():
            if layers.get(layer_id, {}).get("score", 100) < min_score:
                match = True
        if match:
            supplements.append({k: v for k, v in supp.items() if k not in {"when_gaps", "when_layers_below", "priority"}})
            evidence.append(f"Supplement matched: {supp['name']}")

    supplements.sort(
        key=lambda s: next(x["priority"] for x in SUPPLEMENTS if x["name"] == s["name"]),
        reverse=True,
    )

    for item in LIFESTYLE:
        match = False
        if item.get("when_gaps") and gap_ids.intersection(item["when_gaps"]):
            match = True
        for layer_id, min_score in item.get("when_layers_below", {}).items():
            if layers.get(layer_id, {}).get("score", 100) < min_score:
                match = True
        if match:
            lifestyle.append({k: v for k, v in item.items() if k not in {"when_gaps", "when_layers_below"}})

    return {
        "tool": "recommend_precision_nutrition",
        "foods": foods[:6],
        "meals": meals[:4],
        "supplements": supplements[:5],
        "lifestyle": lifestyle[:4],
        "evidence": evidence,
        "confidence": 0.84,
        "disclaimer": "Personalised suggestions for awareness — not prescribing. Confirm supplements and doses with your clinician.",
    }
