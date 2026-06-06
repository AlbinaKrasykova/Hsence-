# Hsence

**Hormonal intelligence platform** — static site + precision medicine agent API on **one port**.

Sync labs and wearable once. Hsence explains your hormonal state, surfaces personal risks, and builds a supplement and daily plan matched to your biology. Includes an autonomous **clinical decision support** agent for intent detection, care-gap triage, trial matching, and clinician handoff.

> **Not a diagnosis engine.** Decision support and education only.

---

## Problem → Solution

| Problem | Hsence solution |
|---------|-----------------|
| Dismissed or unexplained lab results | Multimodal read: labs + wearable + daily signals, plain language |
| Siloed hormone / metabolic / mood care | Four-layer agent + unified home setup flow |
| Forum-only answers between visits | Evidence-graded supplements, GP questions, trial criteria |
| Overwhelming health dashboards | Morning brew + daily ritual — low cognitive load |

Full pitch, distribution, and safety scope: **[docs/PITCH.md](docs/PITCH.md)**  
Demo script: **[docs/DEMO.md](docs/DEMO.md)**  
Deploy guide: **[docs/DEPLOY.md](docs/DEPLOY.md)**

---

## Live & repo

- **GitHub:** https://github.com/AlbinaKrasykova/Hsence-
- **Deploy:** Connect repo on [Render](https://render.com) → Blueprint → `render.yaml` → public URL (e.g. `https://hsence.onrender.com`)

---

## Run locally

```bash
git clone https://github.com/AlbinaKrasykova/Hsence-.git
cd Hsence-
bash scripts/start.sh
```

Then open:

| URL | Page |
|-----|------|
| http://localhost:8080 | Home — setup flow, morning brew, features |
| http://localhost:8080/agent.html | Precision agent (CDSS demo) |
| http://localhost:8080/daily.html | Daily ritual |

### Manual start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_app.py
```

Optional: `PORT=9000` · `HOST=0.0.0.0` for LAN sharing.

---

## Health check

```bash
curl http://localhost:8080/agent/health
```

---

## What’s in the repo

| Path | Purpose |
|------|---------|
| `index.html`, `agent.html`, `daily.html` | UI |
| `assets/site.css`, `scripts/nav.js` | Shared layout + nav |
| `agent/` | FastAPI server, planner, tools, memory |
| `data/` | Demo patient + sample lab panel |
| `docs/` | Pitch, demo script, deploy |
| `render.yaml` | Render blueprint |

No database — demo memory is `data/patient-memory.json`. No API keys required for the demo agent.

---

## Quick demo (agent)

1. Open `agent.html`
2. Chat: *Should I take berberine for PCOS?*
3. Run full CDSS cycle → layers, gaps, evidence, trials, handoff

See **[docs/DEMO.md](docs/DEMO.md)** for the full judge script.
