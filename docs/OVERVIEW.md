# Hsence — Full overview (every point in depth)

Complete GitHub / pitch reference. Shorter summary: [README.md](../README.md)

---

# 1. Introduction

## What is Hsence?

**Hsence** is a **hormonal intelligence platform** — a preventative medicine agent that treats hormones as **longitudinal biomarkers** (signals that change over time and encode reproductive, metabolic, emotional, and cognitive risk). It is built for women navigating PCOS, perimenopause, gestational diabetes, osteoporosis, and hormone-sensitive cancer survivorship.

Unlike a cycle-tracking app or a generic wellness dashboard, Hsence:

1. **Meets patients upstream** where health beliefs form (Patient Front Door).
2. **Reasons over clinical data downstream** with an autonomous CDSS agent (Medical Intelligence / Track 01).

> **Hsence is not a diagnosis engine.** It is clinical decision support, patient education, and clinician handoff preparation.

---

## Pillar A — Patient Front Door

### What it means

The **Patient Front Door** is every channel where a patient forms health beliefs **before** a licensed clinician is in the loop:

- Google and health search
- Generic AI chatbots (ChatGPT, etc.)
- Reddit, TikTok, Instagram health influencers
- Femtech apps with no clinical guardrails
- Pharmacy aisles and supplement marketing

### Why it matters for Hsence

Research and industry framing (Pfizer Patient Front Door) highlight that **treatment choices, adherence, and self-management strategies are often decided in these channels**. By the time a patient books a GP appointment:

- They may have **already started supplements** (e.g. berberine, progesterone cream, “hormone balance” bundles).
- They may have **rejected** standard care based on forum fear.
- They arrive with **fixed beliefs** and fragmented data the clinician has never seen.

### What Hsence does at the front door

| Function | Detail |
|----------|--------|
| **Intent detection** | Classifies: supplement self-treatment, symptom seeking, trial interest, clinician prep, care-gap frustration |
| **Risk stratification** | High-risk intents (e.g. “should I take X”) trigger safety and guidelines **before** recommendations |
| **Double-check** | Cross-checks patient questions against **their** labs, wearable data, and evidence grades — not generic internet answers |
| **Frictionless resolution** | One message → structured output: layers, gaps, pathway, handoff — not a conversational dead end |
| **Explainability** | Intent badge, “Show why,” guideline snippets, full tool trace — auditable reasoning |

### Example (live in repo)

**Input:** *“Should I take berberine for PCOS? My labs show high testosterone.”*

**Behavior:**

1. Intent = `supplement_self_treatment` (high risk).
2. Agent does **not** say “yes, take berberine.”
3. Parses labs → PCOS pattern + insulin resistance.
4. Surfaces **standard care** discussion (e.g. metformin) first.
5. Grades alternatives (★ myo-inositol strong evidence for PCOS insulin picture).
6. Generates **questions for doctor** + trace of every tool.

---

## Pillar B — Medical Intelligence (Track 01 CDSS)

### What it means

**Track 01 Clinical Decision Support** addresses the clinician-side and system-side complexity:

- Multimodal patient data (labs, wearables, EHR, free text, daily behavior)
- **Triage** — what matters most right now?
- **Diagnostic reasoning support** — pattern + layers (not autonomous diagnosis)
- **Care pathways** — nutrition, supplements, lifestyle, referrals
- **Trial matching** — eligibility with traceable rationale
- **Explainability** — reduce cognitive load, improve consistency

### Why hormones are the right lens

Hormones are not “one blood test.” They are **cross-system signals**:

- **Reproductive** — LH, FSH, testosterone, estradiol, progesterone
- **Metabolic** — insulin, glucose, lipids, HOMA-IR
- **Cognitive / sleep** — HRV, sleep architecture, mood (via wearable + daily log)
- **Inflammation / recovery** — especially in survivorship and metabolic overlap

Hsence reads these **together** — the same architecture serves PCOS and perimenopause and GDM with condition modules.

### Hackathon alignment

| Track 01 theme | Hsence implementation |
|----------------|----------------------|
| Multimodal fusion | Labs + wearable + daily ritual + chat in one agent run |
| Triage | `score_care_gaps` — ranked, evidence-tagged |
| Diagnostic reasoning | `parse_lab_panel` + `score_layer_health` |
| Care pathways | `recommend_precision_nutrition` |
| Trial matching | `match_clinical_trials` — criterion-by-criterion |
| Explainability | Guideline snippets + agent trace |
| Structured memory | `patient-memory.json` (demo) → EHR/FHIR (roadmap) |

