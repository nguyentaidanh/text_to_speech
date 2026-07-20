import httpx
import json
from typing import Dict, Any
from src.core.interfaces.ai_analyzer import AnalysisResult
from src.domain.ai.local.base import LocalAIAnalyzer
from src.domain.ai.local.prompt import format_local_prompt

class OpenAICompatibleLocalAnalyzer(LocalAIAnalyzer):
    """Generic OpenAI-Compatible Local Endpoint Provider."""

    @property
    def provider_name(self) -> str:
        return "openai_local"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 1234)
        model = config.get("model", "local-model")
        timeout = config.get("timeout", 30)

        url = f"http://{host}:{port}/v1/chat/completions"
        prompt = format_local_prompt(text)

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.2),
            "top_p": config.get("top_p", 0.9)
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content_str = data["choices"][0]["message"]["content"]
                    return self.parse_json_response(content_str, text)
        except Exception:
            pass

        res = await self.fallback.analyze(text, config)
        res.provider = "openai_local_fallback_error"
        return res
