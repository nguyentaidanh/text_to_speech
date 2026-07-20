import asyncio
import logging
import edge_tts
from typing import List
from src.core.interfaces.tts_engine import TTSEngine, VoiceInfo, SynthesisChunk

logger = logging.getLogger("VietTTS")

class EdgeTTSEngine(TTSEngine):
    """Microsoft Edge TTS Engine providing high quality Vietnamese Male & Female neural voices with automatic retry resilience."""

    @property
    def engine_name(self) -> str:
        return "edge_tts"

    async def get_available_voices(self) -> List[VoiceInfo]:
        return [
            VoiceInfo(
                id="vi-VN-NamMinhNeural",
                name="Nam Minh (Giọng Nam Trầm Ấm Podcast / Đọc Truyện)",
                gender="male",
                language="vi-VN",
                description="Deep, warm, natural Vietnamese male voice suitable for podcasts & audiobooks",
                is_offline=False,
                style="podcast"
            ),
            VoiceInfo(
                id="vi-VN-HoaiMyNeural",
                name="Hoài My (Giọng Nữ Ngọt Ngào, Nhẹ Nhàng & Truyền Cảm)",
                gender="female",
                language="vi-VN",
                description="Giọng nữ Tiếng Việt ngọt ngào, truyền cảm, phát âm tròn vành rõ chữ",
                is_offline=False,
                style="sweet"
            )
        ]

    async def synthesize_chunk(self, chunk: SynthesisChunk) -> bytes:
        voice = chunk.voice_id or "vi-VN-NamMinhNeural"
        
        try:
            speed_val = float(chunk.speed)
        except (ValueError, TypeError):
            speed_val = 1.0
        rate_percent = f"{int((speed_val - 1.0) * 100):+d}%"

        try:
            pitch_val = int(float(chunk.pitch))
        except (ValueError, TypeError):
            pitch_val = 0
        pitch_percent = f"{pitch_val:+d}Hz"

        clean_text = chunk.text.strip()
        logger.info(f"[EdgeTTS] Synthesizing text='{clean_text[:30]}...' voice='{voice}' rate='{rate_percent}' pitch='{pitch_percent}'")

        # 3-attempt automatic retry with exponential backoff for network/websocket resilience
        last_error = None
        for attempt in range(1, 4):
            async def _stream():
                communicate = edge_tts.Communicate(
                    text=clean_text,
                    voice=voice,
                    rate=rate_percent,
                    pitch=pitch_percent
                )
                audio_bytes = bytearray()
                async for data in communicate.stream():
                    if data["type"] == "audio":
                        audio_bytes.extend(data["data"])
                return bytes(audio_bytes)

            try:
                res = await asyncio.wait_for(_stream(), timeout=12.0)
                if res and len(res) > 0:
                    logger.info(f"[EdgeTTS] Synthesized {len(res)} bytes successfully on attempt #{attempt}")
                    return res
                else:
                    logger.warning(f"[EdgeTTS] Attempt #{attempt} returned empty audio stream")
            except Exception as err:
                last_error = err
                logger.warning(f"[EdgeTTS] Attempt #{attempt} failed: {err}")

            if attempt < 3:
                await asyncio.sleep(0.3 * attempt)

        logger.error(f"[EdgeTTS] All 3 attempts failed for text='{clean_text[:30]}...': {last_error}")
        raise last_error or ValueError(f"Failed to synthesize chunk: {clean_text[:30]}")
