# 🎙️ VietTTS Studio - Hệ Thống Tổng Hợp Giọng Nói Tiếng Việt Enterprise

**VietTTS Studio** là ứng dụng Chuyển đổi Văn bản thành Giọng nói (Text-to-Speech) Tiếng Việt chuyên nghiệp, sẵn sàng cho sản xuất (Production-Ready). Ứng dụng được thiết kế tối ưu cho các Nhà sáng tạo nội dung YouTube, Audiobook, Podcast, Doanh nghiệp và Hệ thống nội bộ.

---

## 🌟 Tính Năng Nổi Bật

### ⚡ MODE 1: Rule-Based Processing (Mặc định - 0$ Chi phí, 100% Offline)
- **Tối ưu chi phí tuyệt đối**: Không cần bất kỳ AI API Key nào, chạy hoàn toàn offline, tốc độ cực nhanh và ổn định.
- **Engine Chuẩn hóa Ngữ âm Tiếng Việt**:
  - **Số & Ngày tháng**: `2026` $\rightarrow$ `hai nghìn không trăm hai mươi sáu`, `20/07/2026` $\rightarrow$ `ngày hai mươi tháng bảy năm hai nghìn không trăm hai mươi sáu`.
  - **Giờ giấc & Tiền tệ**: `09:30` $\rightarrow$ `chín giờ ba mươi phút`, `100.000đ` $\rightarrow$ `một trăm nghìn đồng`, `$50` $\rightarrow$ `năm mươi đô la`.
  - **Đơn vị đo lường**: `50km` $\rightarrow$ `năm mươi ki lô mét`, `25°C` $\rightarrow$ `hai mươi lăm độ C`.
  - **Từ viết tắt & Số La Mã**: `TP.HCM` $\rightarrow$ `Thành phố Hồ Chí Minh`, `XXI` $\rightarrow$ `hai mươi mốt`.
  - **Từ tiếng Anh & Ký tự đặc biệt**: Phân giải tự động các từ ngoại nhập phổ biến (`youtube` $\rightarrow$ `yêu túp`, `%` $\rightarrow$ `phần trăm`).
- **Quy tắc Ngắt nghỉ (Pause Rules) Tùy chỉnh (ms)**:
  - Dấu phẩy (`,`): `250 ms`
  - Dấu chấm (`.`): `700 ms`
  - Dấu hai chấm (`:`): `400 ms`
  - Dấu chấm hỏi (`?`): `700 ms`
  - Dấu chấm cảm (`!`): `650 ms`
  - Xuống dòng / Đoạn văn: `700 ms - 1000 ms`

---

### 🤖 MODE 2: AI-Assisted Text Analysis (Tùy chọn Bật/Tắt)
- Hỗ trợ các nhà cung cấp AI hàng đầu: **Google Gemini**, **OpenAI (GPT-4o)**, **Anthropic Claude**, **DeepSeek**, **Qwen (Alibaba)** và **Custom REST API (Ollama/VLLM)**.
- AI thực hiện: Tối ưu khoảng ngắt, phân tích cảm xúc (Prosody), gợi ý nhấn giọng (Emphasis) **mà KHÔNG tạo file âm thanh (Không tốn chi phí TTS API)**.
- Tự động fallback về MODE 1 nếu mất kết nối hoặc không nhập API Key.

---

### 🎧 Giọng Đọc Mặc Định Chuyên Nghiệp
- Giọng Nam Tiếng Việt: **Trầm, Ấm, Phong cách Podcast / Audiobook, Đọc tự nhiên, Không bị kịch / nhái (No Robotic Sound)**.
- Hỗ trợ Giọng Nữ nhẹ nhàng, rõ chữ.
- Điều chỉnh Tốc độ (Speed), Cao độ (Pitch), Âm lượng (Volume) và Hệ số Ngắt nghỉ (Pause Multiplier).

---

## 🏗️ Kiến Trúc Dự Án (Enterprise Directory Structure)

```
text_to_speech/
├── config/                      # Cấu hình hệ thống & Từ điển chuẩn hóa
│   ├── default_settings.json
│   ├── pause_config.json
│   └── dictionaries/            # Từ điển từ viết tắt, từ ngoại nhập, ký hiệu
├── src/
│   ├── core/                    # Interfaces, Plugin Registry & Config Manager
│   ├── domain/
│   │   ├── nlp/                 # Rule-Based Vietnamese Normalizer Engine
│   │   ├── ai/                  # AI Providers (Gemini, OpenAI, Claude, DeepSeek, Qwen)
│   │   ├── tts/                 # Multi-Engine TTS Matrix (EdgeTTS, Piper, VITS)
│   │   ├── audio/               # Audio Pause Stitcher & SRT Subtitle Exporter
│   │   └── orchestrator.py      # Pipeline Controller chính
│   ├── api/                     # FastAPI REST API Server
│   └── ui/                      # Giao diện Studio (HTML5/CSS3/JS & Desktop launcher)
├── tests/                       # Bộ kiểm thử tự động (Unit & Integration Tests)
├── docker/                      # Container Dockerfile & docker-compose.yml
├── main.py                      # File chạy ứng dụng chính
└── requirements.txt
```

---

## 🛠️ Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Sử dụng `uv` (Khuyên dùng - Nhanh nhất)

```bash
# 1. Khởi tạo môi trường ảo
uv venv

# 2. Cài đặt các thư viện cần thiết
uv pip install -r requirements.txt

# 3. Chạy Ứng dụng Studio
uv run python main.py
```

---

### Cách 2: Sử dụng `pip` tiêu chuẩn

```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Khởi chạy ứng dụng
python main.py
```

---

### Cách 3: Chạy Web Server riêng lẻ
```bash
uv run python -m uvicorn src.api.server:app --reload --port 8000
```
- Giao diện Studio Web: 👉 **[http://127.0.0.1:8000/studio](http://127.0.0.1:8000/studio)**
- Swagger API Docs: 👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

### Cách 4: Chạy bằng Docker
```bash
docker-compose -f docker/docker-compose.yml up --build -d
```

---

## 📡 REST API Reference

| Method | Endpoint | Mô tả |
| :--- | :--- | :--- |
| `POST` | `/api/tts` | Tổng hợp văn bản thành âm thanh & trả về metadata |
| `POST` | `/api/tts/raw` | Trả về file binary âm thanh trực tiếp (`.mp3` / `.wav`) |
| `POST` | `/api/analyze` | Phân tích cú pháp văn bản & bảng ngắt nghỉ ms |
| `POST` | `/api/preview` | Đọc thử 100 ký tự đầu tiên |
| `GET` | `/api/voices` | Lấy danh sách giọng đọc khả dụng |
| `GET/PUT` | `/api/settings` | Đọc / Cập nhật cấu hình & Quy tắc ngắt nghỉ |

---

## 🧪 Kiểm Thử Tự Động (Automated Testing)

Chạy bộ kiểm thử với `pytest`:

```bash
uv run python -m pytest tests/
```

---

## 📄 Xuất Dữ Liệu Supported
- 🎵 Audio: `MP3`, `WAV`, `OGG`
- 📄 Phụ đề: `SRT` (Thời gian khớp chuẩn từng miligiây)
- 📊 Metadata: `JSON`

---

## 📝 License
Phát triển dành cho mục đích thương mại, linh hoạt tùy biến và mở rộng plugin.
