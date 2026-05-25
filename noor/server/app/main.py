"""FastAPI service exposing the pronunciation-assessment endpoint.

Implements the contract the frontend's ServerAssessor expects:
  POST /assess  (multipart: audio=WAV, letter, harakah)
  -> { pass, score, heard, message, engine }
"""

from __future__ import annotations

import os

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .assessor import build_assessor
from .audio import load_wav

REFERENCES_DIR = os.environ.get(
    "NOOR_REFERENCES_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "references"),
)

app = FastAPI(title="Noor Pronunciation Assessment", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the app origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSESSOR = build_assessor(REFERENCES_DIR)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "engine": ASSESSOR.name}


@app.post("/assess")
async def assess(
    audio: UploadFile,
    letter: str = Form(...),
    harakah: str = Form(...),
) -> dict:
    data = await audio.read()
    try:
        signal, sr = load_wav(data)
    except Exception:
        return {
            "pass": False,
            "score": 0.0,
            "heard": None,
            "message": "تعذّر قراءة الصوت. تأكد من إرسال ملف WAV صالح.",
            "engine": "error",
        }
    return ASSESSOR.assess(letter, harakah, signal, sr)
