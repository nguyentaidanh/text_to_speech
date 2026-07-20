import httpx
import json
from typing import Dict, Any
from src.core.interfaces.ai_analyzer import AnalysisResult
from src.domain.ai.local.base import LocalAIAnalyzer
from src.domain.ai.local.prompt import format_local_prompt

class LlamaCppAnalyzer(LocalAIAnalyzer):
    """llama.cpp Server Local AI Provider Implementation."""

    @property
    def provider_name(self) -> str:
        return "llama_cpp"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8080)
        timeout = config.get("timeout", 30)

        url = f"http://{host}:{port}/completion"
        prompt = format_local_prompt(text)

        payload = {
            "prompt": prompt,
            "temperature": config.get("temperature", 0.2),
            "top_p": config.get("top_p", 0.9),
            "top_k": config.get("top_k", 40),
            "n_predict": config.get("max_tokens", 1024),
            "stream": False,
            "json_schema": {
                "type": "object",
                "properties": {
                    "suggested_global_emotion": {"type": "string"},
                    "segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sentence_id": {"type": "integer"},
                                "text": {"type": "string"},
                                "pause_after": {"type": "integer"},
                                "emotion": {"type": "string"},
                                "rate": {"type": "number"},
                                "pitch": {"type": "number"},
                                "emphasis": {"type": "boolean"}
                            },
                            "required": ["text", "pause_after", "emotion"]
                        }
                    }
                },
                "required": ["segments"]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("content", "")
                    return self.parse_json_response(response_text, text)
        except Exception:
            pass

        res = await self.fallback.analyze(text, config)
        res.provider = "llama_cpp_fallback_error"
        return res
