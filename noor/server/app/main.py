"""FastAPI service exposing the pronunciation-assessment endpoint.

Implements the contract the frontend's ServerAssessor expects:
  POST /assess  (multipart: audio=WAV, letter, harakah)
  -> { pass, score, heard, message, engine }
"""

from __future__ import annotations

import os

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .assessor import Assessor, EnergyAssessor, build_assessor
from .audio import load_wav

REFERENCES_DIR = os.environ.get(
    "NOOR_REFERENCES_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "references"),
)

# Built frontend (noor/dist). When present, the API also serves the app so the
# whole thing runs from a single origin/URL — no separate static host or CORS.
STATIC_DIR = os.environ.get(
    "NOOR_STATIC_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dist"),
)


def select_assessor() -> Assessor:
    """Pick the engine from the environment.

    NOOR_ENGINE: auto (default) | azure | dtw | energy
    Azure also needs AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.
    """
    engine = os.environ.get("NOOR_ENGINE", "auto").lower()
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if engine in ("azure", "auto") and key and region:
        from .azure_assessor import AzureAssessor

        return AzureAssessor(
            key=key,
            region=region,
            locale=os.environ.get("NOOR_AZURE_LOCALE", "ar-SA"),
            pass_threshold=float(os.environ.get("NOOR_PASS_THRESHOLD", "80")),
        )
    if engine == "azure":
        # Azure was explicitly requested but not configured.
        return EnergyAssessor()
    if engine == "energy":
        return EnergyAssessor()
    return build_assessor(REFERENCES_DIR)


app = FastAPI(title="Noor Pronunciation Assessment", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the app origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSESSOR = select_assessor()


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


# Mounted last so /health and /assess take precedence over the static catch-all.
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
