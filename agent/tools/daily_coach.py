"""Daily ritual agent — answers questions using lab memory and current log context."""

from __future__ import annotations

import re
from typing import Any

STEP_HINTS = {
    "mood": "Step 1 · feelings — mood connects to sleep, HRV, and cognition layer.",
    "supp": "Step 2 · supplements — matched to your PCOS pattern and care gaps.",
    "food": "Step 3 · food — low-GI and protein-forward rules for insulin resistance.",
    "infl": "Step 4 · inflammation — correlates with food triggers and recovery.",
    "voice": "Step 5 · voice — speak freely; we map speech to cognition signals.",
    "general": "Daily ritual — log only what you want; agent uses your labs as context.",
}

QUICK_BY_STEP = {
    "mood": [
        "Why do I feel foggy if my labs are borderline?",
        "Does poor sleep affect my hormone labs?",
        "What should I tell my doctor about mood?",
    ],
    "supp": [
        "Should I take myo-inositol today?",
        "Is berberine safe with my labs?",
        "Which supplements match my PCOS pattern?",
    ],
    "food": [
        "What should I eat for insulin resistance?",
        "Are oats okay for PCOS?",
        "Why avoid dairy today?",
    ],
    "infl": [
        "What causes inflammation with PCOS?",
        "Does food trigger my symptoms?",
        "When should I see my doctor?",
    ],
    "voice": [
        "I have brain fog and I'm tired",
        "I didn't sleep well last night",
        "Explain my cognition layer score",
    ],
    "general": [
        "What do my labs mean together?",
        "What is my biggest care gap?",
        "Summarize my hormone pattern",
    ],
}


