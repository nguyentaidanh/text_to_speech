import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.core.interfaces.ai_analyzer import AIAnalyzer, AnalysisResult, SegmentAnalysis
from src.domain.ai.base import RuleBasedAnalyzer
from src.domain.ai.local.prompt import format_local_prompt

class LocalModelInfo(BaseModel):
    name: str
    size_mb: Optional[float] = None
    quantization: Optional[str] = None
    provider: str = "ollama"
    status: str = "available"

class LocalAIAnalyzer(AIAnalyzer, ABC):
    """Abstract Base Class for Offline Local AI Speech Analyzers."""

    def __init__(self):
        self.fallback = RuleBasedAnalyzer()

    def parse_json_response(self, raw_content: str, full_text: str) -> AnalysisResult:
        """Parses model text response and extracts valid JSON payload."""
        cleaned = raw_content.strip()
        # Remove potential markdown code fences ```json ... ```
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            segments = []
            for idx, item in enumerate(parsed.get("segments", []), start=1):
                segments.append(
                    SegmentAnalysis(
                        sentence_id=item.get("sentence_id", idx),
                        raw_text=item.get("text", item.get("raw_text", "")),
                        normalized_text=item.get("text", item.get("normalized_text", "")),
                        emotion=item.get("emotion", "neutral"),
                        pitch_adjustment=float(item.get("pitch", 0.0)),
                        speed_adjustment=float(item.get("rate", 1.0)),
                        pause_after_ms=int(item.get("pause_after", item.get("pause_after_ms", 700))),
                        emphasis_words=[] if not item.get("emphasis", False) else ["emphasis"]
                    )
                )

            if not segments:
                raise ValueError("No valid segments in model JSON")

            return AnalysisResult(
                provider=self.provider_name,
                is_ai_assisted=True,
                full_text=full_text,
                segments=segments,
                suggested_global_emotion=parsed.get("suggested_global_emotion", "neutral")
            )
        except Exception:
            raise ValueError(f"Failed to parse JSON response from {self.provider_name}: {raw_content[:200]}")
