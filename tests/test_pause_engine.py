import pytest
from src.domain.nlp.pause_engine import PauseEngine
from src.domain.nlp.tokenizer import SentenceTokenizer

def test_pause_engine_defaults():
    engine = PauseEngine()
    assert engine.get_pause_for_punctuation(",") == 50
    assert engine.get_pause_for_punctuation(".") == 140
    assert engine.get_pause_for_punctuation(":") == 80
    assert engine.get_pause_for_punctuation(";") == 70
    assert engine.get_pause_for_punctuation("?") == 140
    assert engine.get_pause_for_punctuation("!") == 140

def test_tokenizer():
    tok = SentenceTokenizer()
    text = "Câu một. Câu hai! Câu ba?\nĐoạn hai."
    paragraphs = tok.split_paragraphs(text)
    assert len(paragraphs) == 2
    sentences = tok.split_sentences(paragraphs[0])
    assert len(sentences) == 3
