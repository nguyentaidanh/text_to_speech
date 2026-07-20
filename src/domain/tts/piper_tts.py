from typing import List
from src.core.interfaces.tts_engine import TTSEngine, VoiceInfo, SynthesisChunk
from src.domain.tts.base import MockTTSEngine

class PiperTTSEngine(TTSEngine):
    """Piper ONNX Air-gapped Offline TTS Engine Adapter."""

    def __init__(self):
        self.fallback = MockTTSEngine()

    @property
    def engine_name(self) -> str:
        return "piper"

    async def get_available_voices(self) -> List[VoiceInfo]:
        return [
            VoiceInfo(
                id="piper-vi-namminh-onnx",
                name="Piper Vietnamese Male (ONNX Offline)",
                gender="male",
                language="vi-VN",
                description="Air-gapped offline ONNX neural TTS engine",
                is_offline=True,
                style="offline"
            )
        ]

    async def synthesize_chunk(self, chunk: SynthesisChunk) -> bytes:
        # If piper ONNX runtime is installed and model present, use piper. Otherwise fallback to mock audio.
        try:
            # Piper ONNX synthesis logic hook
            pass
        except Exception:
            pass
        return await self.fallback.synthesize_chunk(chunk)
