import pytest
from src.domain.ai.local.ollama import OllamaAnalyzer
from src.domain.ai.local.llama_cpp import LlamaCppAnalyzer
from src.domain.ai.local.lm_studio import LMStudioAnalyzer
from src.domain.ai.local.vllm import VLLMAnalyzer
from src.domain.ai.local.detector import LocalModelDetector
from src.domain.ai.local.prompt import format_local_prompt
from src.domain.orchestrator import TTSOrchestrator

def test_local_prompt_formatting():
    prompt = format_local_prompt("Hôm nay trời đẹp.")
    assert "Hôm nay trời đẹp." in prompt
    assert "JSON SCHEMA:" in prompt

def test_local_json_parsing():
    analyzer = OllamaAnalyzer()
    raw_response = """```json
    {
      "suggested_global_emotion": "warm",
      "segments": [
        {
          "sentence_id": 1,
          "text": "Hôm nay trời đẹp.",
          "pause_after": 700,
          "emotion": "warm",
          "rate": 0.95,
          "pitch": 2.0,
          "emphasis": true
        }
      ]
    }
    ```"""
    result = analyzer.parse_json_response(raw_response, "Hôm nay trời đẹp.")
    assert result.is_ai_assisted is True
    assert len(result.segments) == 1
    assert result.segments[0].pause_after_ms == 700
    assert result.segments[0].emotion == "warm"

@pytest.mark.asyncio
async def test_ollama_fallback_on_offline_connection():
    analyzer = OllamaAnalyzer()
    config = {"host": "127.0.0.1", "port": 9999, "timeout": 1.0}  # Invalid port
    result = await analyzer.analyze("Xin chào Việt Nam", config)
    
    # Verify graceful failover to rule-based fallback without crashing
    assert result.is_ai_assisted is False
    assert "fallback" in result.provider

@pytest.mark.asyncio
async def test_orchestrator_local_ai_failover():
    orchestrator = TTSOrchestrator()
    config = {
        "mode": "local_ai",
        "local_ai": {
            "enabled": True,
            "provider": "ollama",
            "host": "127.0.0.1",
            "port": 9999,
            "timeout": 1.0
        }
    }
    result = await orchestrator.analyze_text("Hôm nay ngày 20/07/2026.", config)
    assert result is not None
    assert len(result.segments) >= 1
    assert "failover" in result.provider or "fallback" in result.provider

@pytest.mark.asyncio
async def test_local_model_detector():
    detector = LocalModelDetector()
    models = await detector.detect_all()
    assert isinstance(models, list)
