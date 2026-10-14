"""Pronunciation assessors.

Mirrors the frontend's pluggable design: a fast local check that can catch
"nothing was said", plus a reference-based discriminative check that verifies
the child produced the target letter rather than a confusable one.

Accuracy ceiling note: DTW-over-MFCC against reference recordings is a solid
classical baseline but is not as strong as a model trained on labeled
children's speech. The interface here is deliberately swappable so a trained
acoustic/GOP model can replace ReferenceDtwAssessor without touching the API.
"""

from __future__ import annotations

import glob
import os
from typing import Protocol

import numpy as np

from .audio import has_speech
from .confusables import confusables_for
from .dtw import dtw_distance
from .features import mfcc

# Reference filename convention: "{letter}__{harakah}__{index}.npy"
REF_GLOB = "*__*__*.npy"


class Assessor(Protocol):
    name: str

    def assess(self, letter_id: str, harakah_id: str, signal: np.ndarray, sr: int) -> dict: ...


def _result(passed: bool, message: str, engine: str, score: float | None = None, heard: str | None = None) -> dict:
    return {"pass": passed, "score": score, "heard": heard, "message": message, "engine": engine}


class EnergyAssessor:
    """Server-side fallback when no reference data is available."""

    name = "energy"

    def assess(self, letter_id: str, harakah_id: str, signal: np.ndarray, sr: int) -> dict:
        if not has_speech(signal, sr):
            return _result(False, "لم نسمع صوتاً واضحاً. انطق الحرف بصوت مسموع.", self.name, score=0.0)
        return _result(
            True,
            "سجّلنا محاولتك. (لا توجد مراجع صوتية بعد لتقييم المخرج تلقائياً — يؤكّد وليّ الأمر.)",
            self.name,
            score=0.5,
        )


class ReferenceDtwAssessor:
    """Compares the attempt to reference recordings of the target and its
    confusable letters using MFCC + DTW, and passes only when the attempt is
    closest to the target by a clear margin."""

    name = "dtw-reference"

    def __init__(self, references: dict[tuple[str, str], list[np.ndarray]], margin: float = 0.04):
        self.references = references
        self.margin = margin
        self._fallback = EnergyAssessor()

    def _refs_for(self, letter_id: str, harakah_id: str) -> list[np.ndarray]:
        same = self.references.get((letter_id, harakah_id), [])
        if same:
            return same
        # Fall back to any harakah of the same letter.
        out: list[np.ndarray] = []
        for (lid, _hid), feats in self.references.items():
            if lid == letter_id:
                out.extend(feats)
        return out

    def _min_distance(self, feats: np.ndarray, refs: list[np.ndarray]) -> float:
        if not refs:
            return float("inf")
        return min(dtw_distance(feats, ref) for ref in refs)

    def assess(self, letter_id: str, harakah_id: str, signal: np.ndarray, sr: int) -> dict:
        if not has_speech(signal, sr):
            return _result(False, "لم نسمع صوتاً واضحاً. انطق الحرف بصوت مسموع.", self.name, score=0.0)

        target_refs = self._refs_for(letter_id, harakah_id)
        if not target_refs:
            return self._fallback.assess(letter_id, harakah_id, signal, sr)

        feats = mfcc(signal, sr)
        d_target = self._min_distance(feats, target_refs)

        # Distance to the most-similar confusable letter.
        d_confuse = float("inf")
        nearest_confuse = None
        for other in confusables_for(letter_id):
            d = self._min_distance(feats, self._refs_for(other, harakah_id))
            if d < d_confuse:
                d_confuse, nearest_confuse = d, other

        if d_confuse == float("inf"):
            # No confusable references; judge on absolute closeness only.
            passed = d_target < 8.0
            score = float(1.0 / (1.0 + d_target))
            heard = letter_id if passed else None
            msg = "أحسنت، النطق قريب من النموذج." if passed else "حاول مرة أخرى، النطق بعيد عن النموذج."
            return _result(passed, msg, self.name, score=score, heard=heard)

        passed = d_target + self.margin < d_confuse
        total = d_target + d_confuse
        score = float(d_confuse / total) if total > 0 else 0.0
        heard = letter_id if passed else nearest_confuse
        if passed:
            msg = "أحسنت، نطقٌ صحيح للحرف."
        else:
            msg = "النطق أقرب إلى حرفٍ آخر. ركّز على مخرج الحرف وحاول مرة أخرى."
        return _result(passed, msg, self.name, score=score, heard=heard)


def load_references(directory: str) -> dict[tuple[str, str], list[np.ndarray]]:
    """Load reference MFCC arrays saved as {letter}__{harakah}__{idx}.npy."""
    refs: dict[tuple[str, str], list[np.ndarray]] = {}
    for path in glob.glob(os.path.join(directory, REF_GLOB)):
        stem = os.path.basename(path)[: -len(".npy")]
        parts = stem.split("__")
        if len(parts) < 2:
            continue
        letter_id, harakah_id = parts[0], parts[1]
        refs.setdefault((letter_id, harakah_id), []).append(np.load(path))
    return refs


def build_assessor(references_dir: str) -> Assessor:
    refs = load_references(references_dir)
    if refs:
        return ReferenceDtwAssessor(refs)
    return EnergyAssessor()
