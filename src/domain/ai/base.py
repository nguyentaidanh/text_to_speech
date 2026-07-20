import json
from typing import Dict, Any, List
from src.core.interfaces.ai_analyzer import AIAnalyzer, AnalysisResult, SegmentAnalysis
from src.domain.nlp.tokenizer import SentenceTokenizer
from src.domain.nlp.pause_engine import PauseEngine
from src.domain.nlp.normalizer import VietnameseTextNormalizer

class RuleBasedAnalyzer(AIAnalyzer):
    """Fallback Analyzer when AI Mode is Disabled (MODE 1). Zero cost, 100% offline."""

    def __init__(self):
        self.tokenizer = SentenceTokenizer()
        self.pause_engine = PauseEngine()
        self.normalizer = VietnameseTextNormalizer()

    @property
    def provider_name(self) -> str:
        return "rule_based"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        multiplier = config.get("pause_multiplier", 1.0)
        paragraphs = self.tokenizer.split_paragraphs(text)
        
        segments: List[SegmentAnalysis] = []
        sent_id = 1

        for p_idx, paragraph in enumerate(paragraphs):
            is_last_paragraph = (p_idx == len(paragraphs) - 1)
            sentences = self.tokenizer.split_sentences(paragraph)
            
            for s_idx, sentence in enumerate(sentences):
                is_last_sentence = (s_idx == len(sentences) - 1)
                
                normalized = self.normalizer.normalize(sentence)
                pause_ms = self.pause_engine.calculate_sentence_pause(
                    sentence, 
                    is_last_in_paragraph=(is_last_sentence and not is_last_paragraph),
                    multiplier=multiplier
                )
                
                if is_last_sentence and is_last_paragraph:
                    pause_ms = int(self.pause_engine.rules.get("paragraph", 1000) * multiplier)

                segments.append(
                    SegmentAnalysis(
                        sentence_id=sent_id,
                        raw_text=sentence,
                        normalized_text=normalized,
                        emotion=config.get("emotion", "neutral"),
                        pitch_adjustment=config.get("pitch", 0.0),
                        speed_adjustment=config.get("speed", 1.0),
                        pause_after_ms=pause_ms,
                        emphasis_words=[]
                    )
                )
                sent_id += 1

        return AnalysisResult(
            provider="rule_based",
            is_ai_assisted=False,
            full_text=text,
            segments=segments,
            suggested_global_emotion=config.get("emotion", "neutral")
        )