def answer_daily_question(
    message: str,
    step: str = "general",
    daily_log: dict[str, Any] | None = None,
    memory: dict[str, Any] | None = None,
) -> dict[str, Any]:
    memory = memory or {}
    daily_log = daily_log or {}
    text = (message or "").strip()
    step = step if step in STEP_HINTS else "general"
    pattern = (memory.get("labs") or {}).get("latest", {}).get("pattern") or "endocrine-metabolic pattern"
    layers = memory.get("layer_scores") or {}
    gaps = memory.get("care_gaps") or []
    cognition = layers.get("cognition", {})
    metabolic = layers.get("metabolic", {})
    hormones = layers.get("hormones", {})

    if not text:
        return _empty_prompt(step, pattern, gaps)

    lowered = text.lower()
    suggestions: list[dict[str, Any]] = []
    cognition_signals: list[str] = []

    if any(w in lowered for w in ("fog", "foggy", "brain", "focus", "memory")):
        cognition_signals.append("Brain fog · daily check-in")
        suggestions.append({"field": "mood", "value": 2, "label": "Log low mood (2/5)"})
        answer = (
            f"Brain fog often tracks with sleep fragmentation and insulin resistance — both show up in your pattern "
            f"({pattern}). Your cognition layer is at {cognition.get('score', '—')}/100. "
            f"Prioritise protein breakfast, steady glucose, and discuss formal PCOS evaluation with your clinician."
        )
    elif any(w in lowered for w in ("berberine", "supplement", "inositol", "metformin", "nac", "spearmint")):
        if "berberine" in lowered:
            answer = (
                "Berberine has limited PCOS evidence compared with myo-inositol and lifestyle-first care. "
                f"Given your pattern ({pattern}) and insulin resistance gap, standard care discussion "
                "(metformin, inositol ★) belongs with your GP — not self-starting from search."
            )
            suggestions.append({"field": "supp", "value": "inositol", "label": "Log myo-inositol (★ evidence)"})
        elif "inositol" in lowered:
            answer = (
                "Myo-inositol (40:1) has strong PCOS evidence for insulin and androgen balance. "
                f"It fits your {pattern}. Tap it in step 2 if you took it today."
            )
            suggestions.append({"field": "supp", "value": "inositol", "label": "Select myo-inositol AM"})
        else:
            answer = (
                f"Your supplement plan is graded to {pattern}. "
                f"★ myo-inositol · ◈ NAC, magnesium, D3+K2, spearmint — always confirm with your clinician."
            )
    elif any(w in lowered for w in ("eat", "food", "meal", "dairy", "oats", "breakfast", "dinner", "lunch")):
        triggers = daily_log.get("food_triggers") or daily_log.get("foodCats") or []
        answer = (
            f"For insulin resistance in {pattern}: protein + fibre each meal, low-GI carbs, omega-3 fish 2–3×/week. "
            f"Limit high-GI carbs and dairy if symptoms spike."
        )
        if "dairy" in lowered:
            answer += " Dairy can worsen androgen and inflammation signals in some PCOS profiles."
        if "oats" in lowered:
            answer += " Oats + flax + cinnamon can work if paired with protein — avoid sugary add-ons."
            suggestions.append({"field": "meal", "value": "oats", "label": "Select oats + flax meal"})
        if triggers:
            answer += f" You logged triggers today: {', '.join(triggers)}."
    elif any(w in lowered for w in ("lab", "labs", "lh", "fsh", "testosterone", "homa", "insulin", "borderline", "pattern")):
        answer = (
            f"Your lab read: {pattern}. Key flags: LH:FSH ratio elevated, androgen excess, HOMA-IR suggesting insulin resistance, "
            f"suboptimal vitamin D. These connect across hormones + metabolic layers — not isolated 'borderline' results."
        )
    elif any(w in lowered for w in ("gap", "care gap", "doctor", "gp", "appointment", "follow")):
        top = gaps[0]["name"] if gaps else "insulin resistance discussion"
        answer = (
            f"Top care gap: {top}. "
            f"Ask your clinician: 'Given my LH:FSH, testosterone, and HOMA-IR, should we formally evaluate PCOS "
            f"and discuss metformin or inositol?'"
        )
    elif any(w in lowered for w in ("inflammation", "bloat", "joint", "flare", "skin")):
        infl = daily_log.get("inflammation") or daily_log.get("infl") or "none"
        answer = (
            f"Inflammation links food triggers, recovery, and PCOS metabolic load. "
            f"You logged inflammation as '{infl}'. Anti-inflammatory plates: oily fish, greens, turmeric, berries."
        )
        if infl in ("mild", "noticeable"):
            suggestions.append({"field": "infl", "value": infl, "label": f"Keep inflammation: {infl}"})
    elif any(w in lowered for w in ("sleep", "tired", "fatigue", "exhausted", "hrv")):
        cognition_signals.append("Fatigue · daily check-in")
        wear = memory.get("wearable") or {}
        answer = (
            f"Your wearable shows {wear.get('sleep_hours', '—')}h sleep"
            f"{' · fragmented' if wear.get('sleep_fragmented') else ''}. "
            f"Short sleep lowers cognition layer scores and worsens insulin sensitivity — log mood honestly in step 1."
        )
        suggestions.append({"field": "mood", "value": 2, "label": "Log tired mood"})
    elif any(w in lowered for w in ("cognition", "layer", "score")):
        answer = (
            f"Cognition layer: {cognition.get('score', '—')}/100 · {cognition.get('status', 'monitor')}. "
            f"Signals: {', '.join(cognition.get('signals') or ['sleep', 'mood', 'vitamin D'])}. "
            f"Metabolic layer: {metabolic.get('score', '—')}/100. Hormones: {hormones.get('score', '—')}/100."
        )
    elif any(w in lowered for w in ("summar", "overall", "today", "help")):
        answer = _daily_summary(pattern, layers, gaps, daily_log)
    else:
        answer = (
            f"I read your question against {pattern}. "
            f"{STEP_HINTS[step]} "
            f"For PCOS + insulin resistance, focus on mood/sleep signals, ★ inositol, low-GI food, and clinician follow-up. "
            f"Ask about labs, supplements, food, fog, or care gaps."
        )

    return {
        "tool": "daily_ritual_agent",
        "answer": answer,
        "step": step,
        "lab_context": pattern,
        "layers": {
            "cognition": cognition.get("score"),
            "metabolic": metabolic.get("score"),
            "hormones": hormones.get("score"),
        },
        "top_care_gap": gaps[0]["name"] if gaps else None,
        "suggestions": suggestions,
        "cognition_signals": cognition_signals,
        "quick_replies": QUICK_BY_STEP.get(step, QUICK_BY_STEP["general"])[:3],
        "confidence": 0.85,
    }


