import io
import wave

import numpy as np

from app.assessor import EnergyAssessor, ReferenceDtwAssessor, build_assessor, load_references
from app.audio import load_wav, rms
from app.dtw import dtw_distance
from app.features import mfcc


def chirp(f0: float, f1: float, dur: float = 0.6, sr: int = 16000, amp: float = 0.3) -> np.ndarray:
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    phase = 2 * np.pi * (f0 * t + (f1 - f0) / (2 * dur) * t ** 2)
    return amp * np.sin(phase)


def make_wav_bytes(signal: np.ndarray, sr: int = 16000) -> bytes:
    pcm = (np.clip(signal, -1, 1) * 32767).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def test_load_wav_roundtrip():
    sig = chirp(200, 800)
    signal, sr = load_wav(make_wav_bytes(sig))
    assert sr == 16000
    assert signal.shape[0] == sig.shape[0]
    assert rms(signal) > 0.1


def test_mfcc_shape():
    feats = mfcc(chirp(200, 800), 16000)
    assert feats.ndim == 2
    assert feats.shape[1] == 13
    assert feats.shape[0] > 10


def test_dtw_self_vs_different():
    a = mfcc(chirp(200, 900), 16000)
    b = mfcc(chirp(2200, 2900), 16000)
    assert dtw_distance(a, a) < dtw_distance(a, b)


def test_energy_assessor_silence_vs_speech():
    assessor = EnergyAssessor()
    silence = np.zeros(16000, dtype=np.float32)
    assert assessor.assess("ta2", "fatha", silence, 16000)["pass"] is False
    speech, sr = load_wav(make_wav_bytes(chirp(200, 800)))
    assert assessor.assess("ta2", "fatha", speech, sr)["pass"] is True


def test_reference_dtw_discriminates_target_from_confusable():
    # Synthetic stand-ins: ط = low chirp, ت (a confusable of ط) = high chirp.
    refs = {
        ("ta2", "fatha"): [mfcc(chirp(200, 900), 16000)],
        ("ta", "fatha"): [mfcc(chirp(2200, 2900), 16000)],
    }
    assessor = ReferenceDtwAssessor(refs)

    good = chirp(200, 900) + 0.01 * np.random.RandomState(0).randn(int(16000 * 0.6))
    res_good = assessor.assess("ta2", "fatha", good, 16000)
    assert res_good["pass"] is True
    assert res_good["heard"] == "ta2"

    wrong = chirp(2200, 2900) + 0.01 * np.random.RandomState(1).randn(int(16000 * 0.6))
    res_wrong = assessor.assess("ta2", "fatha", wrong, 16000)
    assert res_wrong["pass"] is False
    assert res_wrong["heard"] == "ta"


def test_build_assessor_without_references(tmp_path):
    assessor = build_assessor(str(tmp_path))
    assert assessor.name == "energy"


def test_load_references_roundtrip(tmp_path):
    feats = mfcc(chirp(200, 900), 16000)
    np.save(tmp_path / "ta2__fatha__1.npy", feats)
    refs = load_references(str(tmp_path))
    assert ("ta2", "fatha") in refs
    assert len(refs[("ta2", "fatha")]) == 1


def test_api_health_and_assess():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    health = client.get("/health").json()
    assert health["status"] == "ok"

    wav = make_wav_bytes(chirp(200, 800))
    resp = client.post(
        "/assess",
        files={"audio": ("attempt.wav", wav, "audio/wav")},
        data={"letter": "ta2", "harakah": "fatha"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "pass" in body and "engine" in body
