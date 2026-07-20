import re
from typing import List

ABBREVIATIONS = [
    "TP", "Tp", "tp", "TS", "Ts", "ts", "ThS", "Th.S", "PGS", "GS",
    "BS", "Bs", "CN", "KS", "TT", "TƯ", "TW", "HĐND", "UBND",
    "V.V", "v.v", "E.g", "e.g", "I.e", "i.e", "St", "Mr", "Mrs", "Ms", "Dr"
]

class SentenceTokenizer:
    """Splits full Vietnamese text into paragraphs and sentences safely without skipping words or abbreviations."""

    def split_paragraphs(self, text: str) -> List[str]:
        if not text:
            return []
        paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
        return paragraphs if paragraphs else [text.strip()]

    def split_sentences(self, paragraph: str) -> List[str]:
        if not paragraph or not paragraph.strip():
            return []

        temp_text = paragraph
        for idx, abbr in enumerate(ABBREVIATIONS):
            temp_text = re.sub(rf'\b{abbr}\.', f'__ABBR_{idx}__', temp_text)

        temp_text = re.sub(r'(\d+)\.(\d+)', r'\1__DOT__\2', temp_text)

        raw_splits = re.split(r'(?<=[.?!;\n])\s+', temp_text)

        sentences = []
        for s in raw_splits:
            s = re.sub(r'__DOT__', '.', s)
            for idx, abbr in enumerate(ABBREVIATIONS):
                s = re.sub(rf'__ABBR_{idx}__', f'{abbr}.', s)

            s_clean = s.strip()
            if s_clean:
                sentences.append(s_clean)

        if not sentences and paragraph.strip():
            return [paragraph.strip()]

        return sentences
