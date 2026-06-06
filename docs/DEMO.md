# Hsence — Demo script

## Before you start

```bash
bash scripts/start.sh
```

Open **http://localhost:8080/agent.html**

---

## Script A — Precision agent (CDSS)

**Say:** “Maya has PCOS. She was dismissed by her GP. She asks about berberine.”

1. Leave default chat: *Should I take berberine for PCOS? My labs show high testosterone.*
2. Click **Run full CDSS cycle** (or equivalent run button).
3. Walk through:
   - **Intent** badge (supplement / evidence question)
   - **Four layers** — hormones, metabolic, cognition, inflammation
   - **Care gaps** — what’s missing from standard care
   - **Supplements** — ★ / ◈ evidence codes
   - **Trials** — criterion-by-criterion match (demo)
   - **Questions for your doctor**
   - **Agent trace** — tools called in order

**Close:** “This is decision support and handoff — not diagnosis or prescribing.”

---

## Script B — Patient journey (home → daily)

1. **Home** (`/`) — hero, how it works, **setup flow** (wearable + lab upload prototype).
2. **Morning brew** section — switch PCOS / perimenopause modes.
3. **Daily ritual** — log mood, supplements, one meal; show review timeline.

---

## Personas (demo data)

| Name | Condition | Use in demo |
|------|-----------|-------------|
| Maya Chen | PCOS | Default agent inputs |
| Sofia | Gestational diabetes | Daily / quotes on home |
| Helen | Osteoporosis | Condition modules on home |
| Rachel | Survivorship | Trial / surveillance language |

Sample lab PDF: `data/Maya-Chen-Sample-Lab-Report.pdf`  
Web report: `sample-lab-report.html`
