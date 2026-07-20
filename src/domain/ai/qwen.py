import httpx
import json
from typing import Dict, Any
from src.core.interfaces.ai_analyzer import AIAnalyzer, AnalysisResult, SegmentAnalysis
from src.domain.ai.base import RuleBasedAnalyzer
from src.domain.ai.gemini import AI_PROMPT_TEMPLATE

class QwenProvider(AIAnalyzer):
    """Qwen (Alibaba Cloud / DashScope) Provider."""

    def __init__(self):
        self.fallback = RuleBasedAnalyzer()

    @property
    def provider_name(self) -> str:
        return "qwen"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        api_key = config.get("api_key")
        if not api_key:
            res = await self.fallback.analyze(text, config)
            res.provider = "qwen_fallback_no_key"
            return res

        model = config.get("model", "qwen-turbo")
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": AI_PROMPT_TEMPLATE.format(text=text)}],
            "response_format": {"type": "json_object"},
            "temperature": config.get("temperature", 0.3)
        }

        try:
            async with httpx.AsyncClient(timeout=config.get("timeout", 15)) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    content_str = data["choices"][0]["message"]["content"]
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
                        provider="qwen",
                        is_ai_assisted=True,
                        full_text=text,
                        segments=segments,
                        suggested_global_emotion=parsed.get("suggested_global_emotion", "neutral")
                    )
        except Exception:
            pass

        res = await self.fallback.analyze(text, config)
        res.provider = "qwen_fallback_error"
        return res
