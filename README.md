# 🎙️ VietTTS Studio - Enterprise Vietnamese Text-to-Speech System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()

**VietTTS Studio** is a production-ready, enterprise-grade Vietnamese Text-to-Speech (TTS) Desktop and Web Application built for YouTube creators, audiobook authors, podcasters, businesses, and internal tools.

---

## 🌟 Core Architecture Principles

### ⚡ MODE 1: Rule-Based Text Processing (Default - Zero API Cost, 100% Offline)
- **Zero API Expenses**: Operates 100% offline without requiring any AI API keys, providing ultra-fast and stable speech synthesis.
- **Comprehensive Vietnamese Linguistic Engine**:
  - **Numbers & Dates**: `2026` $\rightarrow$ `hai nghìn không trăm hai mươi sáu`, `20/07/2026` $\rightarrow$ `ngày hai mươi tháng bảy năm hai nghìn không trăm hai mươi sáu`.
  - **Time & Currency**: `09:30` $\rightarrow$ `chín giờ ba mươi phút`, `100.000đ` $\rightarrow$ `một trăm nghìn đồng`, `$50` $\rightarrow$ `năm mươi đô la`.
  - **Units & Measurements**: `50km` $\rightarrow$ `năm mươi ki lô mét`, `25°C` $\rightarrow$ `hai mươi lăm độ C`.
  - **Acronyms & Roman Numerals**: `TP.HCM` $\rightarrow$ `Thành phố Hồ Chí Minh`, `XXI` $\rightarrow$ `hai mươi mốt`.
  - **English Words & Symbols**: Auto-phonetizes foreign loan words (`youtube` $\rightarrow$ `yêu túp`, `%` $\rightarrow$ `phần trăm`).
- **Customizable Punctuation Pause Rules (ms)**:
  - Comma (`,`): `250 ms`
  - Period (`.`): `700 ms`
  - Colon (`:`): `400 ms`
  - Semicolon (`;`): `350 ms`
  - Question mark (`?`): `700 ms`
  - Exclamation mark (`!`): `650 ms`
  - Paragraph Break / Newline: `700 ms - 1000 ms`

---

### 🤖 MODE 2: Optional AI-Assisted Text Analysis
- Integrates leading AI Providers: **Google Gemini**, **OpenAI (GPT-4o)**, **Anthropic Claude**, **DeepSeek**, **Qwen (Alibaba)**, and **Custom REST APIs (Ollama/VLLM)**.
- **Pure Prosody Analysis**: AI optimizes pause durations, emotions, and speech emphasis **without performing TTS audio generation (No audio API costs)**.
- Graceful automatic fallback to MODE 1 rule-based processing if API keys are missing or requests time out.

---

### 🎧 Professional Voice Pipeline
- Default Vietnamese Male Voice: **Deep, Warm, Natural Podcast / Audiobook style (No robotic artifacts)**.
- Clear, natural female voice options.
- Dynamic adjustments for Speed, Pitch, Volume, and Pause Multipliers.

---

## 🏗️ Project Directory Structure

```
text_to_speech/
├── config/                      # Settings & Linguistic Dictionaries
│   ├── default_settings.json
│   ├── pause_config.json
│   └── dictionaries/            # Abbreviations, foreign words, symbols
├── src/
│   ├── core/                    # Core Interfaces, Plugin Registry & Config Manager
│   ├── domain/
│   │   ├── nlp/                 # Rule-Based Vietnamese Normalizer Engine
│   │   ├── ai/                  # AI Providers (Gemini, OpenAI, Claude, DeepSeek, Qwen)
│   │   ├── tts/                 # Multi-Engine TTS Adapter Matrix (EdgeTTS, Piper, VITS)
│   │   ├── audio/               # Audio Pause Stitcher & SRT Subtitle Exporter
│   │   └── orchestrator.py      # Main Pipeline Controller
│   ├── api/                     # FastAPI REST API Server
│   └── ui/                      # Studio UI (HTML5/CSS3/JS & Desktop launcher)
├── tests/                       # Automated Test Suite (Unit & Integration Tests)
├── docker/                      # Dockerfile & docker-compose.yml
├── main.py                      # Primary Application Entrypoint
└── requirements.txt
```

---

## 🛠️ Installation & Getting Started

### Method 1: Using `uv` (Recommended - Ultra Fast)

```bash
# 1. Create virtual environment
uv venv

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Launch VietTTS Studio
uv run python main.py
```

---

### Method 2: Using Standard `pip`

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch application
python main.py
```

---

### Method 3: Standalone Web Server
```bash
uv run python -m uvicorn src.api.server:app --reload --port 8000
```
- Studio Web Interface: 👉 **[http://127.0.0.1:8000/studio](http://127.0.0.1:8000/studio)**
- Interactive Swagger API Docs: 👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

### Method 4: Docker Deployment
```bash
docker-compose -f docker/docker-compose.yml up --build -d
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/tts` | Synthesize text and return full audio & metadata response |
| `POST` | `/api/tts/raw` | Stream raw binary audio (`audio/mpeg` or `audio/wav`) |
| `/api/analyze` | `POST` | Analyze Vietnamese text for prosody & millisecond pause breakdown |
| `/api/preview` | `POST` | Synthesize short preview snippet (first 100 characters) |
| `GET` | `/api/voices` | Retrieve available voices across installed TTS engines |
| `GET/PUT` | `/api/settings` | Retrieve or update application configuration & pause rules |

---

## 🧪 Automated Testing

Execute automated unit tests with `pytest`:

```bash
uv run python -m pytest tests/
```

---

## 📄 Output Formats
- 🎵 Audio: `MP3`, `WAV`, `OGG`
- 📄 Subtitles: `SRT` (Millisecond timestamp precision)
- 📊 Metadata: `JSON`

---

## 📝 License
Distributed under the MIT License. Commercial and enterprise friendly.
