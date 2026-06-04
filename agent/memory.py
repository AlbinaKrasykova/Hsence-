import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = ROOT / "data" / "patient-memory.json"

DEFAULT_MEMORY: dict[str, Any] = {
    "profile": {
        "name": "Maya Chen",
        "sex": "F",
        "age": 34,
        "goals": ["understand hormonal pattern", "personal nutrition plan"],
    },
    "labs": {"panel_id": "maya-chen", "latest": None},
    "wearable": {
        "hrv_delta": 0.08,
        "sleep_hours": 5.7,
        "sleep_fragmented": True,
        "readiness": 74,
    },
    "daily_log": {
        "mood": 3,
        "inflammation": "mild",
        "food_triggers": [],
        "supplements_taken": [],
    },
    "layer_scores": {},
    "care_gaps": [],
    "precision_plan": {"foods": [], "supplements": [], "lifestyle": [], "meals": []},
    "intent": {},
    "guidelines": [],
    "clinician_handoff": {},
    "trials": [],
    "agent_trace": [],
}


def load_memory() -> dict[str, Any]:
    if MEMORY_PATH.exists():
        with MEMORY_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return deepcopy(DEFAULT_MEMORY)


def save_memory(memory: dict[str, Any]) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def append_trace(memory: dict[str, Any], entry: dict[str, Any]) -> None:
    trace = memory.setdefault("agent_trace", [])
    trace.append(entry)
    memory["agent_trace"] = trace[-20:]
