from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class VoiceInfo(BaseModel):
    id: str
    name: str
    gender: str  # male, female, neutral
    language: str = "vi-VN"
    description: str = ""
    is_offline: bool = False
    style: str = "general"  # podcast, news, warm, deep, etc.

class SynthesisChunk(BaseModel):
    text: str
    voice_id: str
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    pause_after_ms: int = 700

class SynthesisResult(BaseModel):
    engine_name: str
    audio_data: bytes
    sample_rate: int = 24000
    format: str = "mp3"
    duration_seconds: float = 0.0

class TTSEngine(ABC):
    """Abstract Interface for TTS Engines (EdgeTTS, Piper, Coqui, VITS, StyleTTS2, etc.)"""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        pass

    @abstractmethod
    async def get_available_voices(self) -> List[VoiceInfo]:
        """Return list of supported voices for this engine."""
        pass

    @abstractmethod
    async def synthesize_chunk(self, chunk: SynthesisChunk) -> bytes:
        """Synthesize a single sentence/chunk into raw audio bytes (MP3/WAV)."""
        pass
