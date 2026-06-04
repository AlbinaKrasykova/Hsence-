"""Patient front-door intent detection."""

from __future__ import annotations

import re
from typing import Any

INTENT_RULES = [
    {
        "id": "supplement_self_treatment",
        "patterns": [r"should i take", r"berberine", r"supplement", r"metformin dose", r"how much"],
        "risk": "high",
        "response_hint": "Redirect from self-prescribing to structured lab-informed conversation prep",
    },
    {
        "id": "trial_interest",
        "patterns": [r"trial", r"clinical study", r"enroll", r"research study"],
        "risk": "low",
        "response_hint": "Route to trial matching after care gap scoring",
    },
    {
        "id": "clinician_prep",
        "patterns": [r"doctor", r"\bgp\b", r"endocrin", r"what should i ask", r"appointment"],
        "risk": "low",
        "response_hint": "Generate clinician handoff questions",
    },
    {
        "id": "symptom_seeking",
        "patterns": [r"pcos", r"brain fog", r"tired", r"insulin", r"testosterone", r"period", r"cycle"],
        "risk": "med",
        "response_hint": "Structure symptoms against labs and layers — not diagnosis",
    },
    {
        "id": "care_gap",
        "patterns": [r"why no one", r"dismissed", r"years to diagnose", r"ignored"],
        "risk": "med",
        "response_hint": "Surface care gaps with traceable evidence",
    },
]


def detect_patient_intent(message: str, profile: dict[str, Any]) -> dict[str, Any]:
    text = (message or "").strip()
    if not text:
        return {
            "tool": "detect_patient_intent",
            "intent": "general",
            "risk_level": "low",
            "evidence": ["No message provided"],
            "suggested_route": "full_cycle",
            "confidence": 0.5,
        }

    lowered = text.lower()
    matched = []
    for rule in INTENT_RULES:
        if any(re.search(p, lowered) for p in rule["patterns"]):
            matched.append(rule)

    if not matched:
        return {
            "tool": "detect_patient_intent",
            "intent": "general",
            "risk_level": "low",
            "raw_query": text,
            "evidence": [f"Query: {text[:120]}"],
            "suggested_route": "full_cycle",
            "confidence": 0.6,
        }

    primary = matched[0]
    if any(r["id"] == "supplement_self_treatment" for r in matched):
        primary = next(r for r in matched if r["id"] == "supplement_self_treatment")

    route = "full_cycle"
    if primary["id"] == "clinician_prep":
        route = "clinician_handoff"
    elif primary["id"] == "trial_interest":
        route = "trial_search"

    return {
        "tool": "detect_patient_intent",
        "intent": primary["id"],
        "risk_level": primary["risk"],
        "raw_query": text,
        "evidence": [f"Matched intent: {primary['id']}", primary["response_hint"]],
        "suggested_route": route,
        "confidence": 0.88,
    }
