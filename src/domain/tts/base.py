import io
import math
import struct
from typing import List
from src.core.interfaces.tts_engine import TTSEngine, VoiceInfo, SynthesisChunk

class MockTTSEngine(TTSEngine):
    """Mock TTS Engine producing synthetic sine wave audio for zero-dependency testing & offline benchmarks."""

    @property
    def engine_name(self) -> str:
        return "mock"

    async def get_available_voices(self) -> List[VoiceInfo]:
        return [
            VoiceInfo(
                id="mock-male-deep",
                name="Vietnamese Male Deep Warm (Mock)",
                gender="male",
                language="vi-VN",
                description="Synthetic offline mock voice",
                is_offline=True,
                style="podcast"
            ),
            VoiceInfo(
                id="mock-female-warm",
                name="Vietnamese Female Warm (Mock)",
                gender="female",
                language="vi-VN",
                description="Synthetic offline mock female voice",
                is_offline=True,
                style="warm"
            )
        ]

    async def synthesize_chunk(self, chunk: SynthesisChunk) -> bytes:
        # Generate 0.5s tone audio as PCM WAV
        sample_rate = 24000
        duration = 0.5
        frequency = 440.0
        num_samples = int(sample_rate * duration)
        
        raw_pcm = bytearray()
        for i in range(num_samples):
            sample = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            raw_pcm.extend(struct.pack("<h", sample))

        # Wrap in simple WAV header
        header = bytearray()
        header.extend(b'RIFF')
        header.extend(struct.pack('<I', 36 + len(raw_pcm)))
        header.extend(b'WAVEfmt ')
        header.extend(struct.pack('<I', 16))
        header.extend(struct.pack('<H', 1))  # PCM
        header.extend(struct.pack('<H', 1))  # Mono
        header.extend(struct.pack('<I', sample_rate))
        header.extend(struct.pack('<I', sample_rate * 2))
        header.extend(struct.pack('<H', 2))
        header.extend(struct.pack('<H', 16))
        header.extend(b'data')
        header.extend(struct.pack('<I', len(raw_pcm)))

        return bytes(header + raw_pcm)
