"""Letters most often confused by non-native children.

Used to make the assessment discriminative: an attempt only passes if it is
closer to the target letter than to the letters it is typically mistaken for
(e.g. ط vs ت/د, ض vs د/ظ).
"""

from __future__ import annotations

CONFUSABLES: dict[str, list[str]] = {
    "ta2": ["ta", "dal", "dad"],        # ط
    "ta": ["ta2", "dal", "tha"],        # ت
    "dad": ["dal", "za2", "ta2", "dhal"],  # ض
    "dal": ["dad", "ta2", "ta"],        # د
    "sad": ["sin", "za2"],              # ص
    "sin": ["sad", "tha", "shin"],      # س
    "za2": ["dhal", "dad", "zay"],      # ظ
    "dhal": ["za2", "zay", "dal", "tha"],  # ذ
    "tha": ["sin", "fa", "ta"],         # ث
    "ha2": ["kha", "ha"],               # ح
    "kha": ["ha2", "ghayn"],            # خ
    "ayn": ["ha2", "ghayn"],            # ع
    "ghayn": ["kha", "ayn"],            # غ
    "qaf": ["kaf", "ghayn"],            # ق
    "kaf": ["qaf"],                     # ك
    "ha": ["ha2"],                      # ه
    "zay": ["sin", "dhal", "za2"],      # ز
}


def confusables_for(letter_id: str) -> list[str]:
    return CONFUSABLES.get(letter_id, [])
