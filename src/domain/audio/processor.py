import io
import math
import struct
import logging
from typing import List, Tuple
from src.core.interfaces.audio_processor import AudioProcessorInterface

logger = logging.getLogger("VietTTS")

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

class AudioProcessor(AudioProcessorInterface):
    """Audio Processing Engine for generating pause silence, stitching chunks, and adjusting volume/fade."""

    def generate_silence(self, duration_ms: int, sample_rate: int = 24000) -> bytes:
        if duration_ms <= 0:
            return b""
        num_samples = int(sample_rate * (duration_ms / 1000.0))
        return b"\x00\x00" * num_samples

    def stitch_chunks(
        self, 
        chunks: List[Tuple[bytes, int]],  # (audio_bytes, pause_after_ms)
        output_format: str = "mp3",
        sample_rate: int = 24000
    ) -> bytes:
        if not chunks:
            return b""

        # Use pydub to decode MP3 chunks and inject silent audio segments cleanly without frame corruption
        if HAS_PYDUB:
            try:
                combined = AudioSegment.empty()
                for audio_bytes, pause_ms in chunks:
                    if audio_bytes:
                        try:
                            seg = AudioSegment.from_file(io.BytesIO(audio_bytes))
                            combined += seg
                        except Exception as e:
                            logger.warning(f"pydub failed to decode chunk: {e}")
                    if pause_ms > 0:
                        combined += AudioSegment.silent(duration=pause_ms, frame_rate=sample_rate)

                out_buf = io.BytesIO()
                fmt = "mp3" if output_format.lower() in ["mp3", "mpeg"] else "wav"
                combined.export(out_buf, format=fmt)
                return out_buf.getvalue()
            except Exception as e:
                logger.warning(f"pydub export failed: {e}. Falling back to raw concatenation.")

        # Fallback raw byte concatenation
        output = bytearray()
        for audio_bytes, pause_ms in chunks:
            if audio_bytes:
                output.extend(audio_bytes)

        return bytes(output)
