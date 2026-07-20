import httpx
import json
from typing import Dict, Any
from src.core.interfaces.ai_analyzer import AIAnalyzer, AnalysisResult, SegmentAnalysis
from src.domain.ai.base import RuleBasedAnalyzer
from src.domain.ai.gemini import AI_PROMPT_TEMPLATE

class ClaudeProvider(AIAnalyzer):
    """Anthropic Claude API Provider."""

    def __init__(self):
        self.fallback = RuleBasedAnalyzer()

    @property
    def provider_name(self) -> str:
        return "claude"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        api_key = config.get("api_key")
        if not api_key:
            res = await self.fallback.analyze(text, config)
            res.provider = "claude_fallback_no_key"
            return res

        model = config.get("model", "claude-3-haiku-20240307")
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": AI_PROMPT_TEMPLATE.format(text=text)}],
            "temperature": config.get("temperature", 0.3)
        }

        try:
            async with httpx.AsyncClient(timeout=config.get("timeout", 15)) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    content_str = data["content"][0]["text"]
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
                        provider="claude",
                        is_ai_assisted=True,
                        full_text=text,
                        segments=segments,
                        suggested_global_emotion=parsed.get("suggested_global_emotion", "neutral")
                    )
        except Exception:
            pass

        res = await self.fallback.analyze(text, config)
        res.provider = "claude_fallback_error"
        return res
