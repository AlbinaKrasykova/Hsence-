"""Clinician handoff — questions and visit summary."""

from __future__ import annotations

from typing import Any


def generate_clinician_handoff(
    care_gaps: list[dict[str, Any]],
    layers: dict[str, dict[str, Any]],
    pattern: str,
    profile: dict[str, Any],
    precision_plan: dict[str, Any],
) -> dict[str, Any]:
    questions: list[dict[str, str]] = []
    summary_points: list[str] = []

    gap_map = {g["id"]: g for g in care_gaps}

    if "androgen_excess" in gap_map:
        g = gap_map["androgen_excess"]
        questions.append(
            {
                "q": "Given my LH:FSH and testosterone pattern, should we formally evaluate PCOS or related androgen excess?",
                "because": " · ".join(g.get("evidence", [])[:2]),
            }
        )
        summary_points.append("Pattern suggests androgen excess — seek formal endocrine evaluation")

    if "insulin_resistance" in gap_map:
        g = gap_map["insulin_resistance"]
        questions.append(
            {
                "q": "Is metformin or lifestyle-first protocol appropriate given my glucose/HOMA-IR pattern?",
                "because": " · ".join(g.get("evidence", [])[:2]),
            }
        )
        summary_points.append("Insulin resistance signal — discuss metabolic intervention")

    if "vitamin_d" in gap_map:
        questions.append(
            {
                "q": "What vitamin D repletion plan and retest interval do you recommend?",
                "because": gap_map["vitamin_d"].get("note", "Vitamin D insufficient"),
            }
        )

    if "cardiovascular" in gap_map:
        questions.append(
            {
                "q": "Should I repeat lipids in 3–6 months and consider cardiovascular risk reduction?",
                "because": "Adverse lipid pattern on recent panel",
            }
        )

    if "iron_fatigue" in gap_map:
        questions.append(
            {
                "q": "Could low ferritin be contributing to fatigue alongside my hormonal pattern?",
                "because": "Ferritin low-normal on panel",
            }
        )

    weak = [l["label"] for l in layers.values() if l.get("score", 100) < 60]
    if weak:
        summary_points.append(f"Layers needing support: {', '.join(weak[:3])}")

    supps = [s["name"] for s in precision_plan.get("supplements", [])[:3]]
    if supps:
        questions.append(
            {
                "q": f"Are these supplements appropriate for me: {', '.join(supps)}?",
                "because": "Precision plan matched to labs — confirm doses and interactions",
            }
        )

    if not questions:
        questions.append(
            {
                "q": "Can we review my recent hormone and metabolic panel together?",
                "because": pattern or "General endocrine-metabolic review",
            }
        )

    return {
        "tool": "generate_clinician_handoff",
        "questions_for_doctor": questions[:6],
        "visit_summary": summary_points[:5] or [pattern],
        "patient_name": profile.get("name", "Patient"),
        "evidence": [q["because"] for q in questions[:3]],
        "confidence": 0.87,
    }
