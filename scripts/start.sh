#!/usr/bin/env bash
# Start Hsence — website + agent on one port (default 8080)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${ROOT}/.venv/bin/python"
PIP="${ROOT}/.venv/bin/pip"

if [[ ! -x "$PY" ]]; then
  echo "Creating virtualenv..."
  python3 -m venv .venv
fi

"$PIP" install -q -r requirements.txt

PORT="${PORT:-8080}"
echo "Starting Hsence at http://127.0.0.1:${PORT}"
echo "  Agent UI → http://127.0.0.1:${PORT}/agent.html"
echo "  Labs     → http://127.0.0.1:${PORT}/labs.html"
echo ""

exec "$PY" scripts/run_app.py
