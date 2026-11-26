"""Cloud pronunciation assessment via Azure Speech (REST API).

Azure's Pronunciation Assessment returns a per-phoneme accuracy score for a
given reference text, which is exactly what we need to judge automatically
whether the child produced the target letter correctly. We call the REST
endpoint directly (no heavy SDK) so it deploys anywhere and is easy to test.

Docs: https://learn.microsoft.com/azure/ai-services/speech-service/how-to-pronunciation-assessment
"""

from __future__ import annotations

import base64
import json

import numpy as np

from .audio import has_speech, to_wav_bytes
from .curriculum import build_glyph


def _result(passed: bool, message: str, score: float | None = None, heard: str | None = None) -> dict:
    return {"pass": passed, "score": score, "heard": heard, "message": message, "engine": "azure"}


def decide(accuracy: float | None, recognized_text: str | None, threshold: float) -> dict:
    """Map an Azure accuracy score (0..100) to our assessment result. Pure/testable."""
    if accuracy is None:
        return _result(False, "لم نتمكّن من تمييز الصوت بوضوح. حاول مرة أخرى بصوت أوضح.")
    passed = accuracy >= threshold
    score = max(0.0, min(1.0, accuracy / 100.0))
    heard = recognized_text or None
    if passed:
        message = f"أحسنت، نطقٌ صحيح! (دقّة {round(accuracy)}٪)"
    else:
        message = f"النطق يحتاج تحسيناً (دقّة {round(accuracy)}٪). استمع للنموذج وركّز على مخرج الحرف."
    return _result(passed, message, score=score, heard=heard)


class AzureAssessor:
    name = "azure"

    def __init__(
        self,
        key: str,
        region: str,
        locale: str = "ar-SA",
        pass_threshold: float = 80.0,
        timeout: float = 15.0,
    ):
        self.key = key
        self.region = region
        self.locale = locale
        self.pass_threshold = pass_threshold
        self.timeout = timeout

    def _endpoint(self) -> str:
        return (
            f"https://{self.region}.stt.speech.microsoft.com"
            f"/speech/recognition/conversation/cognitiveservices/v1"
            f"?language={self.locale}&format=detailed"
        )

    def _pa_header(self, reference_text: str) -> str:
        config = {
            "ReferenceText": reference_text,
            "GradingSystem": "HundredMark",
            "Granularity": "Phoneme",
            "Dimension": "Comprehensive",
            "EnableMiscue": False,
        }
        raw = json.dumps(config).encode("utf-8")
        return base64.b64encode(raw).decode("ascii")

    @staticmethod
    def parse_response(payload: dict) -> tuple[float | None, str | None]:
        """Extract (accuracy_score, recognized_text) from an Azure detailed response."""
        if payload.get("RecognitionStatus") != "Success":
            return None, None
        nbest = payload.get("NBest") or []
        if not nbest:
            return None, payload.get("DisplayText")
        top = nbest[0]
        pa = top.get("PronunciationAssessment", {})
        accuracy = pa.get("AccuracyScore")
        text = top.get("Display") or payload.get("DisplayText")
        return (float(accuracy) if accuracy is not None else None), text

    def assess(self, letter_id: str, harakah_id: str, signal: np.ndarray, sr: int) -> dict:
        if not has_speech(signal, sr):
            return _result(False, "لم نسمع صوتاً واضحاً. انطق الحرف بصوت مسموع.", score=0.0)

        import httpx  # already a dependency

        reference_text = build_glyph(letter_id, harakah_id)
        wav = to_wav_bytes(signal, sr)
        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Content-Type": f"audio/wav; codecs=audio/pcm; samplerate={sr}",
            "Accept": "application/json",
            "Pronunciation-Assessment": self._pa_header(reference_text),
        }
        try:
            resp = httpx.post(self._endpoint(), headers=headers, content=wav, timeout=self.timeout)
            resp.raise_for_status()
            accuracy, text = self.parse_response(resp.json())
        except Exception:
            return _result(False, "تعذّر الوصول إلى خدمة التقييم. تحقّق من الاتصال والمفتاح.")
        return decide(accuracy, text, self.pass_threshold)
