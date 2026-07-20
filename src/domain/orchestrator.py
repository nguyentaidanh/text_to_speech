import io
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel

from src.core.registry import PluginRegistry
from src.core.config_manager import ConfigManager
from src.core.interfaces.ai_analyzer import AIAnalyzer, AnalysisResult, SegmentAnalysis
from src.core.interfaces.tts_engine import TTSEngine, SynthesisChunk, VoiceInfo

from src.domain.ai.base import RuleBasedAnalyzer
from src.domain.ai.gemini import GeminiProvider
from src.domain.ai.openai import OpenAIProvider
from src.domain.ai.claude import ClaudeProvider
from src.domain.ai.deepseek import DeepSeekProvider
from src.domain.ai.qwen import QwenProvider
from src.domain.ai.custom import CustomProvider

from src.domain.tts.base import MockTTSEngine
from src.domain.tts.edge_tts import EdgeTTSEngine
from src.domain.tts.piper_tts import PiperTTSEngine
from src.domain.tts.vits_tts import AdvancedTTSEngineAdapter

from src.domain.audio.processor import AudioProcessor
from src.domain.audio.subtitle import SubtitleExporter

class SynthesisResponse(BaseModel):
    analysis: AnalysisResult
    audio_hex: str  # Base64 or raw audio hex representation
    audio_format: str
    sample_rate: int
    duration_seconds: float
    srt_subtitles: str
    metadata_json: Dict[str, Any]

class TTSOrchestrator:
    """Core Orchestrator coordinating NLP, AI, TTS Engines, and Audio Stitching."""

    def __init__(self, config_mgr: ConfigManager = None):
        self.config_mgr = config_mgr or ConfigManager()
        self.audio_processor = AudioProcessor()
        self.subtitle_exporter = SubtitleExporter()
        self._register_default_plugins()

    def _register_default_plugins(self):
        # AI Providers
        PluginRegistry.register_ai_provider("rule_based", RuleBasedAnalyzer)
        PluginRegistry.register_ai_provider("gemini", GeminiProvider)
        PluginRegistry.register_ai_provider("openai", OpenAIProvider)
        PluginRegistry.register_ai_provider("claude", ClaudeProvider)
        PluginRegistry.register_ai_provider("deepseek", DeepSeekProvider)
        PluginRegistry.register_ai_provider("qwen", QwenProvider)
        PluginRegistry.register_ai_provider("custom", CustomProvider)

        # TTS Engines
        PluginRegistry.register_tts_engine("mock", MockTTSEngine)
        PluginRegistry.register_tts_engine("edge_tts", EdgeTTSEngine)
        PluginRegistry.register_tts_engine("piper", PiperTTSEngine)
        PluginRegistry.register_tts_engine("coqui", lambda: AdvancedTTSEngineAdapter("coqui"))
        PluginRegistry.register_tts_engine("vits", lambda: AdvancedTTSEngineAdapter("vits"))

    async def analyze_text(self, text: str, user_config: Dict[str, Any] = None) -> AnalysisResult:
        settings = self.config_mgr.settings.copy()
        if user_config:
            settings.update(user_config)

        ai_settings = settings.get("ai", {})
        ai_enabled = ai_settings.get("enabled", False)

        if not ai_enabled:
            provider_cls = PluginRegistry.get_ai_provider("rule_based")
        else:
            provider_name = ai_settings.get("provider", "gemini")
            provider_cls = PluginRegistry.get_ai_provider(provider_name) or PluginRegistry.get_ai_provider("rule_based")

        analyzer_instance: AIAnalyzer = provider_cls() if callable(provider_cls) else provider_cls
        merged_config = {**ai_settings, **settings.get("voice", {})}
        return await analyzer_instance.analyze(text, merged_config)

    async def get_all_voices(self) -> List[VoiceInfo]:
        voices: List[VoiceInfo] = []
        for engine_name in PluginRegistry.list_tts_engines():
            engine_cls = PluginRegistry.get_tts_engine(engine_name)
            if engine_cls:
                instance: TTSEngine = engine_cls() if isinstance(engine_cls, type) else engine_cls
                try:
                    engine_voices = await instance.get_available_voices()
                    voices.extend(engine_voices)
                except Exception:
                    pass
        return voices

    async def process_and_synthesize(self, text: str, user_config: Dict[str, Any] = None) -> SynthesisResponse:
        settings = self.config_mgr.settings.copy()
        if user_config:
            settings.update(user_config)

        voice_settings = settings.get("voice", {})
        engine_name = voice_settings.get("engine", "edge_tts")

        engine_cls = PluginRegistry.get_tts_engine(engine_name) or PluginRegistry.get_tts_engine("edge_tts")
        tts_engine: TTSEngine = engine_cls() if isinstance(engine_cls, type) else engine_cls

        # Step 1: Text Analysis (Rule-Based or AI)
        analysis_result = await self.analyze_text(text, user_config)

        # Step 2: Synthesize each segment chunk
        audio_chunks_with_pause: List[Tuple[bytes, int]] = []
        durations_ms: List[float] = []

        for segment in analysis_result.segments:
            chunk = SynthesisChunk(
                text=segment.normalized_text or segment.raw_text,
                voice_id=voice_settings.get("voice_id", "vi-VN-NamMinhNeural"),
                speed=voice_settings.get("speed", 1.0) * segment.speed_adjustment,
                pitch=voice_settings.get("pitch", 0.0) + segment.pitch_adjustment,
                volume=voice_settings.get("volume", 1.0),
                pause_after_ms=segment.pause_after_ms
            )

            try:
                raw_audio = await tts_engine.synthesize_chunk(chunk)
            except Exception:
                # Fallback to mock synthesis if external network fails
                mock_engine = MockTTSEngine()
                raw_audio = await mock_engine.synthesize_chunk(chunk)

            audio_chunks_with_pause.append((raw_audio, segment.pause_after_ms))
            
            # Approximate audio duration (or extract exact header)
            est_duration = max(500.0, len(segment.normalized_text.split()) * 250.0)
            durations_ms.append(est_duration)

        # Step 3: Audio Stitching with pause silences
        final_audio_bytes = self.audio_processor.stitch_chunks(
            audio_chunks_with_pause,
            output_format=settings.get("general", {}).get("output_format", "mp3"),
            sample_rate=settings.get("general", {}).get("sample_rate", 24000)
        )

        # Step 4: Subtitles & Metadata
        total_dur_sec = sum(durations_ms + [s.pause_after_ms for s in analysis_result.segments]) / 1000.0
        srt_subtitles = self.subtitle_exporter.generate_srt(analysis_result.segments, durations_ms)
        metadata_json = self.subtitle_exporter.generate_json_metadata(analysis_result.segments, durations_ms, total_dur_sec)

        return SynthesisResponse(
            analysis=analysis_result,
            audio_hex=final_audio_bytes.hex(),
            audio_format=settings.get("general", {}).get("output_format", "mp3"),
            sample_rate=settings.get("general", {}).get("sample_rate", 24000),
            duration_seconds=total_dur_sec,
            srt_subtitles=srt_subtitles,
            metadata_json=metadata_json
        )
