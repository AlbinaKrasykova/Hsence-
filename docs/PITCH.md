# Hsence — Problem, Solution & Distribution

## One-liner

**Hsence is a hormonal intelligence platform with a precision medicine agent** — it syncs labs and wearable data once, explains your hormonal state in plain language, and turns that into a personal plan (food, supplements, daily ritual) with clinician-ready handoff. Not a diagnosis engine.

---

## Problem

Women with **PCOS, perimenopause, gestational diabetes, osteoporosis, and hormone-sensitive survivorship** are routinely **dismissed or left to piece together care alone**:

- GPs flag labs as “borderline” without explaining what they mean for symptoms.
- Hormones, metabolism, sleep, and mood are treated in **separate silos** — no one reads them together.
- Patients rely on **forums and intuition** between appointments, with no medically grounded parallel system.
- **8–10 years** average time to PCOS diagnosis; **0 FDA-approved** options for common perimenopause cognitive symptoms.
- Care gaps (imaging follow-up, trial eligibility, supplement evidence) are **never surfaced** at the patient front door.

---

## Solution

**Hsence** gives users a calm, rigorous parallel care system:

| Layer | What it does |
|--------|----------------|
| **Home + setup** | Connect wearable, upload blood work, see hormonal state + risks + supplement plan in one guided flow |
| **Precision agent** | Autonomous CDSS: detects intent, fuses multimodal data, scores health layers, triages care gaps, matches trials, clinician handoff |
| **Daily ritual** | Low-cognitive-load logging (mood, food, supplements) tied to labs and wearable — no streaks, no shame |
| **Morning brew** | Daily narrative from sleep, HRV, and temperature — one honest read, not a dashboard |

**Design principles:** white, minimal UI · one-click explainers · evidence grades (★ strong / ◈ moderate) · always private · not a prescription tool.

---

## Who it’s for

- **Primary:** Women 25–55 navigating PCOS, perimenopause, or metabolic-hormone overlap.
- **Secondary:** Gestational diabetes, osteoporosis risk, oncology survivorship surveillance.
- **Clinical adjacency:** GPs, endocrinology, OB/GYN — GP summary export, “questions for your doctor,” trial matching demo.

---

## How it’s different

| Typical apps | Hsence |
|--------------|--------|
| Generic 28-day cycle | PCOS- and perimenopause-aware patterns |
| Single biomarker charts | Multimodal fusion: labs + wearable + daily signals |
| Wellness scores | Actionable sentences: what to protect, postpone, push |
| Static content | Agent with tool trace, care gaps, trial criteria |
| Diagnosis claims | Decision support + handoff — **not** a diagnosis engine |

---

## Distribution

### Live demo (after deploy)

- **Render:** `https://hsence.onrender.com` (or your Render service URL)
- **GitHub:** [AlbinaKrasykova/Hsence-](https://github.com/AlbinaKrasykova/Hsence-)

### Local (judges / developers)

```bash
git clone https://github.com/AlbinaKrasykova/Hsence-.git
cd Hsence-
bash scripts/start.sh
```

Open:

- `/` — home, setup flow, morning brew prototype
- `/agent.html` — precision agent (CDSS demo)
- `/daily.html` — daily ritual

### Demo flow (5 min)

1. **Home** → scroll setup flow (wearable + lab upload story).
2. **Agent** → ask: *“Should I take berberine for PCOS?”* → **Run full CDSS cycle**.
3. Show: intent → layers → care gaps → supplement evidence → trial criteria → clinician questions → trace.
4. **Daily ritual** → log mood + food in &lt; 60 seconds.

### Channels

- Hackathon / Nucleate BioHack judging
- GitHub README + `docs/` for reproducibility
- Render blueprint (`render.yaml`) for one-click public URL
- Optional: share LAN URL via `HOST=0.0.0.0 bash scripts/start.sh`

---

## Tech stack

- **Frontend:** Static HTML/CSS/JS (`index.html`, `agent.html`, `daily.html`, `assets/site.css`)
- **Backend:** Python FastAPI agent (`agent/`) — planner, tools, memory, guardrails
- **Deploy:** Render / Railway (`render.yaml`, `Procfile`) — single port for site + API
- **Demo data:** `data/fake-lab-panel.json`, `data/patient-memory.json` — no API keys required

---

## Safety & scope

Hsence is **clinical decision support and patient education**, not a medical device claim. All supplements, trials, and pathways require **clinician confirmation**. Berberine and similar supplements are routed with **weak-evidence** flags where appropriate.
