# Deploy Hsence

## GitHub

Repo: **https://github.com/AlbinaKrasykova/Hsence-**

```bash
git clone https://github.com/AlbinaKrasykova/Hsence-.git
cd Hsence-
```

Push updates:

```bash
git add .
git commit -m "Your message"
git push origin main
```

---

## Render (recommended — free tier)

1. Sign in at [render.com](https://render.com) with GitHub.
2. **New** → **Blueprint**.
3. Connect repository `AlbinaKrasykova/Hsence-`, branch `main`.
4. Render reads `render.yaml` and creates the `hsence` web service.
5. Wait for build (~2–5 min). Open the `.onrender.com` URL.

**Health check:** `GET /agent/health`

**Start command (in blueprint):** `python scripts/run_app.py`

---

## Railway (alternative)

`railway.toml` and `Procfile` are included. Link the repo in Railway dashboard and deploy; set start command to `python scripts/run_app.py`.

---

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `8080` | HTTP port (set by Render automatically) |
| `HOST` | `0.0.0.0` | Bind address |

No API keys needed for the bundled demo agent.

---

## Verify deployment

```bash
curl https://YOUR-SERVICE.onrender.com/agent/health
```

Browser:

- `https://YOUR-SERVICE.onrender.com/`
- `https://YOUR-SERVICE.onrender.com/agent.html`
- `https://YOUR-SERVICE.onrender.com/daily.html`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Blueprint not found | Ensure `render.yaml` is on `main` |
| Cold start slow (free tier) | First request after idle may take 30–60s |
| Agent UI empty | Wait for health check; hard-refresh |
| 404 on pages | Confirm `agent/server.py` mounts static files at `/` |
