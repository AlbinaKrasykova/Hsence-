"""FastAPI server — agent API + static site (single deploy)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.memory import load_memory
from agent.orchestrator import run_agent

ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title="Hsence Precision Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentRunRequest(BaseModel):
    event_type: str = "full_cycle"
    payload: dict[str, Any] | None = None


@app.get("/agent/health")
def health():
    return {"status": "ok", "agent": "hsence-precision", "site": "hsence"}


@app.get("/agent/memory")
def get_memory():
    return load_memory()


@app.post("/agent/run")
def agent_run(body: AgentRunRequest):
    return run_agent(body.event_type, body.payload or {})


app.mount("/", StaticFiles(directory=str(ROOT), html=True), name="site")
