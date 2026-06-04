#!/usr/bin/env python3
"""Run Hsence — agent API + website on one port (local or production)."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("agent.server:app", host=host, port=port, reload=False)
