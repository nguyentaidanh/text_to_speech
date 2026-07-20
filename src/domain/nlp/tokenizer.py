import re
from typing import List

class SentenceTokenizer:
    """Splits full Vietnamese text into paragraphs and sentences while retaining punctuation context."""

    def split_paragraphs(self, text: str) -> List[str]:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        return paragraphs

    def split_sentences(self, paragraph: str) -> List[str]:
        # Split on sentence ending punctuation: . ? ! ;
        pattern = r'(?<=[.?!;])\s+'
        sentences = [s.strip() for s in re.split(pattern, paragraph) if s.strip()]
        return sentences
