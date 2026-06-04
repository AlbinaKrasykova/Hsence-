#!/usr/bin/env python3
"""Quick test for Hsence precision agent + planner."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.orchestrator import run_agent


def main():
    r = run_agent(
        "full_cycle",
        {
            "chat_message": "Should I take berberine for PCOS?",
            "daily_log": {"mood": 2, "inflammation": "mild"},
        },
    )
    plan = r["plan"]
    print("OK · tools planned:", len(plan["tools"]))
    print("  planner:", " → ".join(plan["tools"]))
    print("  intent:", r["intent"].get("intent"))
    print("  trials:", len(r.get("trials", [])))
    print("  doctor Qs:", len(r.get("clinician_handoff", {}).get("questions_for_doctor", [])))
    print("  guidelines:", len(r.get("guidelines", [])))
    print("  trace steps:", len(r["trace"]))


if __name__ == "__main__":
    main()