def _empty_prompt(step: str, pattern: str, gaps: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "tool": "daily_ritual_agent",
        "answer": (
            f"Hi — I'm your daily ritual agent. I use your labs ({pattern}) to answer questions. "
            f"{STEP_HINTS.get(step, STEP_HINTS['general'])} "
            f"Ask anything about mood, supplements, food, inflammation, or your lab pattern."
        ),
        "step": step,
        "lab_context": pattern,
        "top_care_gap": gaps[0]["name"] if gaps else None,
        "suggestions": [],
        "cognition_signals": [],
        "quick_replies": QUICK_BY_STEP.get(step, QUICK_BY_STEP["general"]),
        "confidence": 0.9,
    }


def _daily_summary(
    pattern: str,
    layers: dict[str, Any],
    gaps: list[dict[str, Any]],
    daily_log: dict[str, Any],
) -> str:
    gap_text = gaps[0]["name"] if gaps else "follow-up with clinician"
    mood = daily_log.get("mood")
    mood_note = f"Mood today: {mood}/5. " if mood else ""
    return (
        f"{mood_note}Pattern: {pattern}. "
        f"Cognition {layers.get('cognition', {}).get('score', '—')}/100 · "
        f"Metabolic {layers.get('metabolic', {}).get('score', '—')}/100. "
        f"Priority gap: {gap_text}. Log gently — no streaks required."
    )


def parse_voice_for_cognition(transcript: str) -> dict[str, Any]:
    """Lightweight voice → cognition signal parse for daily ritual."""
    text = (transcript or "").strip().lower()
    signals: list[str] = []
    impact = 0
    rules = [
        (r"brain fog|foggy|can't focus", "Brain fog · voice", 12),
        (r"tired|exhausted|fatigue|no energy", "Fatigue · voice", 10),
        (r"didn't sleep|insomnia|poor sleep", "Sleep disruption · voice", 10),
        (r"anxious|stressed|overwhelmed", "Stress load · voice", 8),
        (r"sad|low mood|hopeless", "Low mood · voice", 10),
    ]
    for pattern, signal, delta in rules:
        if re.search(pattern, text):
            signals.append(signal)
            impact += delta
    inferred_mood = 2 if any(re.search(r"sad|low mood|hopeless|foggy|tired", text) for _ in [0]) else None
    return {
        "transcript": transcript[:500],
        "cognition_signals": signals,
        "cognition_impact": min(impact, 35),
        "inferred_mood": inferred_mood,
    }


RITUAL_PHASES = ["mood", "supp", "food", "infl", "open", "done"]

SUPP_ALIASES: dict[str, str] = {
    "inositol": "inositol",
    "myo-inositol": "inositol",
    "myo inositol": "inositol",
    "magnesium": "mag",
    "mag": "mag",
    "vitamin d": "d3",
    "d3": "d3",
    "d 3": "d3",
    "nac": "nac",
    "spearmint": "spearmint",
}

FOOD_CAT_ALIASES: dict[str, str] = {
    "dairy": "dairy",
    "milk": "dairy",
    "cheese": "dairy",
    "sugar": "high-gi",
    "pasta": "high-gi",
    "white bread": "high-gi",
    "processed": "processed",
    "junk food": "processed",
    "alcohol": "alcohol",
    "wine": "alcohol",
    "beer": "alcohol",
    "salmon": "omega3",
    "fish": "omega3",
    "greens": "greens",
    "spinach": "greens",
    "protein": "protein",
    "chicken": "protein",
    "eggs": "protein",
}