---

# 2. Problem (in depth)

## 2.1 Hormonal health is invisible until it becomes chronic

### Scale

- A **large majority of women** experience hormonal transitions and imbalances across the lifespan — from puberty through PCOS, pregnancy, perimenopause, and post-menopause.
- Many conditions driven by hormones remain **undiagnosed for years**. PCOS is a documented example: **8–10 years** average from symptom onset to diagnosis in many cohorts.
- Even after diagnosis, patients report feeling **dismissed, unsupported, and confused** — especially when labs are labeled “borderline” or “normal” while symptoms persist.

### Why “borderline” fails patients

A single marker (e.g. LH:FSH 3.6) without context leaves patients with:

- No connection to **symptoms** (acne, weight, fatigue, irregular cycles).
- No connection to **risk** (insulin resistance, cardiovascular lipids, fertility).
- No **action plan** — only anxiety and more searching online.

### Conditions share a hormonal thread

| Condition | Hormonal / systemic link |
|-----------|--------------------------|
| **PCOS** | Androgen excess, insulin resistance, anovulation |
| **Perimenopause** | Estrogen/progesterone transition, sleep, cognition, bone loss |
| **Gestational diabetes** | Pregnancy insulin resistance, glucose variability |
| **Osteoporosis** | Estrogen decline, vitamin D, PTH, fracture risk |
| **Diabetes (type 2 overlap)** | Insulin, metabolic syndrome, PCOS overlap |
| **Hormone-sensitive cancer** | Endocrine therapy, surveillance, inflammation in recovery |

Hsence is designed as **one platform** with **condition modules** — not five separate apps.

---

## 2.2 Patient Front Door — the upstream gap (expanded)

### The gap (official framing)

> Patients today form their healthcare beliefs in places the healthcare system does not show up — search engines, AI chatbots, social communities, apps. What they find there often shapes decisions about treatment, adherence, and self-management before a clinician is ever involved, and is frequently wrong, incomplete, or misaligned with their actual condition. By the time they reach a clinician, the most consequential decisions have often already been made.

### Mechanisms of harm

1. **Wrong** — e.g. megadose vitamin D, unregulated progesterone creams, stopping tamoxifen based on a blog.
2. **Incomplete** — e.g. berberine promoted without HOMA-IR context or pregnancy safety.
3. **Misaligned** — e.g. fertility advice applied to a perimenopause brain-fog presentation.
4. **Adherence damage** — patient starts supplements, feels “treated,” skips follow-up labs and clinician visits.

### What generic AI chatbots miss

- No access to **your** lab PDF.
- No **longitudinal** wearable baseline.
- No **care-gap** or **trial** context.
- No **clinician handoff** artifact.
- No **safety guardrail** against diagnosis or prescription language.

Hsence is the experiment: **AI-native intent detection + multimodal CDSS + loop closure.**

---

## 2.3 Track 01 — the downstream gap (expanded)

### Clinical reality

- Decisions are **time-pressured** — short appointments, high cognitive load.
- Data is **siloed** — labs in one portal, wearables in another, patient story in free text.
- **Trial recruitment** is a bottleneck — pre-screening can consume **~60%** of recruitment effort; median eligibility criteria complexity has increased substantially over two decades.

### What clinicians need

Agents that:

- **Fuse** multimodal inputs automatically.
- **Triage** what to address first.
- **Recommend pathways** with evidence.
- **Match trials** with **explainable** eligibility.
- **Hand off** structured questions and summaries — not more raw data.

### Publication-backed direction (talking points)

- Multimodal oncology CDSS agents (Nature Medicine 2025) — Hsence analogue: endocrine-metabolic multimodal agent.
- Agentic triage with EHR integration (IJSRSET 2025) — Hsence analogue: planner + tools vs fixed rules.
- TrialMatchAI (arXiv 2025) — Hsence analogue: criterion-level trial rows in UI.
- LLM trial matching scoping review (JCO 2025) — Hsence addresses interpretability via trace; EHR on roadmap.

---

# 3. Solution — Hsence preventative medicine agent (each point expanded)

## 3.1 Proactive medicine rather than reactive

**Reactive care today:** One annual blood draw, one 10-minute visit, crisis-driven appointments.

