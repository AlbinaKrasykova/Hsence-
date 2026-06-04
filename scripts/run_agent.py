#!/usr/bin/env python3
"""Run Hsence precision medicine agent API."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("agent.server:app", host="127.0.0.1", port=8787, reload=False)
