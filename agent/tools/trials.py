"""Mock clinical trial matching for demo."""

from __future__ import annotations

from typing import Any

MOCK_TRIALS = [
    {
        "id": "NCT-DEMO-001",
        "title": "Myo-inositol vs metformin for PCOS insulin resistance",
        "phase": "Phase III",
        "indication": "PCOS · insulin resistance",
        "eligibility_keys": ["insulin_resistance", "androgen_excess"],
        "age_range": "18–45",
        "match_reason": "HOMA-IR and androgen pattern align with metabolic PCOS cohort",
    },
    {
        "id": "NCT-DEMO-002",
        "title": "Lifestyle + omega-3 for cardiometabolic risk in anovulatory PCOS",
        "phase": "Phase II",
        "indication": "PCOS · cardiovascular risk",
        "eligibility_keys": ["insulin_resistance", "cardiovascular"],
        "age_range": "21–50",
        "match_reason": "Insulin resistance plus adverse lipid profile",
    },
    {
        "id": "NCT-DEMO-003",
        "title": "Vitamin D repletion impact on insulin sensitivity (women)",
        "phase": "Phase II",
        "indication": "Vitamin D insufficiency · metabolic",
        "eligibility_keys": ["vitamin_d", "insulin_resistance"],
        "age_range": "18–55",
        "match_reason": "Vitamin D insufficient with insulin resistance signal",
    },
    {
        "id": "NCT-DEMO-004",
        "title": "Spearmint tea intervention for hyperandrogenism",
        "phase": "Phase II",
        "indication": "PCOS · hirsutism/acne",
        "eligibility_keys": ["androgen_excess"],
        "age_range": "18–40",
        "match_reason": "Elevated androgen pattern — lifestyle adjunct trial",
    },
]


def match_clinical_trials(
    care_gaps: list[dict[str, Any]],
    profile: dict[str, Any],
) -> dict[str, Any]:
    gap_ids = {g["id"] for g in care_gaps}
    age = profile.get("age", 34)
    matches = []

    for trial in MOCK_TRIALS:
        if not gap_ids.intersection(set(trial["eligibility_keys"])):
            continue
        lo, hi = _parse_age_range(trial["age_range"])
        if age < lo or age > hi:
            continue
        matches.append(
            {
                "id": trial["id"],
                "title": trial["title"],
                "phase": trial["phase"],
                "indication": trial["indication"],
                "match_reason": trial["match_reason"],
                "eligibility_rationale": [
                    f"Care gap: {gid.replace('_', ' ')}" for gid in trial["eligibility_keys"] if gid in gap_ids
                ],
                "confidence": 0.78,
            }
        )

    matches.sort(key=lambda m: len(m["eligibility_rationale"]), reverse=True)

    return {
        "tool": "match_clinical_trials",
        "trials": matches[:3],
        "evidence": [t["title"] for t in matches[:3]],
        "confidence": 0.8 if matches else 0.3,
        "note": "Demo mock trials — not real enrollment. Verify on ClinicalTrials.gov with your clinician.",
    }


def _parse_age_range(text: str) -> tuple[int, int]:
    parts = text.replace("–", "-").split("-")
    try:
        return int(parts[0]), int(parts[1])
    except (IndexError, ValueError):
        return 18, 99
