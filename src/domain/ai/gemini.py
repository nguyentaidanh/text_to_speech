import httpx
import json
from typing import Dict, Any
from src.core.interfaces.ai_analyzer import AIAnalyzer, AnalysisResult, SegmentAnalysis
from src.domain.ai.base import RuleBasedAnalyzer

AI_PROMPT_TEMPLATE = """You are a Vietnamese Speech Synthesizer Assistant.
Analyze the following Vietnamese text and provide prosody, emotion, pause recommendations in strict JSON format.

JSON format required:
{{
  "suggested_global_emotion": "warm",
  "segments": [
    {{
      "sentence_id": 1,
      "raw_text": "...",
      "normalized_text": "...",
      "emotion": "warm",
      "pause_after_ms": 700,
      "emphasis_words": ["word1"]
    }}
  ]
}}

Input Text:
{text}
"""

class GeminiProvider(AIAnalyzer):
    """Gemini AI Provider implementation."""

    def __init__(self):
        self.fallback = RuleBasedAnalyzer()

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        api_key = config.get("api_key")
        if not api_key:
            res = await self.fallback.analyze(text, config)
            res.provider = "gemini_fallback_no_key"
            return res

        model = config.get("model", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        prompt = AI_PROMPT_TEMPLATE.format(text=text)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": config.get("temperature", 0.3), "responseMimeType": "application/json"}
        }

        try:
            async with httpx.AsyncClient(timeout=config.get("timeout", 15)) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content_str = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(content_str)
                    
                    segments = [
                        SegmentAnalysis(
                            sentence_id=item.get("sentence_id", idx + 1),
                            raw_text=item.get("raw_text", ""),
                            normalized_text=item.get("normalized_text", item.get("raw_text", "")),
                            emotion=item.get("emotion", "neutral"),
                            pause_after_ms=item.get("pause_after_ms", 700),
                            emphasis_words=item.get("emphasis_words", [])
                        )
                        for idx, item in enumerate(parsed.get("segments", []))
                    ]
                    return AnalysisResult(
                        provider="gemini",
                        is_ai_assisted=True,
                        full_text=text,
                        segments=segments,
                        suggested_global_emotion=parsed.get("suggested_global_emotion", "neutral")
                    )
        except Exception:
            pass

        res = await self.fallback.analyze(text, config)
        res.provider = "gemini_fallback_error"
        return res
