import httpx
import json
from typing import Dict, Any
from src.core.interfaces.ai_analyzer import AnalysisResult
from src.domain.ai.local.base import LocalAIAnalyzer
from src.domain.ai.local.prompt import format_local_prompt

class OllamaAnalyzer(LocalAIAnalyzer):
    """Ollama Local AI Provider Implementation."""

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def analyze(self, text: str, config: Dict[str, Any]) -> AnalysisResult:
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 11434)
        model = config.get("model", "qwen2.5:7b")
        timeout = config.get("timeout", 30)

        url = f"http://{host}:{port}/api/generate"
        prompt = format_local_prompt(text)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": config.get("temperature", 0.2),
                "top_p": config.get("top_p", 0.9),
                "top_k": config.get("top_k", 40),
                "num_ctx": config.get("context_length", 4096),
                "num_gpu": config.get("gpu_layers", -1),
                "num_thread": config.get("threads", 4)
            },
            "keep_alive": config.get("keep_alive", "5m")
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "")
                    return self.parse_json_response(response_text, text)
        except Exception as e:
            # Trigger automatic failover to RuleBasedAnalyzer
            pass

        # Automatic failover if Ollama is unreachable
        res = await self.fallback.analyze(text, config)
        res.provider = "ollama_fallback_error"
        return res
