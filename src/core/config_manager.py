import json
import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG_PATH = Path("config/default_settings.json")
PAUSE_CONFIG_PATH = Path("config/pause_config.json")

class ConfigManager:
    """Manages application settings, pause rules, and custom dictionaries."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH, pause_path: Path = PAUSE_CONFIG_PATH):
        self.config_path = config_path
        self.pause_path = pause_path
        self.settings: Dict[str, Any] = self._load_json(self.config_path)
        self.pause_config: Dict[str, Any] = self._load_json(self.pause_path)

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_settings(self, new_settings: Dict[str, Any]):
        self.settings.update(new_settings)
        os.makedirs(self.config_path.parent, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def get_pause_rules(self) -> Dict[str, int]:
        return self.pause_config.get("pause_durations_ms", {
            ",": 50,
            ".": 140,
            ":": 80,
            ";": 70,
            "?": 140,
            "!": 140,
            "paragraph": 280,
            "newline": 140
        })

    def save_pause_rules(self, pause_rules: Dict[str, int]):
        self.pause_config["pause_durations_ms"] = pause_rules
        os.makedirs(self.pause_path.parent, exist_ok=True)
        with open(self.pause_path, 'w', encoding='utf-8') as f:
            json.dump(self.pause_config, f, ensure_ascii=False, indent=2)

    def load_dictionary(self, dict_name: str) -> Dict[str, str]:
        file_path = Path(f"config/dictionaries/{dict_name}.json")
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