**Hsence proactive model:**

- **Wearables** passively build sleep, HRV, temperature baselines nightly.
- **Labs** uploaded when available — parsed into patterns, not isolated flags.
- **Daily ritual** captures cognition and behavior in &lt;60 seconds.
- **Morning brew** delivers one narrative read — what to protect today.

**Outcome:** Shifts from “something is wrong” to **continuous hormone-state awareness** and early gap surfacing (DEXA overdue, postpartum glucose screen, etc.).

---

## 3.2 Continuous patient monitoring + multimodal data fusion

### Data sources (ingestion layer)

| Source | Examples | Role |
|--------|----------|------|
| **Blood labs** | LH, FSH, testosterone, glucose, insulin, lipids, vitamin D, thyroid | Pattern detection, care gaps |
| **Wearables** | Oura, Apple Watch — sleep, HRV, readiness, temp | Cognition layer, daily state |
| **EHR** (roadmap) | Problem list, meds, imaging dates | Surveillance gaps, Rx context |
| **Daily behavior** | Mood, food, supplements, inflammation note | Adherence, triggers |
| **Patient chat** | Front-door questions | Intent + routing |

### Fusion logic

Data is **time-aligned** and stored in **health memory**. The agent does not treat a testosterone value alone — it reads testosterone + SHBG + LH:FSH + HOMA-IR + sleep fragmentation **together**.

---

## 3.3 Longitudinal memory — parsing medical history

**Problem:** Every appointment starts from zero.

**Hsence approach:**

- Persist lab patterns, care gaps, layer scores, prior intents, agent traces.
- Demo: `data/patient-memory.json`
- Production: PostgreSQL + optional vector retrieval for guideline/similar-case support.

**Benefit:** “What changed since last panel?” and “which gaps are still open?” — critical for chronic hormonal conditions.

---

## 3.4 Hormones as longitudinal biomarkers

Hormones are not static labels. They encode **trajectories**:

- PCOS: androgen + insulin trajectory over years
- Perimenopause: FSH rise, estradiol variability, sleep disruption
- GDM: rising insulin resistance across pregnancy
- Post-meno: estrogen decline + bone density risk

Hsence maps signals to **hormone state** and **four interrelated layers** — not a single “phase day.”

---

## 3.5 Identify relevant biomarkers

### Reproductive / endocrine
LH, FSH, LH:FSH ratio, estradiol, progesterone, testosterone (total/free), SHBG, AMH, DHEA-S

### Metabolic
Fasting glucose, HbA1c, insulin, HOMA-IR, total/LDL/HDL cholesterol, triglycerides

### Bone / nutritional
Vitamin D, calcium, PTH, ferritin

### Wearable proxies
Sleep duration/architecture, HRV delta, skin temperature, readiness

### Behavioral
Mood, meal timing, supplement adherence, inflammation self-report

The agent **selects relevance** by condition module and care gaps — not every marker every time.

---

## 3.6 Personalized plan based on hormone state

### Nature-based and evidence-graded supplements

- **★ Strong evidence** — e.g. myo-inositol 40:1 for PCOS insulin/LH:FSH patterns (in demo).
- **◈ Moderate** — e.g. NAC, omega-3, magnesium — context-dependent.
- **Weak / flagged** — e.g. berberine self-start from search — standard care first.

### Food and lifestyle

- Low-GI rules for insulin resistance.
- Protein-forward meals for glucose stability (GDM, PCOS).
- Anti-inflammatory plates for survivorship recovery.
- Weight-bearing cues for bone health.

### Medications — always doctor-referred

Hsence **never** prescribes. It prepares:

- “Discuss metformin given HOMA-IR 4.1”
- “Are these supplements appropriate with my current meds?”
- HRT / bone medication conversations with structured questions.

---

## 3.7 Alerts, follow-up, clinician loop

| Alert type | Example |
|------------|---------|
| Care gap | Insulin resistance workup incomplete |
| Surveillance | DEXA overdue post-menopause |
| Postpartum | GDM → type 2 diabetes screen reminder |
| Trial | Eligibility criteria partially met — discuss with coordinator |
| Safety | High-risk supplement intent detected |

**Follow-up:** Clinician handoff panel — visit questions, summary bullets, export roadmap for GP PDF.

---

## 3.8 Double-check user health requests

### Why this is core to Patient Front Door

