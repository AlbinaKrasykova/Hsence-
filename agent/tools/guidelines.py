"""Evidence guideline snippets for explainable recommendations."""

from __future__ import annotations

from typing import Any

GUIDELINES = [
    {
        "id": "pcos_rotterdam",
        "title": "PCOS screening context",
        "source": "Rotterdam criteria · clinical reference",
        "snippet": "Elevated LH:FSH ratio with hyperandrogenism and oligo-anovulation is a commonly used PCOS screening pattern — formal diagnosis requires clinical evaluation.",
        "when_gaps": ["androgen_excess", "insulin_resistance"],
    },
    {
        "id": "insulin_food_first",
        "title": "Insulin resistance · lifestyle first",
        "source": "Endocrine Society · lifestyle guidance",
        "snippet": "For insulin resistance patterns, low-GI dietary pattern and resistance exercise are first-line before medication discussion.",
        "when_gaps": ["insulin_resistance"],
    },
    {
        "id": "vitamin_d_replete",
        "title": "Vitamin D insufficiency",
        "source": "Endocrine practice · repletion",
        "snippet": "Vitamin D insufficiency is associated with insulin sensitivity and mood burden — repletion with retesting is standard practice.",
        "when_gaps": ["vitamin_d"],
    },
    {
        "id": "inositol_pcos",
        "title": "Myo-inositol evidence",
        "source": "PCOS supplement literature",
        "snippet": "Myo-inositol has the strongest supplement evidence base for PCOS-related insulin sensitivity and LH:FSH improvement — discuss with clinician if on metformin.",
        "when_gaps": ["insulin_resistance", "androgen_excess"],
    },
    {
        "id": "inflammation_diet",
        "title": "Inflammation · dietary modulation",
        "source": "Nutrition · anti-inflammatory pattern",
        "snippet": "Omega-3 rich foods and reduced ultra-processed intake may lower inflammatory symptom burden when paired with sleep regularity.",
        "when_layers": ["inflammation"],
    },
]


def retrieve_guideline_snippet(
    care_gaps: list[dict[str, Any]],
    layers: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    gap_ids = {g["id"] for g in care_gaps}
    weak_layers = {lid for lid, data in layers.items() if data.get("score", 100) < 70}
    hits = []
    evidence = []

    for g in GUIDELINES:
        match = False
        if g.get("when_gaps") and gap_ids.intersection(g["when_gaps"]):
            match = True
        if g.get("when_layers") and weak_layers.intersection(g["when_layers"]):
            match = True
        if match:
            hits.append({k: v for k, v in g.items() if k not in {"when_gaps", "when_layers"}})
            evidence.append(g["title"])

    if not hits and gap_ids:
        hits.append(
            {
                "id": "general_handoff",
                "title": "Clinical conversation",
                "source": "Hsence · awareness only",
                "snippet": "Bring your lab pattern summary to a GP or endocrinologist for formal evaluation — Hsence supports conversation prep, not diagnosis.",
            }
        )
        evidence.append("General handoff guidance")

    return {
        "tool": "retrieve_guideline_snippet",
        "guidelines": hits[:4],
        "evidence": evidence,
        "confidence": 0.85 if hits else 0.4,
    }
