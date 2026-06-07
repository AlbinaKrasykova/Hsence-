"""ElevenLabs text-to-speech for the daily ritual voice agent."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any

ASSISTANT_NAME = "Anna"
DEFAULT_VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # Matilda — warm, calm female (Anna's voice)
DEFAULT_MODEL = "eleven_turbo_v2_5"
DEFAULT_STT_MODEL = "scribe_v1"
VOICE_LABELS = {
    "XrExE9yKIg1WjnnlVkGX": "Matilda",
    "XB0fDUnXU5powFXDhCwa": "Charlotte",
    "EXAVITQu4vr4xnSDxMaL": "Sarah",
    "FGY2WhTYpPnrIDTdsKH5": "Laura",
}


def voice_config() -> dict[str, Any]:
    key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    return {
        "elevenlabs_enabled": bool(key),
        "assistant_name": ASSISTANT_NAME,
        "assistant_tagline": "your personal hormone intelligence assistant",
        "stt_mode": "elevenlabs" if key else "browser",
        "voice_id": voice_id,
        "voice_name": ASSISTANT_NAME,
        "voice_model": VOICE_LABELS.get(voice_id, "Matilda"),
        "model_id": os.getenv("ELEVENLABS_MODEL_ID", DEFAULT_MODEL),
        "stt_model_id": os.getenv("ELEVENLABS_STT_MODEL_ID", DEFAULT_STT_MODEL),
        "fallback": "browser_speech",
    }


def text_to_speech_bytes(text: str) -> bytes | None:
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key or not text.strip():
        return None
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    model_id = os.getenv("ELEVENLABS_MODEL_ID", DEFAULT_MODEL)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = json.dumps(
        {
            "text": text[:2500],
            "model_id": model_id,
            "voice_settings": {"stability": 0.52, "similarity_boost": 0.78, "style": 0.12},
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("xi-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "audio/mpeg")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        print(f"[elevenlabs tts] {exc.code}: {body}")
        return None
    except (urllib.error.URLError, TimeoutError):
        return None


def text_to_speech_base64(text: str) -> str | None:
    raw = text_to_speech_bytes(text)
    if not raw:
        return None
    return base64.b64encode(raw).decode("ascii")


def _multipart_audio(
    fields: dict[str, str],
    filename: str,
    audio: bytes,
    mime: str,
) -> tuple[bytes, str]:
    boundary = "----HsenceBoundary8f7a2b1c"
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
        )
    parts.append(
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
            f'filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'
        ).encode()
    )
    parts.append(audio)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(parts), boundary


def speech_to_text(audio_bytes: bytes, mime: str = "audio/webm") -> tuple[str | None, str | None]:
    """Transcribe audio via ElevenLabs Scribe. Returns (text, error_message)."""
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        return None, "ELEVENLABS_API_KEY not set — add to .env and restart"
    if len(audio_bytes) < 500:
        return None, "Recording too short — speak longer before tapping send"
    model_id = os.getenv("ELEVENLABS_STT_MODEL_ID", DEFAULT_STT_MODEL)
    ext = "webm" if "webm" in mime else "wav"
    body, boundary = _multipart_audio(
        {"model_id": model_id, "language_code": "en"},
        f"recording.{ext}",
        audio_bytes,
        mime,
    )
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/speech-to-text",
        data=body,
        method="POST",
    )
    req.add_header("xi-api-key", api_key)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(body).get("detail", {})
            msg = detail.get("message") or body[:200]
        except json.JSONDecodeError:
            msg = body[:200]
        if "permission" in msg.lower() or exc.code == 401:
            msg = (
                "API key missing speech_to_text permission — "
                "create a new key at elevenlabs.io with Speech to Text enabled"
            )
        return None, msg
    except (urllib.error.URLError, TimeoutError) as exc:
        return None, f"Network error: {exc}"
    except json.JSONDecodeError:
        return None, "Invalid response from ElevenLabs"
    if isinstance(result.get("text"), str):
        return result["text"].strip(), None
    transcripts = result.get("transcripts") or []
    if transcripts and isinstance(transcripts[0].get("text"), str):
        return transcripts[0]["text"].strip(), None
    return None, "No transcript returned — try speaking louder"
