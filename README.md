# Hsence
 **[DEMO](https://hsence.onrender.com/)**

![Recording](Hsence-/Recording%202026-06-06%20at%2014.24.57.gif)

> **Definition:** Hsence is a preventive medicine agent and hormonal intelligence platform that uses hormones as longitudinal biomarkers to track health, prevent chronic disease, and close the loop to clinicians — with a traceable clinical decision support (CDSS) agent.

**Hormonal intelligence platform** · Patient Front Door + Medical Intelligence

**Nucleate NY BioHack · Track 01** — *Triage, diagnostics, care pathways, trial matching & multimodal patient data*

---

## Project definition

**Hsence** helps women navigate hormone-linked conditions — **PCOS, perimenopause, gestational diabetes, osteoporosis, and hormone-sensitive cancers** — with proactive, evidence-based care between appointments.

Most patients form treatment beliefs on Google, Reddit, and generic AI *before* seeing a clinician. Hsence meets them at that **Patient Front Door**: it detects intent, double-checks risky requests against *their* labs and wearable data, and routes weak evidence to standard care first. On the clinical side, **Medical Intelligence** fuses multimodal signals into a traceable CDSS pipeline — triage, four-layer scoring, care pathways, trial matching, and clinician handoff.

### What Hsence is

| | |
|---|---|
| **Type** | Hackathon demo — static web app + Python FastAPI agent on one port |
| **Core idea** | Hormones as living biomarkers — tracked over time, not one annual blood draw |
| **Inputs** | Blood labs · wearable (Oura / Apple Watch) · daily ritual · patient chat |
| **Outputs** | Hormonal pattern read · care gaps · ★/◈ supplements · food rules · doctor questions · full agent trace |
| **Conditions** | PCOS · perimenopause · GDM · osteoporosis · ER+ cancer survivorship |

### What Hsence is not

- **Not a diagnosis engine** — decision support and education only
- **Not a prescription tool** — medications always clinician-prescribed
- **Not a cycle tracker** — condition-aware patterns, not a generic 28-day model

### Two pillars

| Pillar | What it does |
|--------|----------------|
| **Patient Front Door** | Intercepts beliefs before the clinic. Detects intent, double-checks supplement requests (e.g. *“Should I take berberine for PCOS?”*), closes the loop safely. |
| **Medical Intelligence** | Track 01 CDSS: autonomous planner → 9 tools → 4 layers (hormones · metabolic · cognition · inflammation) → pathways → trials → handoff → guardrails. |

**Tagline:** Proactive care — not reactive guesswork.

**Pitch deck:** [docs/PITCH_DECK.md](docs/PITCH_DECK.md) · **Full depth:** [docs/OVERVIEW.md](docs/OVERVIEW.md) · **User steps:** see [User journey](#user-journey) below

---

## Architecture

*Multimodal data flows up · personalised understanding and clinician-ready actions flow down.*

**Solid = built today** · **Dashed = vision**

```mermaid
flowchart TB
  subgraph PFD["Patient Front Door · built"]
    CHAT[agent.html · chat + intent]
    SEARCH[Intercepts search path · vision]
  end

  subgraph INGEST["Data · demo today → vision"]
    LABS[fake-lab-panel.json → PDF parser]
    WEAR[Wearable fields → Oura / Apple OAuth]
    LOG[Daily ritual · localStorage + API]
    EHR[EHR / FHIR · roadmap]
  end

  subgraph RUNTIME["Runtime · built · port 8080"]
    API[FastAPI · agent/server.py]
    SITE[Static HTML · index · agent · daily]
  end

  subgraph MEMORY["Memory · built → vision"]
    STORE[(patient-memory.json → PostgreSQL)]
  end

  subgraph CDSS["Track 01 CDSS · built"]
    PLAN[planner.py]
    TOOLS[9 rule-based tools · orchestrator.py]
    LAYERS[4 layers · H · M · C · I]
    PATH[Pathways · ★/◈ supplements]
    TRIAL[Trial match · demo]
    HANDOFF[Clinician handoff]
    GUARD[safety_guardrail]
  end

  subgraph UI["Product · built"]
    HOME[Setup · 5 steps]
    AGENT[Precision agent + trace]
    DAILY[Daily ritual]
    BREW[Morning brew · JS narratives]
  end

  CHAT --> API
  LABS & WEAR & LOG --> STORE
  EHR -.-> STORE
  STORE --> PLAN
  API --> PLAN --> TOOLS --> LAYERS --> PATH --> TRIAL --> HANDOFF --> GUARD
  GUARD --> AGENT
  SITE --> HOME & DAILY & BREW
  SEARCH -.-> CHAT

  style PFD fill:#fef6e8,stroke:#BA7517
  style CDSS fill:#eeeefb,stroke:#7F77DD
  style INGEST fill:#e8f4fc,stroke:#3B8BD4
  style MEMORY fill:#fdeee8,stroke:#D85A30
  style RUNTIME fill:#e8f8f0,stroke:#1D9E75
```

| Built now | Vision |
|-----------|--------|
| FastAPI + static site, one port | Production deploy (Render) |
| `patient-memory.json` + agent trace | PostgreSQL + FHIR |
| Demo lab JSON + wearable form fields | Live labs PDF + Oura OAuth |
| 9 traceable rule-based CDSS tools | LLM narrative layer (optional) |
| Setup UI prototype + morning brew JS | Full ingestion pipeline |

Export PNG: [mermaid.live](https://mermaid.live) · **SVG diagrams:** **[docs/diagrams/](docs/diagrams/)** · Full docs: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

![Hsence architecture](docs/diagrams/hsence-architecture.png)

---

## User journey

| Step | Where | What you complete |
|------|-------|-------------------|
| **1 · Setup** | Home → `#setup` | Connect wearable → upload labs → see hormonal state → supplement plan → diet (5 steps) |
| **2 · Daily ritual** | `/daily.html` | Mood → supplements → food → inflammation → optional voice memo |
| **3 · Precision agent** | `/agent.html` | Ask a question → **Run full CDSS cycle** → review intent, layers, gaps, handoff, trace |
| **4 · Morning brew** | Home → `#prototype` | Daily narrative from sleep, HRV, and hormone context |

**Demo query:** *“Should I take berberine for PCOS?”*

---

## Problem

### Hormonal health is systemic — care is fragmented

- The majority of women experience **hormonal shifts** that drive chronic conditions; many remain **undiagnosed for years** (e.g. PCOS: 8–10 years average to diagnosis).
- Once diagnosed, patients often feel **unsupported and confused** — “borderline” labs, no clear plan.
- **Hormones influence the whole body:** PCOS, **perimenopause**, osteoporosis, diabetes, hormone-sensitive **cancer survivorship** — not just reproduction.

### Patient Front Door — the upstream gap

Patients form healthcare beliefs where the **healthcare system does not show up** — search engines, AI chatbots, social communities, apps. What they find shapes decisions about **treatment, adherence, and self-management** before a clinician is involved — often **wrong, incomplete, or misaligned** with their condition.

**By the time they reach a clinician, the most consequential decisions have often already been made.**

*Example:* *“Should I take berberine for PCOS?”* — decided on Reddit, not in the clinic.

### Track 01 — the downstream gap

Clinical decision-making is **data-intensive and time-pressured**. Trial recruitment consumes up to **60%** of effort; eligibility criteria have surged **58%** over two decades. Clinicians need agents that fuse multimodal inputs with **traceable** triage and pathway support.

---

## Solution — Hsence preventative medicine agent

Hsence focuses on **multimodal analysis**, **longitudinal memory**, and **hormones as biomarkers** to track health and help prevent — and manage — chronic disease.

| Capability | What Hsence does |
|------------|------------------|
| **Proactive vs reactive** | Continuous monitoring via wearables, labs, daily cognition — not one snapshot per year |
| **Multimodal fusion** | Labs + EHR-ready memory + wearable signals + daily behavior |
| **Longitudinal memory** | Parses medical history; patterns and care gaps persist visit to visit |
| **Biomarker intelligence** | LH:FSH, insulin, vitamin D, inflammation, sleep/HRV — tied to **hormone state** |
| **Personalized plan** | Evidence-graded **supplements** (★ strong / ◈ moderate), food rules, lifestyle |
| **Medications** | **Referred to doctor** — never self-prescribed |
| **Alerts & follow-up** | Care-gap triage, clinician handoff, trial match (demo) |
| **Front-door safety** | **Double-checks** health requests — e.g. *“Will this supplement normalize blood sugar?”* → labs + guidelines + standard care first |
| **Better adherence** | Daily ritual + morning brew — low friction, no shame |

### Condition modules

PCOS · perimenopause · gestational diabetes · osteoporosis · hormonal cancer survivorship — see **[docs/CONDITION_CASES.md](docs/CONDITION_CASES.md)**

---

## Patient Front Door — experiment & impact

### Current efforts

We are designing an experiment to test whether an **AI-native approach** can better **detect patient intent** and **close the loop** with a frictionless path to resolution.

**Built in this repo:**

- `detect_patient_intent` — supplement risk, symptoms, trials, clinician prep
- Autonomous planner → full CDSS cycle from one chat message
- **Show why** · guideline snippets · **full agent trace**

### How this helps

| Outcome | Mechanism |
|---------|-----------|
| **Patient journey** — faster time to prescription | Surfaces standard-care gaps (e.g. metformin discussion) with lab evidence |
| **Higher first-time prior auth approval** | Structured GP summary + rationale (roadmap: PA packet) |
| **Faster time to approval** | Patient expectations aligned to guidelines before submission |
| **Share of voice** — citations in patient queries | Guideline snippets + evidence grades — citable medical intelligence |
| **Share of model rank** | Traceable tool chain replaces opaque chatbot answers |

Alignment detail: **[docs/TRACK01_ALIGNMENT.md](docs/TRACK01_ALIGNMENT.md)**

---

## Agent flow & technical detail

### CDSS agent flow (one patient question)

```mermaid
sequenceDiagram
  actor Patient
  participant UI as Agent UI
  participant API as FastAPI /agent/run
  participant Planner as Planner
  participant Tools as CDSS tools

  Patient->>UI: Should I take berberine for PCOS?
  UI->>API: full_cycle + labs + wearable + daily log
  API->>Planner: build_plan()
  Planner->>Tools: detect_patient_intent
  Planner->>Tools: parse_lab_panel
  Planner->>Tools: score_care_gaps
  Planner->>Tools: score_layer_health
  Note over Tools: Hormones · Metabolic · Cognition · Inflammation
  Planner->>Tools: recommend_precision_nutrition
  Planner->>Tools: match_clinical_trials
  Planner->>Tools: generate_clinician_handoff
  Planner->>Tools: safety_guardrail
  Tools->>UI: summary · layers · gaps · trace
```

### Four health layers

| Layer | Signals |
|-------|---------|
| **Hormones** | LH, FSH, testosterone, estradiol, cycle pattern |
| **Metabolic** | Glucose, insulin, HOMA-IR, lipids |
| **Cognition** | Sleep, HRV, mood, daily check-in |
| **Inflammation** | Recovery, food triggers, guideline context |

### CDSS tool catalog

| Tool | Track 01 function |
|------|-------------------|
| `detect_patient_intent` | Patient Front Door — classify query |
| `parse_lab_panel` | Multimodal — lab normalization + pattern |
| `score_care_gaps` | **Triage** prioritization |
| `score_layer_health` | Diagnostic reasoning **support** (layers) |
| `retrieve_guideline_snippet` | Explainability |
| `recommend_precision_nutrition` | **Care pathways** |
| `match_clinical_trials` | Trial matching + eligibility rationale |
| `generate_clinician_handoff` | Loop closure |
| `safety_guardrail` | Not a diagnosis engine |

### Tech stack (this repo)

| Layer | Implementation |
|-------|----------------|
| Frontend | `index.html` · `agent.html` · `daily.html` · `assets/site.css` |
| API | Python **FastAPI** — `agent/server.py` |
| Agent | Planner + tools — `agent/planner.py` · `agent/orchestrator.py` |
| Memory (demo) | `data/patient-memory.json` → roadmap PostgreSQL / FHIR |
| Deploy | `render.yaml` · one port — site + API |

---

## Run locally

```bash
git clone https://github.com/AlbinaKrasykova/Hsence-.git
cd Hsence-
bash scripts/start.sh
```

| URL | Page |
|-----|------|
| http://localhost:8080 | Home — setup, morning brew |
| http://localhost:8080/agent.html | **Precision agent (CDSS demo)** |
| http://localhost:8080/daily.html | Daily ritual |

### Quick demo

1. Open `agent.html`
2. Ask: *Should I take berberine for PCOS?*
3. **Run full CDSS cycle** → intent · layers · gaps · evidence · trials · handoff · trace

```bash
curl http://localhost:8080/agent/health
```

---

## Deploy

1. Push to GitHub (this repo)
2. [Render](https://render.com) → **Blueprint** → connect repo → `render.yaml`
3. Public URL serves UI + `POST /agent/run`

See **[docs/DEPLOY.md](docs/DEPLOY.md)**

---

## Documentation

| Doc | Contents |
|-----|----------|
| **[docs/OVERVIEW.md](docs/OVERVIEW.md)** | **Full in-depth expansion of every section** |
| [docs/PITCH.md](docs/PITCH.md) | Problem, solution, distribution |
| [docs/PITCH_DECK.md](docs/PITCH_DECK.md) | 6-slide deck copy |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Mermaid diagrams + speaker script |
| [docs/diagrams/](docs/diagrams/) | **SVG architecture + agent flow** (slides) |
| [docs/TRACK01_ALIGNMENT.md](docs/TRACK01_ALIGNMENT.md) | Patient Front Door ↔ Track 01 mapping |
| [docs/CONDITION_CASES.md](docs/CONDITION_CASES.md) | PCOS · perimenopause · GDM · bone · cancer |
| [docs/DEMO.md](docs/DEMO.md) | Judge demo script |

---

## Safety

Hsence is **clinical decision support and patient education**. Supplements, medications, and trials require **clinician confirmation**. High-risk supplement queries route to **standard care first** with weak-evidence flags.

---

## License & contact

Hackathon / demo project.  
**Repository:** https://github.com/AlbinaKrasykova/Hsence-
