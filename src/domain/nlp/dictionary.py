import re
from typing import Dict
from src.core.config_manager import ConfigManager

class LexiconManager:
    """Handles substitution for acronyms, abbreviations, foreign words, and special symbols."""

    def __init__(self, config_mgr: ConfigManager = None):
        if config_mgr is None:
            config_mgr = ConfigManager()
        self.abbreviations = config_mgr.load_dictionary("abbreviations")
        self.foreign_words = config_mgr.load_dictionary("foreign_words")
        self.symbols = config_mgr.load_dictionary("symbols")

    def replace_abbreviations(self, text: str) -> str:
        for key, val in self.abbreviations.items():
            # Match whole words or standard punctuation-separated acronyms
            pattern = r'\b' + re.escape(key) + r'\b'
            text = re.sub(pattern, val, text)
        return text

    def replace_foreign_words(self, text: str) -> str:
        for key, val in self.foreign_words.items():
            pattern = r'\b' + re.escape(key) + r'\b'
            text = re.sub(pattern, val, text, flags=re.IGNORECASE)
        return text

    def replace_symbols(self, text: str) -> str:
        for key, val in self.symbols.items():
            # Always use word boundaries or escaped pattern
            if key in ["$", "€", "¥", "£", "₫", "°C", "°F", "°", "@", "&", "#", "+", "=", "%"]:
                text = text.replace(key, f" {val} ")
            else:
                pattern = r'\b' + re.escape(key) + r'\b'
                text = re.sub(pattern, val, text, flags=re.IGNORECASE)
        return text
