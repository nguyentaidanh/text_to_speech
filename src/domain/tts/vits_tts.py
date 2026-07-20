from typing import List
from src.core.interfaces.tts_engine import TTSEngine, VoiceInfo, SynthesisChunk
from src.domain.tts.base import MockTTSEngine

class AdvancedTTSEngineAdapter(TTSEngine):
    """Adapter hook for VITS, Coqui, StyleTTS2, FishSpeech, CosyVoice, XTTS engines."""

    def __init__(self, engine_id: str = "vits"):
        self._engine_id = engine_id
        self.fallback = MockTTSEngine()

    @property
    def engine_name(self) -> str:
        return self._engine_id

    async def get_available_voices(self) -> List[VoiceInfo]:
        return [
            VoiceInfo(
                id=f"{self._engine_id}-vi-default",
                name=f"{self._engine_id.upper()} Vietnamese Neural Engine",
                gender="male",
                language="vi-VN",
                description=f"Plugin adapter for {self._engine_id.upper()}",
                is_offline=True,
                style="advanced"
            )
        ]

    async def synthesize_chunk(self, chunk: SynthesisChunk) -> bytes:
        return await self.fallback.synthesize_chunk(chunk)
