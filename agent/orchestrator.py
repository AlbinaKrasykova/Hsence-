"""Agent orchestrator — planner, tool use, memory, adapt."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from agent.guardrails import DISCLAIMER, apply_guardrails
from agent.memory import append_trace, load_memory, save_memory
from agent.planner import build_plan
from agent.tools.clinician import generate_clinician_handoff
from agent.tools.guidelines import retrieve_guideline_snippet
from agent.tools.intent import detect_patient_intent
from agent.tools.labs import flatten_panel, parse_lab_panel, score_care_gaps, score_layer_health
from agent.tools.nutrition import recommend_precision_nutrition
from agent.tools.trials import match_clinical_trials

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "data" / "fake-lab-panel.json"


def load_panel(panel_id: str | None = None) -> dict[str, Any]:
    with PANEL_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def synthesize_summary(
    pattern: str,
    layers: dict[str, dict[str, Any]],
    gaps: list[dict[str, Any]],
    plan: dict[str, Any],
    intent: dict[str, Any] | None = None,
) -> str:
    top_gap = gaps[0]["name"] if gaps else "general endocrine-metabolic optimisation"
    weak_layers = [l["label"] for l in layers.values() if l.get("score", 100) < 65]
    layer_text = ", ".join(weak_layers[:2]) if weak_layers else "balanced across layers"
    meal = plan.get("meals", [{}])[0].get("name", "protein-forward meals") if plan.get("meals") else "protein-forward meals"
    intent_note = ""
    if intent and intent.get("intent") == "supplement_self_treatment":
        intent_note = " I won't recommend starting supplements from a search query alone — here's what your data supports for clinician discussion."
    return (
        f"Precision read: {pattern}. Priority attention on {top_gap}. "
        f"Interrelated layers needing support: {layer_text}. "
        f"Today's food anchor: {meal}. "
        f"Matched {len(plan.get('supplements', []))} supplements and {len(plan.get('foods', []))} nutrition rules to your biology.{intent_note}"
    )


def run_agent(
    event_type: str = "full_cycle",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = payload or {}
    started = time.time()
    memory = load_memory()

    if payload.get("profile"):
        memory["profile"].update(payload["profile"])
    if payload.get("wearable"):
        memory["wearable"].update(payload["wearable"])
    if payload.get("daily_log"):
        memory["daily_log"].update(payload["daily_log"])
    if payload.get("chat_message"):
        memory.setdefault("intent", {})["raw_query"] = payload["chat_message"]

    panel = payload.get("panel") or load_panel(payload.get("panel_id"))
    markers: list[dict[str, Any]] = []

    plan_result = build_plan(event_type, memory, payload)
    tools_plan: list[str] = plan_result["tools"]
    trace: list[dict[str, Any]] = [plan_result]

    parsed: dict[str, Any] = {}
    intent_result: dict[str, Any] = memory.get("intent", {})
    guidelines_result: dict[str, Any] = {"guidelines": memory.get("guidelines", [])}
    handoff_result: dict[str, Any] = memory.get("clinician_handoff", {})
    trials_result: dict[str, Any] = {"trials": memory.get("trials", [])}

    final_summary = ""
    guard = None

    for tool_name in tools_plan:
        t0 = time.time()
        ms = lambda: int((time.time() - t0) * 1000)

        if tool_name == "detect_patient_intent":
            intent_result = detect_patient_intent(
                payload.get("chat_message") or memory.get("intent", {}).get("raw_query", ""),
                memory["profile"],
            )
            memory["intent"] = intent_result
            trace.append({**intent_result, "duration_ms": ms()})

        elif tool_name == "parse_lab_panel":
            parsed = parse_lab_panel(panel)
            markers = parsed["markers"]
            memory.setdefault("labs", {})["latest"] = {
                "pattern": parsed["pattern"],
                "marker_count": parsed["marker_count"],
            }
            trace.append({**parsed, "duration_ms": ms()})

        elif tool_name == "score_care_gaps":
            if not markers:
                markers = flatten_panel(panel)
            gaps_result = score_care_gaps(markers, memory["profile"])
            memory["care_gaps"] = gaps_result["gaps"]
            trace.append({**gaps_result, "duration_ms": ms()})

        elif tool_name == "score_layer_health":
            if not markers:
                markers = flatten_panel(panel)
            if not memory.get("care_gaps") and markers:
                gaps_result = score_care_gaps(markers, memory["profile"])
                memory["care_gaps"] = gaps_result["gaps"]
            layers_result = score_layer_health(markers, memory["wearable"], memory["daily_log"])
            memory["layer_scores"] = layers_result["layers"]
            trace.append({**layers_result, "duration_ms": ms()})

        elif tool_name == "retrieve_guideline_snippet":
            guidelines_result = retrieve_guideline_snippet(
                memory.get("care_gaps", []),
                memory.get("layer_scores", {}),
            )
            memory["guidelines"] = guidelines_result["guidelines"]
            trace.append({**guidelines_result, "duration_ms": ms()})

        elif tool_name == "recommend_precision_nutrition":
            nutrition_result = recommend_precision_nutrition(
                memory.get("care_gaps", []),
                memory.get("layer_scores", {}),
                memory["daily_log"],
                memory["profile"],
            )
            memory["precision_plan"] = {
                "foods": nutrition_result["foods"],
                "meals": nutrition_result["meals"],
                "supplements": nutrition_result["supplements"],
                "lifestyle": nutrition_result["lifestyle"],
            }
            trace.append({**nutrition_result, "duration_ms": ms()})

        elif tool_name == "generate_clinician_handoff":
            pattern = (
                parsed.get("pattern")
                or memory.get("labs", {}).get("latest", {}).get("pattern")
                or "endocrine-metabolic pattern"
            )
            handoff_result = generate_clinician_handoff(
                memory.get("care_gaps", []),
                memory.get("layer_scores", {}),
                pattern,
                memory["profile"],
                memory.get("precision_plan", {}),
            )
            memory["clinician_handoff"] = handoff_result
            trace.append({**handoff_result, "duration_ms": ms()})

        elif tool_name == "match_clinical_trials":
            trials_result = match_clinical_trials(memory.get("care_gaps", []), memory["profile"])
            memory["trials"] = trials_result["trials"]
            trace.append({**trials_result, "duration_ms": ms()})

        elif tool_name == "safety_guardrail":
            pattern = (
                parsed.get("pattern")
                or memory.get("labs", {}).get("latest", {}).get("pattern")
                or "endocrine-metabolic pattern"
            )
            summary = synthesize_summary(
                pattern,
                memory.get("layer_scores", {}),
                memory.get("care_gaps", []),
                memory.get("precision_plan", {}),
                intent_result,
            )
            guard = apply_guardrails(summary)
            final_summary = guard["text"]
            trace.append({**guard, "duration_ms": ms()})
        else:
            trace.append({"tool": tool_name, "skipped": True, "duration_ms": ms()})

    pattern = (
        parsed.get("pattern")
        or memory.get("labs", {}).get("latest", {}).get("pattern")
        or "endocrine-metabolic pattern"
    )
    if not final_summary:
        raw = synthesize_summary(
            pattern,
            memory.get("layer_scores", {}),
            memory.get("care_gaps", []),
            memory.get("precision_plan", {}),
            intent_result,
        )
        guard = apply_guardrails(raw)
        final_summary = guard["text"]
        trace.append(guard)

    cycle = {
        "event_type": event_type,
        "plan": plan_result,
        "tools_run": tools_plan,
        "duration_ms": int((time.time() - started) * 1000),
        "trace": trace,
    }
    append_trace(memory, cycle)
    save_memory(memory)

    return {
        "summary": final_summary,
        "pattern": pattern,
        "plan": plan_result,
        "intent": intent_result,
        "layers": memory.get("layer_scores", {}),
        "care_gaps": memory.get("care_gaps", []),
        "precision_plan": memory.get("precision_plan", {}),
        "guidelines": memory.get("guidelines", []),
        "clinician_handoff": memory.get("clinician_handoff", {}),
        "trials": memory.get("trials", []),
        "profile": memory.get("profile", {}),
        "wearable": memory.get("wearable", {}),
        "daily_log": memory.get("daily_log", {}),
        "trace": trace,
        "disclaimer": DISCLAIMER,
        "cycle": cycle,
    }
