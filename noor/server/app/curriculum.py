"""Backend copy of the letter glyph map, used to build the reference text for
cloud assessment when the frontend does not send a glyph. Ids must match
src/data/curriculum.ts.
"""

from __future__ import annotations

LETTER_CHARS: dict[str, str] = {
    "alif": "ا", "ba": "ب", "ta": "ت", "tha": "ث", "jim": "ج", "ha2": "ح",
    "kha": "خ", "dal": "د", "dhal": "ذ", "ra": "ر", "zay": "ز", "sin": "س",
    "shin": "ش", "sad": "ص", "dad": "ض", "ta2": "ط", "za2": "ظ", "ayn": "ع",
    "ghayn": "غ", "fa": "ف", "qaf": "ق", "kaf": "ك", "lam": "ل", "mim": "م",
    "nun": "ن", "ha": "ه", "waw": "و", "ya": "ي",
}

HARAKAH_MARKS: dict[str, str] = {
    "fatha": "َ",  # ـَ
    "damma": "ُ",  # ـُ
    "kasra": "ِ",  # ـِ
}


def build_glyph(letter_id: str, harakah_id: str) -> str:
    """Return the letter with its harakah applied, e.g. ('ba','fatha') -> 'بَ'."""
    char = LETTER_CHARS.get(letter_id, "")
    mark = HARAKAH_MARKS.get(harakah_id, "")
    return char + mark
