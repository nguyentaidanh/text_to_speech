# 🎙️ VietTTS Studio - Enterprise Vietnamese Text-to-Speech System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()

**VietTTS Studio** is a production-ready, enterprise-grade Vietnamese Text-to-Speech (TTS) Desktop and Web Application built for YouTube creators, audiobook authors, podcasters, businesses, and internal tools.

---

## 🌟 Architecture & Analysis Modes

### ⚡ MODE 1: Rule-Based Processing (Default - Zero Cost, 100% Offline)
- **Zero API Expenses**: Operates 100% offline without requiring any AI API keys, providing ultra-fast and stable speech synthesis.
- **Comprehensive Vietnamese Linguistic Engine**:
  - **Numbers & Dates**: `2026` $\rightarrow$ `hai nghìn không trăm hai mươi sáu`, `20/07/2026` $\rightarrow$ `ngày hai mươi tháng bảy năm hai nghìn không trăm hai mươi sáu`.
  - **Time & Currency**: `09:30` $\rightarrow$ `chín giờ ba mươi phút`, `100.000đ` $\rightarrow$ `một trăm nghìn đồng`, `$50` $\rightarrow$ `năm mươi đô la`.
  - **Units & Measurements**: `50km` $\rightarrow$ `năm mươi ki lô mét`, `25°C` $\rightarrow$ `hai mươi lăm độ C`.
  - **Acronyms & Roman Numerals**: `TP.HCM` $\rightarrow$ `Thành phố Hồ Chí Minh`, `XXI` $\rightarrow$ `hai mươi mốt`.
  - **English Words & Symbols**: Auto-phonetizes foreign loan words (`youtube` $\rightarrow$ `yêu túp`, `%` $\rightarrow$ `phần trăm`).

---

### 💻 MODE 2: Cloud AI-Assisted Text Analysis
- Integrates leading Cloud AI Providers: **Google Gemini**, **OpenAI (GPT-4o)**, **Anthropic Claude**, **DeepSeek**, **Qwen (Alibaba)**, and **Custom REST APIs**.
- **Pure Prosody Analysis**: AI optimizes pause durations, emotions, and emphasis **without performing TTS audio generation (Zero audio API costs)**.

---

### 🖥️ MODE 3: Local AI Speech Analysis (100% Offline AI Prosody)
- **Zero Cloud API Costs**: Runs local LLMs via **Ollama**, **llama.cpp**, **LM Studio**, **vLLM**, or **OpenAI-Compatible Local APIs**.
- **Automatic Model Detection**: Scans and displays available local models automatically (`GET /api/local-models`).
- **Automatic Failover**: Automatically falls back to MODE 1 (Rule-Based Analyzer) if the local AI service times out or is unreachable.

---

## 🖥️ Hardware & Vietnamese Local Model Matrix

| Hardware Spec | Recommended Model | Quantization | RAM Req. | VRAM Req. | Speed (tok/s) | Quality | License |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **8GB RAM / CPU-only** | `Llama-3.2-3B-Instruct` | Q4_K_M | ~3.5 GB | N/A | 15–25 t/s | Good | Llama 3.2 |
| **16GB RAM / CPU-only** | `Qwen2.5-7B-Instruct` | Q4_K_M | ~5.8 GB | N/A | 10–18 t/s | Excellent | Apache 2.0 |
| **32GB RAM / CPU-only** | `Qwen2.5-14B-Instruct` | Q4_K_M | ~9.5 GB | N/A | 6–12 t/s | Superior | Apache 2.0 |
| **RTX 3060 (12GB VRAM)** | `Qwen2.5-7B-Instruct` | Q5_K_M / Q8 | ~2 GB | ~6.5 GB | 55–80 t/s | Superior | Apache 2.0 |
| **RTX 4060 (8GB VRAM)** | `Qwen2.5-7B-Instruct` | Q4_K_M | ~2 GB | ~5.2 GB | 60–90 t/s | Superior | Apache 2.0 |
| **RTX 4070 (12GB VRAM)**| `DeepSeek-R1-Distill-Qwen-14B` | Q4_K_M | ~2 GB | ~9.8 GB | 45–70 t/s | SOTA | MIT |

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
│   │   ├── ai/                  # Cloud & Local AI Providers
│   │   │   └── local/           # [NEW] Ollama, llama.cpp, LM Studio, vLLM Local AI Providers
│   │   ├── tts/                 # Multi-Engine TTS Adapter Matrix (EdgeTTS, Piper, VITS)
│   │   ├── audio/               # Audio Pause Stitcher & SRT Subtitle Exporter
│   │   └── orchestrator.py      # Main Pipeline Controller with Failover
│   ├── api/                     # FastAPI REST API Server
│   └── ui/                      # Studio UI (HTML5/CSS3/JS & Desktop launcher)
├── tests/                       # Test Suite (Unit & Local AI Tests)
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

### Method 2: Standalone Web Server
```bash
uv run python -m uvicorn src.api.server:app --reload --port 8000
```
- Studio Web Interface: 👉 **[http://127.0.0.1:8000/studio](http://127.0.0.1:8000/studio)**
- Interactive Swagger API Docs: 👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/tts` | Synthesize text and return full audio & metadata response |
| `POST` | `/api/tts/raw` | Stream raw binary audio (`audio/mpeg` or `audio/wav`) |
| `POST` | `/api/analyze` | Analyze Vietnamese text for prosody & millisecond pause breakdown |
| `GET` | `/api/local-models` | Auto-detect installed models from Ollama & local LLM servers |
| `GET` | `/api/voices` | Retrieve available voices across installed TTS engines |
| `GET/PUT` | `/api/settings` | Retrieve or update application configuration & pause rules |

---

## 🧪 Automated Testing

Execute automated unit tests with `pytest`:

```bash
uv run python -m pytest tests/
```

---

## 📝 License
Distributed under the MIT License. Commercial and enterprise friendly.
