import numpy as np

from app.azure_assessor import AzureAssessor, decide
from app.curriculum import build_glyph


def test_build_glyph():
    assert build_glyph("ba", "fatha") == "بَ"
    assert build_glyph("ta2", "damma") == "طُ"


def test_decide_pass_and_fail():
    ok = decide(92.0, "بَ", threshold=80.0)
    assert ok["pass"] is True
    assert 0.9 <= ok["score"] <= 1.0
    assert ok["engine"] == "azure"

    bad = decide(55.0, "تَ", threshold=80.0)
    assert bad["pass"] is False
    assert bad["heard"] == "تَ"


def test_decide_no_recognition():
    res = decide(None, None, threshold=80.0)
    assert res["pass"] is False
    assert res["score"] is None


def test_parse_response_success():
    payload = {
        "RecognitionStatus": "Success",
        "DisplayText": "بَ",
        "NBest": [
            {"Display": "بَ", "PronunciationAssessment": {"AccuracyScore": 88.0}},
        ],
    }
    accuracy, text = AzureAssessor.parse_response(payload)
    assert accuracy == 88.0
    assert text == "بَ"


def test_parse_response_nomatch():
    accuracy, text = AzureAssessor.parse_response({"RecognitionStatus": "NoMatch"})
    assert accuracy is None


def test_azure_silence_shortcircuits_without_network():
    # No network/key is touched because the silence guard returns first.
    assessor = AzureAssessor(key="x", region="westeurope")
    silence = np.zeros(16000, dtype=np.float32)
    res = assessor.assess("ta2", "fatha", silence, 16000)
    assert res["pass"] is False
    assert res["engine"] == "azure"
