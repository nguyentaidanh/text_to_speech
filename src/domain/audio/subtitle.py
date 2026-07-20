from typing import List, Dict, Any
from datetime import timedelta
from src.core.interfaces.ai_analyzer import SegmentAnalysis

def ms_to_srt_timestamp(ms: float) -> str:
    td = timedelta(milliseconds=ms)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    millis = int(ms % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

class SubtitleExporter:
    """Generates SRT Subtitle files and JSON metadata from segment analysis and audio durations."""

    def generate_srt(self, segments: List[SegmentAnalysis], segment_durations_ms: List[float]) -> str:
        srt_lines = []
        current_time_ms = 0.0

        for idx, (segment, duration_ms) in enumerate(zip(segments, segment_durations_ms), start=1):
            start_time = current_time_ms
            end_time = start_time + duration_ms
            
            start_str = ms_to_srt_timestamp(start_time)
            end_str = ms_to_srt_timestamp(end_time)

            srt_lines.append(f"{idx}")
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(segment.raw_text)
            srt_lines.append("")  # Empty line separator

            current_time_ms = end_time + segment.pause_after_ms

        return "\n".join(srt_lines)

    def generate_json_metadata(self, segments: List[SegmentAnalysis], segment_durations_ms: List[float], total_duration_seconds: float) -> Dict[str, Any]:
        items = []
        current_time_ms = 0.0

        for idx, (segment, duration_ms) in enumerate(zip(segments, segment_durations_ms), start=1):
            start_time = current_time_ms
            end_time = start_time + duration_ms

            items.append({
                "id": idx,
                "raw_text": segment.raw_text,
                "normalized_text": segment.normalized_text,
                "emotion": segment.emotion,
                "start_time_ms": start_time,
                "end_time_ms": end_time,
                "duration_ms": duration_ms,
                "pause_after_ms": segment.pause_after_ms
            })
            current_time_ms = end_time + segment.pause_after_ms

        return {
            "total_segments": len(segments),
            "total_duration_seconds": total_duration_seconds,
            "segments": items
        }
