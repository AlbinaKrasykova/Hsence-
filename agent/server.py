"""FastAPI server — agent API + static site (single deploy)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.elevenlabs_client import speech_to_text, text_to_speech_base64, voice_config
from agent.memory import load_memory
from agent.orchestrator import run_agent
from agent.tools.daily_coach import (
    answer_daily_question,
    parse_voice_for_cognition,
    run_conversation_turn,
)

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


class DailyChatRequest(BaseModel):
    message: str = ""
    step: str = "general"
    daily_log: dict[str, Any] | None = None


class DailyVoiceRequest(BaseModel):
    transcript: str = ""
    step: str = "voice"
    daily_log: dict[str, Any] | None = None


class DailyConversationRequest(BaseModel):
    message: str = ""
    phase: str | None = None
    daily_log: dict[str, Any] | None = None
    action: str = "turn"  # start | turn


class DailySpeakRequest(BaseModel):
    text: str


@app.get("/agent.html")
def redirect_legacy_agent():
    return RedirectResponse(url="/daily.html", status_code=302)


@app.get("/agent/health")
def health():
    vc = voice_config()
    return {
        "status": "ok",
        "agent": "hsence-precision",
        "site": "hsence",
        "elevenlabs": vc["elevenlabs_enabled"],
    }


@app.get("/agent/memory")
def get_memory():
    return load_memory()


@app.get("/agent/voice/config")
def get_voice_config():
    cfg = voice_config()
    if cfg["elevenlabs_enabled"]:
        cfg["setup_hint"] = (
            "API key must allow Text to Speech AND Speech to Text "
            "(create key at elevenlabs.io → API Keys → enable both)"
        )
    else:
        cfg["setup_hint"] = "Add ELEVENLABS_API_KEY to .env and run bash scripts/start.sh"
    return cfg


@app.post("/agent/run")
def agent_run(body: AgentRunRequest):
    return run_agent(body.event_type, body.payload or {})


@app.post("/agent/daily/chat")
def daily_chat(body: DailyChatRequest):
    memory = load_memory()
    result = answer_daily_question(
        body.message,
        body.step,
        body.daily_log or {},
        memory,
    )
    audio = text_to_speech_base64(result.get("answer", ""))
    if audio:
        result["audio_base64"] = audio
        result["tts"] = "elevenlabs"
    else:
        result["tts"] = "browser"
    result["voice"] = voice_config()
    return result


@app.post("/agent/daily/voice")
def daily_voice(body: DailyVoiceRequest):
    memory = load_memory()
    parsed = parse_voice_for_cognition(body.transcript)
    coach = answer_daily_question(
        body.transcript,
        body.step,
        body.daily_log or {},
        memory,
    )
    result = {**coach, **parsed}
    audio = text_to_speech_base64(coach["answer"])
    if audio:
        result["audio_base64"] = audio
        result["tts"] = "elevenlabs"
    return result


@app.post("/agent/daily/conversation")
def daily_conversation(body: DailyConversationRequest):
    memory = load_memory()
    result = run_conversation_turn(
        body.message,
        body.phase,
        body.daily_log or {},
        memory,
        action=body.action,
    )
    audio = text_to_speech_base64(result.get("speak_text") or result.get("answer", ""))
    if audio:
        result["audio_base64"] = audio
        result["tts"] = "elevenlabs"
    else:
        result["tts"] = "browser"
    result["voice"] = voice_config()
    return result


@app.post("/agent/daily/speak")
def daily_speak(body: DailySpeakRequest):
    audio = text_to_speech_base64(body.text)
    if not audio:
        return {"tts": "browser", "text": body.text}
    return {"tts": "elevenlabs", "audio_base64": audio, "text": body.text}


@app.post("/agent/daily/transcribe")
async def daily_transcribe(file: UploadFile = File(...)):
    vc = voice_config()
    if not vc["elevenlabs_enabled"]:
        raise HTTPException(
            status_code=503,
            detail="Add ELEVENLABS_API_KEY to .env for server-side voice (bypasses Chrome Google speech)",
        )
    data = await file.read()
    mime = file.content_type or "audio/webm"
    text, err = speech_to_text(data, mime)
    if not text:
        raise HTTPException(status_code=502, detail=err or "Could not transcribe audio — try again or type")
    return {"transcript": text, "stt": "elevenlabs"}


app.mount("/", StaticFiles(directory=str(ROOT), html=True), name="site")
