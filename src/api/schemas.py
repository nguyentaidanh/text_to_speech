from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class TTSRequest(BaseModel):
    text: str
    config: Optional[Dict[str, Any]] = None

class AnalyzeRequest(BaseModel):
    text: str
    config: Optional[Dict[str, Any]] = None

class SettingsUpdateRequest(BaseModel):
    general: Optional[Dict[str, Any]] = None
    ai: Optional[Dict[str, Any]] = None
    local_ai: Optional[Dict[str, Any]] = None
    voice: Optional[Dict[str, Any]] = None
    pause_rules: Optional[Dict[str, int]] = None
