from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class SegmentAnalysis(BaseModel):
    sentence_id: int
    raw_text: str
    normalized_text: str
    emotion: str = "neutral"
    pitch_adjustment: float = 0.0
    speed_adjustment: float = 1.0
    pause_after_ms: int = 700
    emphasis_words: List[str] = []

class AnalysisResult(BaseModel):
    provider: str
    is_ai_assisted: bool
    full_text: str
    segments: List[SegmentAnalysis]
    suggested_global_emotion: str = "neutral"

class AIAnalyzer(ABC):
    """Abstract Interface for AI Text Analyzers (Gemini, OpenAI, Claude, DeepSeek, Qwen, Custom)"""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        """Analyzes normalized text and returns prosody, emotion, emphasis, and pause recommendations."""
        pass
