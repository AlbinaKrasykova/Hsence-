"""Safety guardrails for clinical-adjacent agent outputs."""

FORBIDDEN_PHRASES = [
    "you have pcos",
    "you have diabetes",
    "diagnosis:",
    "take metformin 500mg",
    "prescribe",
]

DISCLAIMER = (
    "Not a diagnosis or prescription. Hsence provides precision lifestyle and nutrition "
    "guidance for awareness and clinician conversation."
)


def apply_guardrails(text: str) -> dict:
    lowered = text.lower()
    flags = [p for p in FORBIDDEN_PHRASES if p in lowered]
    safe_text = text
    for phrase in flags:
        safe_text = safe_text.replace(phrase, "pattern consistent with clinical evaluation")
    return {
        "tool": "safety_guardrail",
        "passed": len(flags) == 0,
        "flags": flags,
        "disclaimer": DISCLAIMER,
        "text": safe_text,
    }
