from abc import ABC, abstractmethod
from typing import List, Tuple

class AudioProcessorInterface(ABC):
    @abstractmethod
    def generate_silence(self, duration_ms: int, sample_rate: int = 24000) -> bytes:
        """Generate silent audio chunk of given duration."""
        pass

    @abstractmethod
    def stitch_chunks(
        self, 
        chunks: List[Tuple[bytes, int]],  # (audio_bytes, pause_after_ms)
        output_format: str = "mp3",
        sample_rate: int = 24000
    ) -> bytes:
        """Combine audio chunks with pause durations into a single audio output."""
        pass
