import io
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.core.config_manager import ConfigManager
from src.domain.orchestrator import TTSOrchestrator
from src.domain.ai.local.detector import LocalModelDetector
from src.api.schemas import TTSRequest, AnalyzeRequest, SettingsUpdateRequest

app = FastAPI(
    title="VietTTS Studio REST API",
    description="Production-ready Vietnamese Text-to-Speech Desktop/Web Engine",
    version="1.1.0"
)

# CORS middleware for Web Client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config_mgr = ConfigManager()
orchestrator = TTSOrchestrator(config_mgr)
local_detector = LocalModelDetector()

# Serve Static UI files if present
ui_static_dir = Path("src/ui/static")
if ui_static_dir.exists():
    app.mount("/studio", StaticFiles(directory=str(ui_static_dir), html=True), name="static")

@app.get("/")
async def root():
    return {"message": "VietTTS Studio API is running", "docs_url": "/docs", "studio_url": "/studio"}

@app.post("/api/tts")
async def synthesize_tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    try:
        result = await orchestrator.process_and_synthesize(req.text, req.config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts/raw")
async def synthesize_tts_raw(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    try:
        result = await orchestrator.process_and_synthesize(req.text, req.config)
        audio_bytes = bytes.fromhex(result.audio_hex)
        media_type = "audio/mpeg" if result.audio_format == "mp3" else "audio/wav"
        return Response(content=audio_bytes, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_text(req: AnalyzeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    try:
        result = await orchestrator.analyze_text(req.text, req.config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preview")
async def preview_text(req: TTSRequest):
    preview_text = req.text[:100]
    return await synthesize_tts(TTSRequest(text=preview_text, config=req.config))

@app.get("/api/voices")
async def list_voices():
    voices = await orchestrator.get_all_voices()
    return {"voices": voices}

@app.get("/api/local-models")
async def list_local_models():
    models = await local_detector.detect_all()
    return {"models": models}

@app.get("/api/settings")
async def get_settings():
    return {
        "settings": config_mgr.settings,
        "pause_rules": config_mgr.get_pause_rules()
    }

@app.put("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    if req.general:
        config_mgr.settings["general"].update(req.general)
    if req.ai:
        config_mgr.settings["ai"].update(req.ai)
    if req.local_ai:
        if "local_ai" not in config_mgr.settings:
            config_mgr.settings["local_ai"] = {}
        config_mgr.settings["local_ai"].update(req.local_ai)
    if req.voice:
        config_mgr.settings["voice"].update(req.voice)
    if req.pause_rules:
        config_mgr.save_pause_rules(req.pause_rules)

    config_mgr.save_settings(config_mgr.settings)
    return {
        "status": "success",
        "settings": config_mgr.settings,
        "pause_rules": config_mgr.get_pause_rules()
    }
