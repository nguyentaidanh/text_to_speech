import io
import math
import struct
from typing import List, Tuple
from src.core.interfaces.audio_processor import AudioProcessorInterface

class AudioProcessor(AudioProcessorInterface):
    """Audio Processing Engine for generating pause silence, stitching chunks, and adjusting volume/fade."""

    def generate_silence(self, duration_ms: int, sample_rate: int = 24000) -> bytes:
        if duration_ms <= 0:
            return b""
            
        num_samples = int(sample_rate * (duration_ms / 1000.0))
        # 16-bit mono silence (0s)
        return b"\x00\x00" * num_samples

    def stitch_chunks(
        self, 
        chunks: List[Tuple[bytes, int]],  # (audio_bytes, pause_after_ms)
        output_format: str = "mp3",
        sample_rate: int = 24000
    ) -> bytes:
        output = bytearray()
        
        for audio_bytes, pause_ms in chunks:
            if audio_bytes:
                output.extend(audio_bytes)
            if pause_ms > 0:
                silence_bytes = self.generate_silence(pause_ms, sample_rate=sample_rate)
                output.extend(silence_bytes)

        return bytes(output)
