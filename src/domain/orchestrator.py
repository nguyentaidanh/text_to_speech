import io
import logging
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

# Local AI Providers
from src.domain.ai.local.ollama import OllamaAnalyzer
from src.domain.ai.local.llama_cpp import LlamaCppAnalyzer
from src.domain.ai.local.lm_studio import LMStudioAnalyzer
from src.domain.ai.local.vllm import VLLMAnalyzer
from src.domain.ai.local.custom_local import OpenAICompatibleLocalAnalyzer

from src.domain.tts.base import MockTTSEngine
from src.domain.tts.edge_tts import EdgeTTSEngine
from src.domain.tts.piper_tts import PiperTTSEngine
from src.domain.tts.vits_tts import AdvancedTTSEngineAdapter

from src.domain.audio.processor import AudioProcessor
from src.domain.audio.subtitle import SubtitleExporter

logger = logging.getLogger("VietTTS")

class SynthesisResponse(BaseModel):
    analysis: AnalysisResult
    audio_hex: str
    audio_format: str
    sample_rate: int
    duration_seconds: float
    srt_subtitles: str
    metadata_json: Dict[str, Any]

class TTSOrchestrator:
    """Core Orchestrator coordinating NLP, AI (Cloud & Local), TTS Engines, and Audio Stitching."""

    def __init__(self, config_mgr: ConfigManager = None):
        self.config_mgr = config_mgr or ConfigManager()
        self.audio_processor = AudioProcessor()
        self.subtitle_exporter = SubtitleExporter()
        self._cache: Dict[str, bytes] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        PluginRegistry.register_ai_provider("rule_based", RuleBasedAnalyzer)
        PluginRegistry.register_ai_provider("gemini", GeminiProvider)
        PluginRegistry.register_ai_provider("openai", OpenAIProvider)
        PluginRegistry.register_ai_provider("claude", ClaudeProvider)
        PluginRegistry.register_ai_provider("deepseek", DeepSeekProvider)
        PluginRegistry.register_ai_provider("qwen", QwenProvider)
        PluginRegistry.register_ai_provider("custom", CustomProvider)

        PluginRegistry.register_ai_provider("ollama", OllamaAnalyzer)
        PluginRegistry.register_ai_provider("llama_cpp", LlamaCppAnalyzer)
        PluginRegistry.register_ai_provider("lm_studio", LMStudioAnalyzer)
        PluginRegistry.register_ai_provider("vllm", VLLMAnalyzer)
        PluginRegistry.register_ai_provider("openai_local", OpenAICompatibleLocalAnalyzer)

        PluginRegistry.register_tts_engine("mock", MockTTSEngine)
        PluginRegistry.register_tts_engine("edge_tts", EdgeTTSEngine)
        PluginRegistry.register_tts_engine("piper", PiperTTSEngine)
        PluginRegistry.register_tts_engine("coqui", lambda: AdvancedTTSEngineAdapter("coqui"))
        PluginRegistry.register_tts_engine("vits", lambda: AdvancedTTSEngineAdapter("vits"))

    async def analyze_text(self, text: str, user_config: Dict[str, Any] = None) -> AnalysisResult:
        settings = self.config_mgr.settings.copy()
        if user_config:
            for k, v in user_config.items():
                if isinstance(v, dict) and k in settings and isinstance(settings[k], dict):
                    settings[k].update(v)
                else:
                    settings[k] = v

        mode = settings.get("mode", "rule_based")
        local_ai_settings = settings.get("local_ai", {})
        cloud_ai_settings = settings.get("ai", {})
        voice_settings = settings.get("voice", {})

        merged_config = {**voice_settings}
        if "pause_rules" in settings:
            merged_config["pause_rules"] = settings["pause_rules"]

        if mode == "rule_based":
            provider_cls = PluginRegistry.get_ai_provider("rule_based")
        elif mode == "cloud_ai":
            provider_name = cloud_ai_settings.get("provider", "gemini")
            provider_cls = PluginRegistry.get_ai_provider(provider_name)
            merged_config.update(cloud_ai_settings)
        elif mode == "local_ai":
            provider_name = local_ai_settings.get("provider", "ollama")
            provider_cls = PluginRegistry.get_ai_provider(provider_name)
            merged_config.update(local_ai_settings)
        else:
            provider_cls = PluginRegistry.get_ai_provider("rule_based")

        if not provider_cls:
            provider_cls = PluginRegistry.get_ai_provider("rule_based")

        analyzer_instance: AIAnalyzer = provider_cls() if callable(provider_cls) else provider_cls

        logger.info(f"[Orchestrator] Analyzing text ({len(text)} chars) with mode={mode}")
        try:
            res = await analyzer_instance.analyze(text, merged_config)
            logger.info(f"[Orchestrator] Analysis success with provider={res.provider}, segments={len(res.segments)}")
            return res
        except Exception as e:
            logger.warning(f"[Orchestrator] Provider failed: {e}. Falling back to RuleBasedAnalyzer")
            fallback_cls = PluginRegistry.get_ai_provider("rule_based")
            fallback_instance = fallback_cls() if callable(fallback_cls) else fallback_cls
            res = await fallback_instance.analyze(text, merged_config)
            res.provider = "rule_based_failover"
            return res

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

        logger.info(f"[Orchestrator] Step 1: Text Analysis starting for text length {len(text)}...")
        analysis_result = await self.analyze_text(text, user_config)

        logger.info(f"[Orchestrator] Step 2: Synthesizing {len(analysis_result.segments)} segments concurrently in parallel using engine '{engine_name}'...")

        async def _synthesize_single_segment(idx: int, segment) -> Tuple[int, bytes, float]:
            chunk_text = segment.normalized_text or segment.raw_text
            voice_id = voice_settings.get("voice_id", "vi-VN-HoaiMyNeural")
            speed = voice_settings.get("speed", 0.95) * segment.speed_adjustment
            pitch = voice_settings.get("pitch", 2.0) + segment.pitch_adjustment
            
            chunk = SynthesisChunk(
                text=chunk_text,
                voice_id=voice_id,
                speed=speed,
                pitch=pitch,
                volume=voice_settings.get("volume", 1.0),
                pause_after_ms=segment.pause_after_ms
            )

            cache_key = f"{engine_name}:{voice_id}:{chunk_text}:{speed:.2f}:{pitch:.1f}"
            if cache_key in self._cache:
                logger.info(f"[Orchestrator] Cache HIT for segment #{idx} ('{chunk_text[:20]}...')")
                raw_audio = self._cache[cache_key]
            else:
                try:
                    raw_audio = await tts_engine.synthesize_chunk(chunk)
                    if raw_audio:
                        self._cache[cache_key] = raw_audio
                except Exception as err:
                    logger.warning(f"[Orchestrator] Chunk #{idx} failed with {tts_engine.engine_name}: {err}. Falling back to MockTTSEngine.")
                    mock_engine = MockTTSEngine()
                    raw_audio = await mock_engine.synthesize_chunk(chunk)

            est_duration = max(500.0, len(chunk_text.split()) * 250.0)
            return idx, raw_audio, est_duration

        tasks = [
            _synthesize_single_segment(idx, segment)
            for idx, segment in enumerate(analysis_result.segments, start=1)
        ]
        import asyncio
        results = await asyncio.gather(*tasks)

        results.sort(key=lambda x: x[0])
        audio_chunks_with_pause: List[Tuple[bytes, int]] = [(r[1], analysis_result.segments[r[0]-1].pause_after_ms) for r in results]
        durations_ms: List[float] = [r[2] for r in results]

        logger.info(f"[Orchestrator] Step 3: Stitching {len(audio_chunks_with_pause)} audio chunks...")
        final_audio_bytes = self.audio_processor.stitch_chunks(
            audio_chunks_with_pause,
            output_format=settings.get("general", {}).get("output_format", "mp3"),
            sample_rate=settings.get("general", {}).get("sample_rate", 24000)
        )

        total_dur_sec = sum(durations_ms + [s.pause_after_ms for s in analysis_result.segments]) / 1000.0
        srt_subtitles = self.subtitle_exporter.generate_srt(analysis_result.segments, durations_ms)
        metadata_json = self.subtitle_exporter.generate_json_metadata(analysis_result.segments, durations_ms, total_dur_sec)

        logger.info(f"[Orchestrator] Synthesis complete! Output size: {len(final_audio_bytes)} bytes, Duration: {total_dur_sec:.2f}s")

        return SynthesisResponse(
            analysis=analysis_result,
            audio_hex=final_audio_bytes.hex(),
            audio_format=settings.get("general", {}).get("output_format", "mp3"),
            sample_rate=settings.get("general", {}).get("sample_rate", 24000),
            duration_seconds=total_dur_sec,
            srt_subtitles=srt_subtitles,
            metadata_json=metadata_json
        )
