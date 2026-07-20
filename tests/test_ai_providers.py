import pytest
from src.domain.ai.gemini import GeminiProvider
from src.domain.ai.openai import OpenAIProvider
from src.domain.ai.claude import ClaudeProvider
from src.domain.ai.deepseek import DeepSeekProvider
from src.domain.ai.qwen import QwenProvider
from src.domain.ai.custom import CustomProvider

@pytest.mark.asyncio
async def test_gemini_provider_no_key():
    provider = GeminiProvider()
    res = await provider.analyze("Hôm nay ngày 20/07/2026.", {"api_key": ""})
    assert res is not None
    assert "fallback" in res.provider

@pytest.mark.asyncio
async def test_openai_provider_no_key():
    provider = OpenAIProvider()
    res = await provider.analyze("Hôm nay ngày 20/07/2026.", {"api_key": ""})
    assert res is not None
    assert "fallback" in res.provider

@pytest.mark.asyncio
async def test_claude_provider_no_key():
    provider = ClaudeProvider()
    res = await provider.analyze("Hôm nay ngày 20/07/2026.", {"api_key": ""})
    assert res is not None
    assert "fallback" in res.provider

@pytest.mark.asyncio
async def test_deepseek_provider_no_key():
    provider = DeepSeekProvider()
    res = await provider.analyze("Hôm nay ngày 20/07/2026.", {"api_key": ""})
    assert res is not None
    assert "fallback" in res.provider

@pytest.mark.asyncio
async def test_qwen_provider_no_key():
    provider = QwenProvider()
    res = await provider.analyze("Hôm nay ngày 20/07/2026.", {"api_key": ""})
    assert res is not None
    assert "fallback" in res.provider
