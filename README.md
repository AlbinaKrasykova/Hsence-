# Hsence

Hormonal intelligence platform — static site + precision medicine agent API on **one port**.

Anyone with **Python 3.10+** can run it on Mac, Linux, or Windows. No API keys required for the demo agent.

## Run locally (fastest)

```bash
cd hormonemap
bash scripts/start.sh
```

Then open:

- http://localhost:8080 — home
- http://localhost:8080/agent.html — precision agent
- http://localhost:8080/labs.html — labs
- http://localhost:8080/daily.html — daily ritual

### Manual start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_app.py
```

Optional env:

- `PORT=9000` — change port (default `8080`)
- `HOST=0.0.0.0` — listen on all interfaces (so others on your network can open it)

## Share on your network

```bash
HOST=0.0.0.0 PORT=8080 bash scripts/start.sh
```

Others use `http://YOUR_LAN_IP:8080` (same Wi‑Fi).

## Deploy online (public URL)

1. Push this folder to GitHub.
2. [Render](https://render.com) → **New** → **Blueprint** → connect the repo.
3. Render uses `render.yaml` automatically.

Live app serves the same pages and `POST /agent/run` API.

## Health check

```bash
curl http://localhost:8080/agent/health
```

## What’s included

- `index.html`, `labs.html`, `daily.html`, `agent.html` — UI
- `agent/` — planner, tools, memory, FastAPI server
- `data/` — demo patient + sample lab panel
- `assets/` — images (protea, coffee cup)

No database setup — demo memory is `data/patient-memory.json`.
