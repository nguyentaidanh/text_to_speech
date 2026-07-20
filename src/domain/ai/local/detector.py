import httpx
from typing import List
from src.domain.ai.local.base import LocalModelInfo

class LocalModelDetector:
    """Auto-detects installed models from local LLM endpoints (Ollama, LM Studio, vLLM, OpenAI local)."""

    async def detect_ollama_models(self, host: str = "127.0.0.1", port: int = 11434, timeout: float = 3.0) -> List[LocalModelInfo]:
        url = f"http://{host}:{port}/api/tags"
        models: List[LocalModelInfo] = []
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("models", []):
                        size_mb = round(item.get("size", 0) / (1024 * 1024), 2)
                        details = item.get("details", {})
                        quant = details.get("quantization_level", "Unknown")
                        models.append(
                            LocalModelInfo(
                                name=item.get("name", "unknown"),
                                size_mb=size_mb,
                                quantization=quant,
                                provider="ollama",
                                status="available"
                            )
                        )
        except Exception:
            pass
        return models

    async def detect_openai_local_models(self, base_url: str = "http://127.0.0.1:1234/v1", provider_label: str = "lm_studio", timeout: float = 3.0) -> List[LocalModelInfo]:
        url = f"{base_url.rstrip('/')}/models"
        models: List[LocalModelInfo] = []
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("data", []):
                        models.append(
                            LocalModelInfo(
                                name=item.get("id", "local-model"),
                                provider=provider_label,
                                status="available"
                            )
                        )
        except Exception:
            pass
        return models

    async def detect_all(self, config: dict = None) -> List[LocalModelInfo]:
        all_models: List[LocalModelInfo] = []
        
        # 1. Detect Ollama
        ollama_models = await self.detect_ollama_models()
        all_models.extend(ollama_models)

        # 2. Detect LM Studio / OpenAI Local (Port 1234)
        lm_models = await self.detect_openai_local_models("http://127.0.0.1:1234/v1", "lm_studio")
        all_models.extend(lm_models)

        # 3. Detect vLLM (Port 8000)
        vllm_models = await self.detect_openai_local_models("http://127.0.0.1:8000/v1", "vllm")
        all_models.extend(vllm_models)

        return all_models