MEAL_ALIASES: dict[str, str] = {
    "oats": "oats",
    "oatmeal": "oats",
    "eggs": "eggs",
    "salmon": "salmon",
    "lentil": "lentil",
    "smoothie": "smoothie",
    "tofu": "tofu-bowl",
    "chicken": "chicken-avocado",
}


def _profile_name(memory: dict[str, Any]) -> str:
    return (memory.get("profile") or {}).get("first_name") or "there"


def _infer_phase(daily_log: dict[str, Any], phase: str | None) -> str:
    if phase and phase in RITUAL_PHASES:
        return phase
    if daily_log.get("mood") is None and not daily_log.get("moodText"):
        return "mood"
    if not daily_log.get("supps") and phase != "open":
        return "supp"
    if not daily_log.get("meals") and not daily_log.get("foodCats") and phase != "open":
        return "food"
    if daily_log.get("infl") is None and daily_log.get("inflammation") is None:
        return "infl"
    return "open"


def _phase_question(phase: str, pattern: str) -> str:
    questions = {
        "mood": (
            "First, how does your body feel today? "
            "Say low, okay, or good — or tell me about brain fog or tiredness."
        ),
        "supp": (
            "Which supplements did you take today? "
            "For your pattern I'd highlight myo-inositol — say inositol, magnesium, NAC, spearmint, or none."
        ),
        "food": (
            "What did you eat, or what food categories stood out? "
            "Mention dairy, high sugar carbs, oats, salmon, or anything you noticed."
        ),
        "infl": (
            "Any inflammation signals today — bloating, joint ache, or skin flare? "
            "Say none, mild, or noticeable."
        ),
        "open": (
            "Ask me anything about your labs, supplements, or food — "
            "for example, should I take inositol, or why brain fog? Say done when you're finished."
        ),
    }
    return questions.get(phase, questions["open"])


def _extract_log_updates(text: str, phase: str) -> dict[str, Any]:
    lowered = (text or "").strip().lower()
    updates: dict[str, Any] = {}
    if not lowered:
        return updates

    if phase == "mood":
        if re.search(r"\b(done|finish|skip)\b", lowered):
            updates["mood"] = 3
        elif any(w in lowered for w in ("fog", "foggy", "tired", "exhausted", "low", "bad", "rough", "sad")):
            updates["mood"] = 2
        elif any(w in lowered for w in ("okay", "ok", "fine", "meh", "neutral", "average")):
            updates["mood"] = 3
        elif any(w in lowered for w in ("good", "great", "well", "energetic", "happy")):
            updates["mood"] = 4
        updates["moodText"] = text.strip()[:240]

    elif phase == "supp":
        if re.search(r"\b(none|nothing|no supplements|didn't take|skipped)\b", lowered):
            updates["supps"] = []
        else:
            found: list[str] = []
            for alias, sid in SUPP_ALIASES.items():
                if alias in lowered and sid not in found:
                    found.append(sid)
            if found:
                updates["supps"] = found

    elif phase == "food":
        cats: list[str] = []
        meals: list[str] = []
        for alias, cid in FOOD_CAT_ALIASES.items():
            if alias in lowered and cid not in cats:
                cats.append(cid)
        for alias, mid in MEAL_ALIASES.items():
            if alias in lowered and mid not in meals:
                meals.append(mid)
        if cats:
            updates["foodCats"] = cats
            updates["food_triggers"] = cats
        if meals:
            updates["meals"] = meals

    elif phase == "infl":
        if re.search(r"\b(none|no|nothing|fine)\b", lowered):
            updates["infl"] = "none"
            updates["inflammation"] = "none"
        elif "noticeable" in lowered or "bad" in lowered or "flare" in lowered:
            updates["infl"] = "noticeable"
            updates["inflammation"] = "noticeable"
        elif "mild" in lowered or "little" in lowered or "some" in lowered or "bloat" in lowered:
            updates["infl"] = "mild"
            updates["inflammation"] = "mild"

    elif phase == "open":
        voice = parse_voice_for_cognition(text)
        updates["voice"] = {
            "transcript": text.strip()[:500],
            "cognition_signals": voice.get("cognition_signals", []),
        }
        if voice.get("inferred_mood"):
            updates["mood"] = voice["inferred_mood"]

    return updates