Patients ask natural-language questions that are **high stakes**:

- *“Will this supplement normalize my blood sugar?”*
- *“Should I stop tamoxifen for natural alternatives?”*
- *“Can I take berberine while pregnant?”*

### Hsence double-check pipeline

1. **Intent classification** — what kind of question is this?
2. **Risk level** — supplement self-treatment = high.
3. **Multimodal cross-check** — labs + context (pregnancy = hard stop).
4. **Evidence grade** — strong / moderate / weak.
5. **Standard care routing** — what should clinician discuss first?
6. **Guardrail** — disclaimer, no diagnosis language.

---

## 3.9 Better adherence

- **Daily ritual** — step-by-step, skippable, no streak punishment.
- **Morning brew** — one emotional + clinical narrative — reduces dashboard fatigue.
- **Supplement chips** — matched to plan, log what you took.
- **Experiment framing** (home prototype) — 14-day protein breakfast trial tied to afternoon energy.

**Link to Pfizer outcomes:** Better adherence → better outcomes → cleaner prior auth and pathway adherence narratives.

---

# 4. Patient Front Door — experiment & business impact (expanded)

## 4.1 Current efforts

> We are designing an experiment to test whether an AI-native approach can better detect patient intent and close the loop with a frictionless path to resolution.

### Hypothesis

If patients receive **intent-aware, multimodal, traceable** resolution at the front door, then:

- Fewer harmful self-treatment decisions stick.
- Clinical encounters start with **aligned** expectations.
- Medical intelligence surfaces earn **trust** (citations, rank) vs generic AI.

### What is built (measurable in demo)

- Intent tool with 5+ intent classes.
- Planner with dynamic tool lists per event type (`full_cycle`, `chat`, `clinician_handoff`, `trial_search`).
- UI surfaces: intent badge, layers, gaps, trials, trace, doctor questions.
- End-to-end API: `POST /agent/run` on same port as static site.

---

## 4.2 How this helps — each outcome in depth

### → Patient journey: faster time to prescription

**Problem:** Patient delays Rx because they’re trying supplements first or don’t understand insulin resistance.

**Hsence:** Surfaces **documented gap** — e.g. HOMA-IR elevated, metformin discussion indicated — with lab evidence patient can show at visit.

**Result:** Shorter path from “confused” to **appropriate prescription conversation** (clinician still decides).

---

### → Higher first-time prior auth approval

**Problem:** PA fails when medical necessity narrative is thin.

**Hsence (roadmap):** Exportable summary — pattern, gaps, failed conservative steps, biomarker timeline.

**Result:** Patient and clinician submit **structured rationale** first time.

---

### → Faster time to approval

**Problem:** Back-and-forth on “try lifestyle first” without documentation.

**Hsence:** Shows lifestyle + supplement trials in daily log; documents adherence attempts.

**Result:** Faster insurer/clinical alignment when step therapy required.

---

### → Share of voice: increased citations in patient queries

**Problem:** Patient queries answered by unreferenced social content.

**Hsence:** Embeds **guideline snippets** with source labels in UI — designed for curated medical intelligence corpus.

**Result:** Hsence-aligned answers become **citable** in patient education and AI-mediated search (production partnership path).

---

### → Share of model rank

**Problem:** Black-box chatbots rank on fluency, not safety or traceability.

**Hsence:** Every answer backed by **tool trace** — auditable steps judges, regulators, and models can score.

**Result:** Higher trust ranking for medical-intent queries vs generic wellness bots.

---

# 5. Architecture (each layer in depth)

## 5.1 Data ingestion

| Channel | Processing |
|---------|------------|
| Lab PDF | Parse → normalize units → flag high/low → pattern inference |
| Manual lab entry | Setup flow / agent sidebar |
| Wearable API (roadmap) | Sleep, HRV, temp sync |
| Daily ritual | Mood, food, supplements, voice memo (demo) |
| EHR FHIR (roadmap) | Meds, problems, imaging dates |
| Chat | Raw query → intent pipeline |

---

## 5.2 Health memory

Stores:

- Profile (age, sex, condition focus)
- Latest lab pattern and markers
- Wearable snapshot
- Daily log aggregate
- Care gaps list
- Precision plan (foods, supplements, meals)
- Intent history
- Agent trace log

**Demo file:** `data/patient-memory.json`  
**Production:** PostgreSQL; FAISS/Pinecone for similarity (as on home architecture section).

