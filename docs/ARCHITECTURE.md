# Hsence — Architecture

**One-liner:** Multimodal data flows up · personalised understanding and clinician-ready actions flow down.

**Legend:** **Solid = built in this repo today** · *Dashed = solution vision / roadmap*

---

## Diagram 1 — As-built + vision (recommended for slides)

Copy into [mermaid.live](https://mermaid.live) → export PNG/SVG.

```mermaid
flowchart TB
  subgraph PFD["Patient Front Door · built"]
    CHAT[agent.html · patient chat]
    INTENT[detect_patient_intent · regex rules]
    SEARCH[Intercepts Google / Reddit / AI chat path]
  end

  subgraph INPUTS["Inputs · demo today"]
    PANEL[fake-lab-panel.json · Maya Chen PCOS]
    WEAR_DEMO[Wearable fields · agent form + memory]
    DAILY_LOG[daily.html · localStorage]
    SETUP_UI[Setup flow · UI prototype · index.html]
  end

  subgraph INPUTS_V["Inputs · vision"]
    OURA_LIVE[Oura / Apple Health OAuth]
    PDF_PARSE[Lab PDF parser]
    EHR[EHR / FHIR]
  end

  subgraph RUNTIME["Runtime · built · one port"]
    API[FastAPI · agent/server.py]
    SITE[Static HTML · index · agent · daily]
  end

  subgraph MEMORY["Memory · built"]
    JSON[(patient-memory.json)]
    TRACE[(agent_trace · intent · gaps · plan)]
  end

  subgraph MEMORY_V["Memory · vision"]
    PG[(PostgreSQL + vector store)]
  end

  subgraph CDSS["Medical Intelligence · Track 01 CDSS · built"]
    PLAN[planner.py · autonomous tool plan]
    ORCH[orchestrator.py]
    T1[parse_lab_panel]
    T2[score_care_gaps]
    T3[score_layer_health]
    T4[retrieve_guideline_snippet]
    T5[recommend_precision_nutrition]
    T6[match_clinical_trials · demo mock]
    T7[generate_clinician_handoff]
    T8[safety_guardrail]
    LAYERS[4 layers · H · M · C · I]
  end

  subgraph UI["Product surface · built"]
    HOME[Home · 5-step setup]
    AGENT[Precision agent · trace UI]
    DAILY[Daily ritual · 5-step log]
    BREW[Morning brew · condition narratives · JS]
  end

  SEARCH -.->|vision: intercept| CHAT
  CHAT --> INTENT --> API
  PANEL & WEAR_DEMO & DAILY_LOG --> JSON
  SETUP_UI --> HOME
  API --> PLAN --> ORCH
  ORCH --> T1 & T2 & T3 & T4 & T5 & T6 & T7 & T8
  T3 --> LAYERS
  JSON --> PLAN
  T8 --> JSON
  API --> AGENT
  SITE --> HOME & DAILY & BREW
  JSON --> AGENT

  OURA_LIVE & PDF_PARSE & EHR -.-> PG
  PG -.-> PLAN

  style PFD fill:#fef6e8,stroke:#BA7517
  style CDSS fill:#eeeefb,stroke:#7F77DD
  style INPUTS fill:#e8f4fc,stroke:#3B8BD4
  style MEMORY fill:#fdeee8,stroke:#D85A30
  style UI fill:#f5f5f4,stroke:#b0aca8
  style RUNTIME fill:#e8f8f0,stroke:#1D9E75
```

---

## Diagram 2 — Simplified stack (GitHub README)

```mermaid
flowchart TB
  subgraph PFD["Patient Front Door"]
    CHAT[Patient chat · intent detection]
    SEARCH[Replaces harmful search path · vision]
  end

  subgraph INGEST["Data · demo today → vision"]
    LABS[Lab panel · JSON demo → PDF parser]
    WEAR[Wearable · form fields → live OAuth]
    LOG[Daily ritual · localStorage + API]
    EHR[EHR · roadmap]
  end

  subgraph MEMORY["Health memory"]
    STORE[(patient-memory.json → PostgreSQL)]
  end

  subgraph CDSS["Track 01 CDSS · built"]
    PLAN[Autonomous planner]
    TOOLS[9 rule-based tools]
    LAYERS[4 layers · H · M · C · I]
    PATH[Pathways · ★/◈ supplements]
    TRIAL[Trial match · demo]
    HANDOFF[Clinician handoff]
    GUARD[Safety guardrails]
  end

  subgraph UI["Product · built"]
    HOME[Setup · 5 steps]
    AGENT[agent.html]
    DAILY[daily.html]
    BREW[Morning brew]
  end

  CHAT --> PLAN
  LABS & WEAR & LOG --> STORE
  EHR -.-> STORE
  STORE --> PLAN
  PLAN --> TOOLS --> LAYERS --> PATH --> TRIAL --> HANDOFF --> GUARD
  GUARD --> HOME & AGENT & DAILY & BREW
  SEARCH -.-> CHAT

  style PFD fill:#fef6e8,stroke:#BA7517
  style CDSS fill:#eeeefb,stroke:#7F77DD
  style INGEST fill:#e8f4fc,stroke:#3B8BD4
  style MEMORY fill:#fdeee8,stroke:#D85A30
```

---

## Diagram 3 — CDSS agent flow (one patient question)

```mermaid
sequenceDiagram
  actor Patient
  participant UI as agent.html
  participant API as POST /agent/run
  participant Plan as planner.py
  participant Orch as orchestrator.py
  participant Mem as patient-memory.json

  Patient->>UI: Should I take berberine for PCOS?
  UI->>API: full_cycle + profile + wearable + daily_log
  API->>Plan: build_plan()
  Plan->>Orch: 9-tool execution order
  Orch->>Mem: detect_patient_intent · supplement_self_treatment
  Orch->>Mem: parse_lab_panel · PCOS pattern · LH/FSH
  Orch->>Mem: score_care_gaps · insulin resistance
  Orch->>Mem: score_layer_health · 4 layers
  Orch->>Mem: retrieve_guideline_snippet
  Orch->>Mem: recommend_precision_nutrition · ★ inositol
  Orch->>Mem: match_clinical_trials · demo
  Orch->>Mem: generate_clinician_handoff
  Orch->>Mem: safety_guardrail
  Orch->>API: summary · layers · gaps · trace
  API->>UI: JSON render via agent-ui.js
  UI->>Patient: Show why · handoff questions
```

---

## Built today vs solution vision

| Layer | Built now (this repo) | Vision |
|-------|-------------------------|--------|
| **Runtime** | FastAPI + static HTML on **one port** (`scripts/run_app.py`) | Render/Railway production deploy |
| **Patient Front Door** | Regex intent detection · berberine double-check · trace UI | LLM intent + citation layer · search intercept |
| **Labs** | `fake-lab-panel.json` · `parse_lab_panel` tool | PDF upload · NHS/Medichecks parser |
| **Wearable** | Demo fields in agent UI + memory | Oura / Apple Health live sync |
| **Daily log** | `daily.html` → `localStorage` + POST payload | Sync to server memory automatically |
| **Memory** | `patient-memory.json` (longitudinal trace) | PostgreSQL · FHIR Patient |
| **CDSS** | Planner + 9 **rule-based** tools (no API keys) | Optional LLM for narrative; tools stay traceable |
| **Trials** | Mock eligibility demo | ClinicalTrials.gov / registry APIs |
| **Setup** | 5-step **UI prototype** on home | Real onboarding + device OAuth |
| **Morning brew** | Condition-mode **JS narratives** | LLM narrative grounded in live signals |
| **Conditions** | PCOS primary demo · GDM · bone · cancer in tools/docs | Perimenopause card + expanded modules |

---

## Layer stack (accurate)

```
┌─────────────────────────────────────────────────────────────┐
│  PRODUCT SURFACE · built                                    │
│  index.html (setup + morning brew) · agent.html · daily.html│
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PATIENT FRONT DOOR · built                                 │
│  Chat → detect_patient_intent → safety-first routing        │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CDSS AGENT · built                                         │
│  planner.py → orchestrator.py → 9 tools → guardrails.py     │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌──────────────┬──────────────┬──────────────┬────────────────┐
│  HORMONES    │  METABOLIC   │  COGNITION   │  INFLAMMATION  │
│  score_layer_health · agent/layers.py + agent/tools/labs.py │
└──────────────┴──────────────┴──────────────┴────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CONDITION MODULES · built in tools + docs                  │
│  PCOS · perimenopause · GDM · osteoporosis · ER+ survivorship│
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  HEALTH MEMORY · built → vision                             │
│  patient-memory.json (+ daily localStorage) → PostgreSQL    │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  DATA INPUTS · demo → vision                                │
│  fake-lab-panel.json · wearable fields → live APIs + EHR    │
└─────────────────────────────────────────────────────────────┘
```

---

## API surface (built)

| Endpoint | Method | Role |
|----------|--------|------|
| `/agent/health` | GET | Deploy health check |
| `/agent/memory` | GET | Load `patient-memory.json` |
| `/agent/run` | POST | Run CDSS cycle (`event_type`: `full_cycle`, `chat`, `daily_log`, …) |
| `/` · `/agent.html` · `/daily.html` | GET | Static site via `StaticFiles` |

---

## CDSS tool catalog

| Tool | File | Track 01 function |
|------|------|-------------------|
| `detect_patient_intent` | `agent/tools/intent.py` | Patient Front Door |
| `parse_lab_panel` | `agent/tools/labs.py` | Multimodal labs |
| `score_care_gaps` | `agent/tools/labs.py` | Triage |
| `score_layer_health` | `agent/tools/labs.py` | 4-layer support |
| `retrieve_guideline_snippet` | `agent/tools/guidelines.py` | Explainability |
| `recommend_precision_nutrition` | `agent/tools/nutrition.py` | Care pathways |
| `match_clinical_trials` | `agent/tools/trials.py` | Trial matching (demo) |
| `generate_clinician_handoff` | `agent/tools/clinician.py` | Loop closure |
| `safety_guardrail` | `agent/guardrails.py` | Not a diagnosis engine |

---

## Four health layers

| Layer | Signals (built) |
|-------|-----------------|
| **Hormones** | LH, FSH, testosterone, estradiol, cycle pattern |
| **Metabolic** | Glucose, insulin, HOMA-IR, lipids |
| **Cognition** | Sleep hours, HRV delta, mood, daily check-in |
| **Inflammation** | Recovery, food triggers, inflammation log |

---

## User journey → architecture mapping

| User step | Architecture touchpoint |
|-----------|-------------------------|
| **Setup 1–5** | UI prototype → vision: ingestion + memory |
| **Daily ritual** | `localStorage` + optional `POST /agent/run` (`daily_log`) |
| **Precision agent** | Full CDSS pipeline · `patient-memory.json` |
| **Morning brew** | Frontend condition narratives (not API yet) |

---

## Speaker script (~60 sec)

“Hsence runs as one FastAPI service — static site plus agent on port 8080. The Patient Front Door catches chat intent before harmful self-treatment. Demo data flows from a real-looking lab panel and wearable fields into longitudinal JSON memory. An autonomous planner runs nine traceable CDSS tools — not a black-box chatbot — scoring four health layers, triaging care gaps, and generating clinician handoff. The vision extends this with live Oura sync, PDF lab parsing, EHR, and PostgreSQL — but the architecture is already end-to-end in demo: setup story, daily ritual, agent trace, and morning brew narratives for PCOS through survivorship.”

---

## SVG diagrams (ready for slides)

| File | Contents |
|------|----------|
| [diagrams/hsence-architecture.svg](diagrams/hsence-architecture.svg) | Full stack · built + vision |
| [diagrams/hsence-agent-flow.svg](diagrams/hsence-agent-flow.svg) | 9-tool CDSS cycle |
| [diagrams/README.md](diagrams/README.md) | How to export and use |

Drag SVG into Google Slides / Canva, or preview in GitHub README.

---

## Link to pitch deck

Architecture slide: `docs/PITCH_DECK.md` · GitHub: `README.md` · Home page: `#architecture` on `index.html`