def _mood_ack(text: str, updates: dict[str, Any], pattern: str, memory: dict[str, Any]) -> str:
    lowered = (text or "").lower()
    short_pattern = pattern.split("·")[0].strip()
    if any(w in lowered for w in ("tired", "exhausted", "fatigue", "no energy", "worn out")):
        wear = memory.get("wearable") or {}
        parts = ["I hear you — tired days are genuinely hard."]
        sleep_h = wear.get("sleep_hours")
        if sleep_h:
            frag = " · fragmented" if wear.get("sleep_fragmented") else ""
            parts.append(f"Your wearable shows {sleep_h}h sleep{frag}.")
        parts.append(
            f"With your {short_pattern} pattern, short sleep and insulin resistance often stack — "
            f"protein breakfast and steady glucose can help today."
        )
        if updates.get("mood"):
            parts.append(f"Mood logged at {updates['mood']}/5.")
        return " ".join(parts)
    if any(w in lowered for w in ("fog", "foggy", "can't focus", "brain")):
        cognition = (memory.get("layer_scores") or {}).get("cognition", {})
        score = cognition.get("score", "—")
        return (
            f"Brain fog noted — your cognition layer is {score}/100. "
            f"I've logged that against your {short_pattern} pattern. "
            f"Sleep, vitamin D, and steady meals are the levers worth watching today."
        )
    if updates.get("mood"):
        return f"Got it — mood logged against your {short_pattern} pattern."
    return "Thanks — I've noted how you feel today."


def _short_ack(
    phase: str,
    updates: dict[str, Any],
    pattern: str,
    *,
    text: str = "",
    memory: dict[str, Any] | None = None,
) -> str:
    if phase == "mood" and updates.get("mood"):
        return _mood_ack(text, updates, pattern, memory or {})
    if phase == "supp":
        supps = updates.get("supps")
        if supps is None:
            return "I'll note your supplement question."
        if not supps:
            return "No supplements today — that's fine."
        return f"Logged {', '.join(supps)} for today."
    if phase == "food" and (updates.get("foodCats") or updates.get("meals")):
        return "Food noted — I'll weigh that against insulin resistance in your labs."
    if phase == "infl" and updates.get("infl"):
        return f"Inflammation set to {updates['infl']}."
    if phase == "open":
        return "Here's what your labs support."
    return "Thanks — I've updated your draft."


def _is_question(text: str, phase: str) -> bool:
    lowered = text.lower()
    if "?" in text:
        return True
    if re.search(r"\b(should i|why|what|how|explain)\b", lowered):
        return True
    if phase == "open" and re.search(r"\b(berberine|safe|mean|borderline)\b", lowered):
        return True
    return False


