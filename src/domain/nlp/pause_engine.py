from typing import Dict, Any
from src.core.config_manager import ConfigManager

class PauseEngine:
    """Calculates pause durations in milliseconds based on punctuation and paragraph boundaries."""

    def __init__(self, config_mgr: ConfigManager = None):
        if config_mgr is None:
            config_mgr = ConfigManager()
        self.rules: Dict[str, int] = config_mgr.get_pause_rules()

    def get_pause_for_punctuation(self, punct: str, is_end_of_paragraph: bool = False, is_end_of_line: bool = False, multiplier: float = 1.0) -> int:
        base_pause = self.rules.get(".", 700)
        
        if is_end_of_paragraph:
            base_pause = self.rules.get("paragraph", 1000)
        elif is_end_of_line:
            base_pause = self.rules.get("newline", 700)
        elif punct in self.rules:
            base_pause = self.rules[punct]
            
        return int(base_pause * multiplier)

    def calculate_sentence_pause(self, sentence: str, is_last_in_paragraph: bool = False, multiplier: float = 1.0) -> int:
        sentence = sentence.strip()
        if not sentence:
            return int(self.rules.get(".", 700) * multiplier)
            
        last_char = sentence[-1]
        return self.get_pause_for_punctuation(last_char, is_end_of_paragraph=is_last_in_paragraph, multiplier=multiplier)
