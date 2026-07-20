import httpx
import json
from typing import Dict, Any
from src.core.interfaces.ai_analyzer import AIAnalyzer, AnalysisResult, SegmentAnalysis
from src.domain.ai.base import RuleBasedAnalyzer

class CustomProvider(AIAnalyzer):
    """Custom REST API Provider for local LLMs (Ollama, LM Studio, VLLM, etc.)."""

    def __init__(self):
        self.fallback = RuleBasedAnalyzer()

    @property
    def provider_name(self) -> str:
        return "custom"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        custom_url = config.get("custom_url")
        if not custom_url:
            res = await self.fallback.analyze(text, config)
            res.provider = "custom_fallback_no_url"
            return res

        api_key = config.get("api_key", "")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "text": text,
            "config": config
        }

        try:
            async with httpx.AsyncClient(timeout=config.get("timeout", 15)) as client:
                resp = await client.post(custom_url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    segments = [
                        SegmentAnalysis(
                            sentence_id=item.get("sentence_id", idx + 1),
                            raw_text=item.get("raw_text", ""),
                            normalized_text=item.get("normalized_text", item.get("raw_text", "")),
                            emotion=item.get("emotion", "neutral"),
                            pause_after_ms=item.get("pause_after_ms", 700),
                            emphasis_words=item.get("emphasis_words", [])
                        )
                        for idx, item in enumerate(data.get("segments", []))
                    ]
                    return AnalysisResult(
                        provider="custom",
                        is_ai_assisted=True,
                        full_text=text,
                        segments=segments,
                        suggested_global_emotion=data.get("suggested_global_emotion", "neutral")
                    )
        except Exception:
            pass

        res = await self.fallback.analyze(text, config)
        res.provider = "custom_fallback_error"
        return res
