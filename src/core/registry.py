from typing import Dict, Type, Any, Optional
from src.core.interfaces.ai_analyzer import AIAnalyzer
from src.core.interfaces.tts_engine import TTSEngine

class PluginRegistry:
    """Plugin Registry using Factory Pattern and Dependency Injection for AI & TTS Providers."""

    _ai_providers: Dict[str, Type[AIAnalyzer]] = {}
    _tts_engines: Dict[str, Type[TTSEngine]] = {}

    @classmethod
    def register_ai_provider(cls, name: str, provider_cls: Type[AIAnalyzer]):
        cls._ai_providers[name.lower()] = provider_cls

    @classmethod
    def register_tts_engine(cls, name: str, engine_cls: Type[TTSEngine]):
        cls._tts_engines[name.lower()] = engine_cls

    @classmethod
    def get_ai_provider(cls, name: str) -> Optional[Type[AIAnalyzer]]:
        return cls._ai_providers.get(name.lower())

    @classmethod
    def get_tts_engine(cls, name: str) -> Optional[Type[TTSEngine]]:
        return cls._tts_engines.get(name.lower())

    @classmethod
    def list_ai_providers(cls) -> list[str]:
        return list(cls._ai_providers.keys())

    @classmethod
    def list_tts_engines(cls) -> list[str]:
        return list(cls._tts_engines.keys())
