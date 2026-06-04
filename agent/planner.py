"""Autonomous tool planner — selects tools based on event, intent, and memory."""

from __future__ import annotations

from typing import Any

# Tool registry metadata for explainability in UI / trace
TOOL_CATALOG: dict[str, str] = {
    "detect_patient_intent": "Classify patient message — supplement risk, symptoms, trial interest",
    "parse_lab_panel": "Normalize lab markers and extract endocrine-metabolic pattern",
    "score_care_gaps": "Rank cross-layer care gaps with evidence",
    "score_layer_health": "Score hormones · metabolic · cognition · inflammation layers",
    "retrieve_guideline_snippet": "Pull evidence snippets for matched patterns",
    "recommend_precision_nutrition": "Match meals, food rules, supplements, lifestyle",
    "generate_clinician_handoff": "Build GP questions and visit summary bullets",
    "match_clinical_trials": "Surface eligible trials with rationale (demo mock)",
    "safety_guardrail": "Block diagnosis language and attach disclaimer",
}


def build_plan(
    event_type: str,
    memory: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Return ordered tool list plus human-readable planning rationale."""
    chat = (payload.get("chat_message") or memory.get("intent", {}).get("raw_query") or "").strip()
    has_labs = bool(payload.get("panel") or memory.get("labs", {}).get("latest"))
    gap_ids = {g["id"] for g in memory.get("care_gaps", [])}
    reasoning: list[str] = []
    tools: list[str] = []

    if event_type == "chat" and chat:
        tools.append("detect_patient_intent")
        reasoning.append("Patient message detected — classify intent before acting")
        intent_preview = _preview_intent(chat)
        if intent_preview in {"supplement_self_treatment", "symptom_seeking", "care_gap"}:
            tools.extend(["retrieve_guideline_snippet", "safety_guardrail"])
            reasoning.append("High-stakes intent — add guideline context and safety first")
        if intent_preview in {"symptom_seeking", "care_gap", "trial_interest"} and has_labs:
            tools.extend(_analysis_tools(memory, gap_ids, reasoning))
        return _plan_result(event_type, tools, reasoning)

    if event_type == "daily_log":
        tools.append("score_layer_health")
        reasoning.append("Daily log update — re-score interrelated layers")
        if memory.get("care_gaps") or has_labs:
            tools.append("recommend_precision_nutrition")
            reasoning.append("Refresh precision nutrition from updated daily signals")
        if payload.get("daily_log", {}).get("inflammation") in {"mild", "noticeable"}:
            tools.insert(-1 if "recommend_precision_nutrition" in tools else len(tools), "retrieve_guideline_snippet")
            reasoning.append("Inflammation logged — add anti-inflammatory guideline context")
        tools.append("safety_guardrail")
        return _plan_result(event_type, tools, reasoning)

    if event_type == "clinician_handoff":
        tools.extend(["generate_clinician_handoff", "safety_guardrail"])
        reasoning.append("User requested clinician handoff — skip re-parse, generate visit prep")
        if not memory.get("care_gaps"):
            tools.insert(0, "parse_lab_panel")
            tools.insert(1, "score_care_gaps")
            reasoning.insert(0, "No care gaps in memory — parse labs first")
        return _plan_result(event_type, tools, reasoning)

    if event_type == "trial_search":
        tools.extend(_analysis_tools(memory, gap_ids, reasoning, include_trials=True))
        return _plan_result(event_type, tools, reasoning)

    # full_cycle (default)
    if chat:
        tools.append("detect_patient_intent")
        reasoning.append("Include patient front-door intent in full multimodal cycle")
    tools.extend(_analysis_tools(memory, gap_ids, reasoning, include_trials=True))
    return _plan_result(event_type, tools, reasoning)


def _analysis_tools(
    memory: dict[str, Any],
    gap_ids: set[str],
    reasoning: list[str],
    *,
    include_trials: bool = False,
) -> list[str]:
    tools = [
        "parse_lab_panel",
        "score_care_gaps",
        "score_layer_health",
        "retrieve_guideline_snippet",
        "recommend_precision_nutrition",
    ]
    reasoning.extend([
        "Multimodal cycle — labs drive gaps, layers, and nutrition",
        "Attach guideline snippets for explainable recommendations",
    ])
    if include_trials and (
        gap_ids.intersection({"insulin_resistance", "androgen_excess"})
        or "insulin_resistance" in gap_ids
        or not gap_ids
    ):
        tools.append("match_clinical_trials")
        reasoning.append("Metabolic/hormone gaps — check trial eligibility (Pfizer care gap)")
    tools.extend(["generate_clinician_handoff", "safety_guardrail"])
    reasoning.append("Prepare clinician handoff and run safety guardrail")
    return tools


def _preview_intent(chat: str) -> str:
    lowered = chat.lower()
    if any(w in lowered for w in ("trial", "study", "enroll", "clinical trial")):
        return "trial_interest"
    if any(w in lowered for w in ("berberine", "supplement", "should i take", "metformin dose")):
        return "supplement_self_treatment"
    if any(w in lowered for w in ("doctor", "gp", "endocrin", "what should i ask")):
        return "clinician_prep"
    if any(w in lowered for w in ("pcos", "tired", "fog", "insulin", "testosterone")):
        return "symptom_seeking"
    return "general"


def _plan_result(event_type: str, tools: list[str], reasoning: list[str]) -> dict[str, Any]:
    # Deduplicate while preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for t in tools:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
    return {
        "tool": "agent_planner",
        "event_type": event_type,
        "tools": ordered,
        "reasoning": reasoning,
        "tool_descriptions": {t: TOOL_CATALOG.get(t, t) for t in ordered},
        "confidence": 0.9,
    }
