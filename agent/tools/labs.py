"""Lab parsing and care-gap scoring."""

from __future__ import annotations

from typing import Any

ROOT_MARKERS = {
    "LH:FSH ratio": {"high": 2.0, "direction": "above"},
    "HOMA-IR (calculated)": {"high": 2.0, "direction": "above"},
    "Fasting glucose": {"high": 5.5, "direction": "above"},
    "Total testosterone": {"high": 2.1, "direction": "above"},
    "Vitamin D (25-OH)": {"low": 75, "direction": "below"},
    "Ferritin": {"low": 30, "direction": "below"},
    "LDL cholesterol": {"high": 3.0, "direction": "above"},
}


def flatten_panel(panel: dict[str, Any]) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    for section in panel.get("sections", []):
        for test in section.get("tests", []):
            markers.append(
                {
                    "name": test["name"],
                    "value": test["value"],
                    "unit": test.get("unit", ""),
                    "flag": test.get("flag", "ok"),
                    "note": test.get("note", ""),
                }
            )
    return markers


def marker_map(markers: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {m["name"]: m for m in markers}


def parse_lab_panel(panel: dict[str, Any]) -> dict[str, Any]:
    markers = flatten_panel(panel)
    by_name = marker_map(markers)
    evidence: list[str] = []

    pattern_parts: list[str] = []
    if by_name.get("LH:FSH ratio", {}).get("flag") == "high":
        evidence.append("LH:FSH ratio elevated — androgen/PCOS-associated pattern")
        pattern_parts.append("elevated androgen pattern")
    if by_name.get("HOMA-IR (calculated)", {}).get("flag") == "high":
        evidence.append("HOMA-IR elevated — insulin resistance signal")
        pattern_parts.append("insulin resistance")
    if by_name.get("Progesterone", {}).get("flag") == "low":
        evidence.append("Low progesterone — likely anovulatory cycle")
    if by_name.get("Vitamin D (25-OH)", {}).get("flag") == "low":
        evidence.append("Vitamin D insufficient")

    summary = panel.get("summary", {})
    pattern = summary.get("pattern") or " · ".join(pattern_parts) or "mixed endocrine-metabolic pattern"

    return {
        "tool": "parse_lab_panel",
        "markers": markers,
        "marker_count": len(markers),
        "pattern": pattern,
        "highlights": summary.get("highlights", []),
        "evidence": evidence,
        "confidence": 0.85 if evidence else 0.5,
    }


def score_care_gaps(markers: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    by_name = marker_map(markers)
    gaps: list[dict[str, Any]] = []

    def add(gap_id: str, name: str, level: str, pct: int, note: str, evidence: list[str], layers: list[str]):
        gaps.append(
            {
                "id": gap_id,
                "name": name,
                "level": level,
                "score": pct,
                "note": note,
                "evidence": evidence,
                "layers": layers,
                "status": "open",
            }
        )

    if (
        by_name.get("HOMA-IR (calculated)", {}).get("flag") == "high"
        or by_name.get("Fasting glucose", {}).get("flag") == "high"
    ):
        add(
            "insulin_resistance",
            "Insulin resistance",
            "high",
            82,
            "Glucose and insulin pattern — food-first intervention priority",
            [
                f"HOMA-IR {by_name.get('HOMA-IR (calculated)', {}).get('value', '?')}",
                f"Glucose {by_name.get('Fasting glucose', {}).get('value', '?')} mmol/L",
            ],
            ["metabolic", "hormones"],
        )

    if by_name.get("LDL cholesterol", {}).get("flag") in {"high", "low"} or by_name.get("HDL cholesterol", {}).get("flag") == "low":
        add(
            "cardiovascular",
            "Cardiovascular lipid risk",
            "med",
            58,
            "LDL/HDL pattern — omega-3 food focus and repeat lipids",
            [
                f"LDL {by_name.get('LDL cholesterol', {}).get('value', '?')}",
                f"HDL {by_name.get('HDL cholesterol', {}).get('value', '?')}",
            ],
            ["metabolic"],
        )

    if by_name.get("Vitamin D (25-OH)", {}).get("flag") == "low":
        add(
            "vitamin_d",
            "Vitamin D insufficiency",
            "med",
            64,
            "Affects insulin sensitivity, mood, and bone layer",
            [f"Vitamin D {by_name.get('Vitamin D (25-OH)', {}).get('value', '?')} nmol/L"],
            ["cognition", "metabolic", "hormones"],
        )

    if by_name.get("Ferritin", {}).get("flag") in {"low", "high"} or float(by_name.get("Ferritin", {}).get("value", 99)) < 30:
        add(
            "iron_fatigue",
            "Iron-related fatigue risk",
            "med",
            41,
            "Low ferritin can amplify brain fog alongside hormonal flux",
            [f"Ferritin {by_name.get('Ferritin', {}).get('value', '?')} µg/L"],
            ["cognition"],
        )

    if by_name.get("LH:FSH ratio", {}).get("flag") == "high":
        add(
            "androgen_excess",
            "Androgen excess pattern",
            "high",
            76,
            "Discuss endocrine evaluation — not a diagnosis",
            [
                f"LH:FSH {by_name.get('LH:FSH ratio', {}).get('value', '?')}",
                f"Testosterone {by_name.get('Total testosterone', {}).get('value', '?')} nmol/L",
            ],
            ["hormones"],
        )

    if by_name.get("TSH", {}).get("flag") != "ok":
        add(
            "thyroid",
            "Thyroid dysfunction signal",
            "med",
            55,
            "Thyroid markers warrant clinical follow-up",
            [f"TSH {by_name.get('TSH', {}).get('value', '?')}"],
            ["hormones", "cognition"],
        )

    gaps.sort(key=lambda g: g["score"], reverse=True)
    return {
        "tool": "score_care_gaps",
        "gaps": gaps,
        "evidence": [e for g in gaps for e in g["evidence"]],
        "confidence": 0.8 if gaps else 0.4,
    }


def score_layer_health(markers: list[dict[str, Any]], wearable: dict[str, Any], daily_log: dict[str, Any]) -> dict[str, Any]:
    by_name = marker_map(markers)
    layers: dict[str, dict[str, Any]] = {}

    def layer(layer_id: str, label: str, score: int, signals: list[str], status: str):
        layers[layer_id] = {
            "id": layer_id,
            "label": label,
            "score": score,
            "signals": signals,
            "status": status,
        }

    hormone_hits = sum(
        1
        for k in ("LH:FSH ratio", "Total testosterone", "Progesterone", "SHBG")
        if by_name.get(k, {}).get("flag") != "ok"
    )
    hormone_score = max(25, 100 - hormone_hits * 18)
    layer(
        "hormones",
        "Hormones & endocrine",
        hormone_score,
        [s for s in [
            "LH:FSH elevated" if by_name.get("LH:FSH ratio", {}).get("flag") == "high" else None,
            "Androgen excess" if by_name.get("Total testosterone", {}).get("flag") == "high" else None,
            "Anovulation signal" if by_name.get("Progesterone", {}).get("flag") == "low" else None,
        ] if s],
        "attention" if hormone_score < 60 else "stable",
    )

    metabolic_hits = sum(
        1
        for k in ("HOMA-IR (calculated)", "Fasting glucose", "LDL cholesterol", "Triglycerides")
        if by_name.get(k, {}).get("flag") != "ok"
    )
    metabolic_score = max(20, 100 - metabolic_hits * 16)
    layer(
        "metabolic",
        "Metabolic & cardiovascular",
        metabolic_score,
        [f"HOMA-IR {by_name.get('HOMA-IR (calculated)', {}).get('value', '?')}"],
        "priority" if metabolic_score < 55 else "monitor",
    )

    cognition_score = 72
    cognition_signals: list[str] = []
    if wearable.get("sleep_hours", 8) < 6:
        cognition_score -= 15
        cognition_signals.append(f"Sleep {wearable.get('sleep_hours')}h · fragmented")
    if daily_log.get("mood", 3) <= 2:
        cognition_score -= 10
        cognition_signals.append("Low mood check-in")
    if by_name.get("Vitamin D (25-OH)", {}).get("flag") == "low":
        cognition_score -= 8
        cognition_signals.append("Vitamin D insufficient")
    if float(by_name.get("Ferritin", {}).get("value", 50)) < 30:
        cognition_score -= 8
        cognition_signals.append("Ferritin low-normal")
    layer("cognition", "Cognition & recovery", max(20, cognition_score), cognition_signals, "support" if cognition_score < 65 else "stable")

    infl_score = 78
    infl_signals: list[str] = []
    if daily_log.get("inflammation") in {"mild", "noticeable"}:
        infl_score -= 12 if daily_log["inflammation"] == "mild" else 24
        infl_signals.append(f"Inflammation logged · {daily_log['inflammation']}")
    if daily_log.get("food_triggers"):
        infl_score -= 10
        infl_signals.append("Trigger foods logged today")
    crp = by_name.get("CRP", {}).get("value")
    if crp is not None and float(crp) > 3:
        infl_signals.append(f"CRP {crp} mg/L")
    layer("inflammation", "Inflammation & gut", max(25, infl_score), infl_signals, "calm" if infl_score >= 70 else "reduce")

    return {
        "tool": "score_layer_health",
        "layers": layers,
        "evidence": [sig for l in layers.values() for sig in l["signals"]],
        "confidence": 0.82,
    }