---

## 5.3 Intelligence engine

| Component | Function |
|-----------|----------|
| State estimator | P(phase/pattern \| signals) — PCOS, anovulatory, metabolic, etc. |
| Risk scoring | Cardiovascular, insulin, androgen, bone, surveillance |
| Care-gap ranker | Priority queue with evidence strings |
| Condition modules | PCOS, perimenopause, GDM, osteoporosis, survivorship rules |

---

## 5.4 CDSS agent core

### Autonomous planner

- Input: event type + memory + payload
- Output: ordered tool list + human-readable reasoning
- Not a fixed pipeline — e.g. `clinician_handoff` skips re-parse if gaps exist

### Four layers (expanded)

**Hormones & endocrine**  
LH:FSH, androgens, estradiol, progesterone, cycle context.

**Metabolic & cardiovascular**  
Glucose, insulin, HOMA-IR, lipids — NAFLD/cholesterol risk in PCOS.

**Cognition & nervous system**  
Sleep hours, HRV, readiness, mood — “brain fog” in perimenopause.

**Inflammation & recovery**  
Food triggers, daily inflammation report, survivorship recovery.

Layers are **scored 0–100** in UI — support prioritization, not diagnosis.

### Care pathways tool

`recommend_precision_nutrition` outputs:

- Meals (e.g. salmon + roasted vegetables)
- Food rules (low-GI, protein breakfast, etc.)
- Supplements with evidence strings and priority
- Lifestyle blocks

### Trial matching tool

Mock trials with:

- Trial ID, title, indication
- **Per-criterion** met / not met
- Match reason string

Analogue to TrialMatchAI / CoT eligibility.

### Clinician handoff tool

- Questions categorized by topic (PCOS evaluation, supplements, surveillance)
- Visit summary bullets from layers + gaps + plan

### Safety guardrail

- Appends disclaimer
- Blocks presenting outputs as diagnosis or prescription

---

## 5.5 Product surface

| Surface | User job |
|---------|----------|
| **Home + setup** | First sync story — wearable + lab upload prototype |
| **Agent UI** | Full CDSS cycle + trace |
| **Daily ritual** | Log + review timeline |
| **Morning brew** | Daily narrative — condition modes in prototype |

---

## 5.6 Tech implementation (this repository)

```
Browser (index.html, agent.html, daily.html)
        ↓
FastAPI (agent/server.py) — static files + API
        ↓
orchestrator.py → planner.py → tools/*.py
        ↓
patient-memory.json + fake-lab-panel.json
```

**Deploy:** `render.yaml` — `python scripts/run_app.py` — port 8080 (or Render `PORT`).

---

# 6. Condition modules (summary)

Deep dive: [CONDITION_CASES.md](CONDITION_CASES.md)

| Module | Front-door risk | CDSS focus |
|--------|-----------------|------------|
| PCOS | Berberine, spearmint self-treatment | Insulin, androgens, inositol ★ |
| Perimenopause | Online HRT/creams | Cognition, sleep, bone gaps |
| GDM | Pregnancy unsafe supplements | Meal timing, glucose |
| Osteoporosis | Vitamin D megadose | DEXA gap, D3+K2 |
| Survivorship | Stopping endocrine therapy | Trials, surveillance |

---

# 7. Safety & regulatory posture

- **CDSS / patient education** — not a medical device claim in this hackathon demo.
- **No autonomous prescribing.**
- **High-risk intents** routed to clinician conversation.
- **Pregnancy guardrails** — no unsupervised herbals.
- **Oncology guardrails** — no advising Rx changes.

---

# 8. Roadmap

| Demo today | Production |
|------------|------------|
| JSON memory | PostgreSQL + FHIR |
| Rule + planner intent | LLM intent + human review |
| Mock trials | Live trial registry API |
| Static HTML | Patient app + clinician dashboard |
| GP summary alert | Prior-auth packet export |

---

# 9. Quick links

- [README.md](../README.md) — GitHub landing
- [ARCHITECTURE.md](ARCHITECTURE.md) — Mermaid PNG export
- [TRACK01_ALIGNMENT.md](TRACK01_ALIGNMENT.md) — Pfizer ↔ Track 01
- [PITCH_DECK.md](PITCH_DECK.md) — Slides
- [DEMO.md](DEMO.md) — Live script