def run_conversation_turn(
    message: str = "",
    phase: str | None = None,
    daily_log: dict[str, Any] | None = None,
    memory: dict[str, Any] | None = None,
    *,
    action: str = "turn",
) -> dict[str, Any]:
    """Proactive ElevenLabs-ready ritual conversation — agent speaks and asks each step."""
    memory = memory or {}
    daily_log = dict(daily_log or {})
    pattern = (memory.get("labs") or {}).get("latest", {}).get("pattern") or "endocrine-metabolic pattern"
    name = _profile_name(memory)
    text = (message or "").strip()
    current = _infer_phase(daily_log, phase)

    if action == "start" or (not text and action in {"start", "turn"}):
        speak = (
            f"Hi {name}, I'm Anna — your personal hormone intelligence assistant. "
            f"I've read your lab pattern — {pattern}. "
            f"I'll check in on your mental health and how it connects to what your labs show. "
            f"Let's log today gently, one step at a time. "
            f"{_phase_question('mood', pattern)}"
        )
        return {
            "tool": "daily_ritual_voice_agent",
            "speak_text": speak,
            "answer": speak,
            "phase": "mood",
            "next_phase": "mood",
            "log_updates": {},
            "listening": True,
            "lab_context": pattern,
            "suggestions": [],
            "quick_replies": QUICK_BY_STEP["mood"][:3],
        }

    if current == "open" and re.search(r"\b(done|finish|that'?s all|complete)\b", text.lower()):
        summary = _daily_summary(pattern, memory.get("layer_scores") or {}, memory.get("care_gaps") or [], daily_log)
        speak = f"Perfect — ritual complete. {summary}"
        return {
            "tool": "daily_ritual_voice_agent",
            "speak_text": speak,
            "answer": speak,
            "phase": "done",
            "next_phase": "done",
            "log_updates": {},
            "listening": False,
            "lab_context": pattern,
            "suggestions": [],
            "quick_replies": [],
        }

    updates = _extract_log_updates(text, current)
    merged_log = {**daily_log, **updates}
    if "supps" in updates and isinstance(updates["supps"], list):
        merged_log["supps"] = updates["supps"]
    if "foodCats" in updates:
        merged_log["foodCats"] = updates["foodCats"]

    is_question = _is_question(text, current)

    qa_block = ""
    suggestions: list[dict[str, Any]] = []
    cognition_signals: list[str] = []

    if is_question or current == "open":
        qa = answer_daily_question(text, current, merged_log, memory)
        qa_block = qa["answer"]
        suggestions = qa.get("suggestions") or []
        cognition_signals = qa.get("cognition_signals") or []

    idx = RITUAL_PHASES.index(current) if current in RITUAL_PHASES else 0
    advance = bool(updates) and not is_question
    if current == "open" and is_question and not re.search(r"\b(done|finish)\b", text.lower()):
        next_phase = "open"
    elif advance and idx < len(RITUAL_PHASES) - 1:
        next_phase = RITUAL_PHASES[idx + 1]
    elif advance:
        next_phase = "open"
    else:
        next_phase = current

    if current == "mood" and updates and any(
        w in text.lower() for w in ("tired", "exhausted", "fatigue", "fog", "foggy")
    ):
        cognition_signals.append("Fatigue · daily check-in")

    ack = _short_ack(current, updates, pattern, text=text, memory=memory) if updates else ""
    if not ack and not qa_block:
        ack = "I didn't catch that — try again, or ask me a question about your labs."

    if next_phase != current and next_phase != "open":
        speak = f"{ack} {_phase_question(next_phase, pattern)}".strip()
    elif next_phase == "open" and current != "open":
        speak = f"{ack} {_phase_question('open', pattern)}".strip()
    elif qa_block:
        speak = f"{qa_block} {_phase_question(current, pattern) if next_phase == current else ''}".strip()
    else:
        speak = f"{ack} {_phase_question(current, pattern)}".strip()

    step_map = {"mood": 0, "supp": 1, "food": 2, "infl": 3, "open": 4, "done": 5}

    return {
        "tool": "daily_ritual_voice_agent",
        "speak_text": speak,
        "answer": speak,
        "phase": current,
        "next_phase": next_phase,
        "wizard_step": step_map.get(next_phase, step_map.get(current, 0)),
        "log_updates": updates,
        "listening": next_phase != "done",
        "lab_context": pattern,
        "suggestions": suggestions,
        "cognition_signals": cognition_signals,
        "quick_replies": QUICK_BY_STEP.get(next_phase, QUICK_BY_STEP["general"])[:3],
        "confidence": 0.88,
    }

