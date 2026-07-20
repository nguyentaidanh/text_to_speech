document.addEventListener('DOMContentLoaded', () => {
  const inputText = document.getElementById('inputText');
  const charCount = document.getElementById('charCount');
  const btnAnalyze = document.getElementById('btnAnalyze');
  const btnSynthesize = document.getElementById('btnSynthesize');
  const inspectorBody = document.getElementById('inspectorBody');

  const aiToggle = document.getElementById('aiToggle');
  const aiProvider = document.getElementById('aiProvider');
  const apiKey = document.getElementById('apiKey');

  const voiceSelect = document.getElementById('voiceSelect');
  const speedRange = document.getElementById('speedRange');
  const speedVal = document.getElementById('speedVal');
  const pitchRange = document.getElementById('pitchRange');
  const pitchVal = document.getElementById('pitchVal');
  const pauseMultiplier = document.getElementById('pauseMultiplier');
  const pauseVal = document.getElementById('pauseVal');

  const audioPlayer = document.getElementById('audioPlayer');
  const btnPlayPause = document.getElementById('btnPlayPause');
  const audioProgress = document.getElementById('audioProgress');
  const timeDisplay = document.getElementById('timeDisplay');

  const btnExportMP3 = document.getElementById('btnExportMP3');
  const btnExportWAV = document.getElementById('btnExportWAV');
  const btnExportSRT = document.getElementById('btnExportSRT');
  const btnExportJSON = document.getElementById('btnExportJSON');

  let currentSynthesisResult = null;

  // Preset text & voice handlers
  const presets = {
    sweet_female: "Chào anh, chúc anh một ngày mới thật nhiều niềm vui và may mắn. Em luôn ở đây đồng hành và lắng nghe cùng anh nhé!",
    podcast: "Chào mừng các bạn đã đến với kênh Podcast Nam Trầm. Hôm nay chúng ta sẽ bàn về Trí tuệ Nhân tạo và tương lai của công nghệ TTS.",
    news: "Hôm nay 20/07/2026 lúc 09:30, Tập đoàn Công nghệ công bố doanh thu 100.000đ mỗi cổ phiếu tại TP.HCM. Tốc độ tăng trưởng đạt 25% trong quý II.",
    tech: "Website google.com và ứng dụng YouTube chính thức tích hợp 50km đường truyền băng thông rộng với tốc độ 100MB mỗi giây."
  };

  document.querySelectorAll('.btn-preset').forEach(btn => {
    btn.addEventListener('click', () => {
      const pKey = btn.getAttribute('data-preset');
      inputText.value = presets[pKey] || '';
      if (pKey === 'sweet_female') {
        voiceSelect.value = 'vi-VN-HoaiMyNeural';
        speedRange.value = 0.9;
        speedVal.textContent = '0.9x';
        pitchRange.value = 2;
        pitchVal.textContent = '+2Hz';
      } else if (pKey === 'podcast') {
        voiceSelect.value = 'vi-VN-NamMinhNeural';
        speedRange.value = 1.0;
        speedVal.textContent = '1.0x';
        pitchRange.value = 0;
        pitchVal.textContent = '0Hz';
      }
      updateCharCount();
    });
  });

  inputText.addEventListener('input', updateCharCount);
  function updateCharCount() {
    charCount.textContent = `${inputText.value.length} kí tự`;
  }

  speedRange.addEventListener('input', () => speedVal.textContent = `${speedRange.value}x`);
  pitchRange.addEventListener('input', () => pitchVal.textContent = `${pitchRange.value}Hz`);
  pauseMultiplier.addEventListener('input', () => pauseVal.textContent = `${pauseMultiplier.value}x`);

  aiToggle.addEventListener('change', () => {
    const isAi = aiToggle.value === "true";
    document.querySelectorAll('.ai-field').forEach(el => {
      el.style.display = isAi ? 'flex' : 'none';
    });
    document.getElementById('modeBadge').textContent = isAi ? "MODE 2: AI-Assisted" : "MODE 1: Rule-Based (Offline)";
  });

  // Collect active config
  function getActiveConfig() {
    return {
      ai: {
        enabled: aiToggle.value === "true",
        provider: aiProvider.value,
        api_key: apiKey.value
      },
      voice: {
        engine: "edge_tts",
        voice_id: voiceSelect.value,
        speed: parseFloat(speedRange.value),
        pitch: parseFloat(pitchRange.value),
        pause_multiplier: parseFloat(pauseMultiplier.value)
      },
      pause_rules: {
        ",": parseInt(document.getElementById('pauseComma').value),
        ".": parseInt(document.getElementById('pausePeriod').value),
        ":": parseInt(document.getElementById('pauseColon').value),
        "?": parseInt(document.getElementById('pauseQuestion').value),
        "!": parseInt(document.getElementById('pauseExclamation').value),
        "newline": parseInt(document.getElementById('pauseNewline').value),
        "paragraph": parseInt(document.getElementById('pauseParagraph').value)
      }
    };
  }

  // Analyze Text
  btnAnalyze.addEventListener('click', async () => {
    const text = inputText.value.trim();
    if (!text) return alert("Vui lòng nhập văn bản!");

    inspectorBody.innerHTML = "<div class='empty-state'>Đang phân tích ngữ âm...</div>";

    try {
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, config: getActiveConfig() })
      });
      const data = await resp.json();
      renderAnalysis(data);
    } catch (err) {
      inspectorBody.innerHTML = `<div class='empty-state' style='color:#ef4444;'>Lỗi: ${err.message}</div>`;
    }
  });

  function renderAnalysis(data) {
    inspectorBody.innerHTML = '';
    document.getElementById('providerBadge').textContent = `Provider: ${data.provider} | AI: ${data.is_ai_assisted}`;

    data.segments.forEach(seg => {
      const card = document.createElement('div');
      card.className = 'segment-card';
      card.innerHTML = `
        <div class="raw-text">#${seg.sentence_id}. ${seg.raw_text}</div>
        <div class="norm-text">➜ Chuẩn hóa: ${seg.normalized_text}</div>
        <div class="segment-meta">
          <span>😊 Cảm xúc: ${seg.emotion}</span>
          <span>⏱️ Khoảng ngắt: ${seg.pause_after_ms}ms</span>
        </div>
      `;
      inspectorBody.appendChild(card);
    });
  }

  // Synthesize Speech
  btnSynthesize.addEventListener('click', async () => {
    const text = inputText.value.trim();
    if (!text) return alert("Vui lòng nhập văn bản!");

    btnSynthesize.disabled = true;
    btnSynthesize.textContent = "⏳ Đang tổng hợp...";

    try {
      const resp = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, config: getActiveConfig() })
      });
      const data = await resp.json();
      currentSynthesisResult = data;
      renderAnalysis(data.analysis);

      // Load audio player
      const audioBlob = hexToBlob(data.audio_hex, 'audio/mpeg');
      const audioUrl = URL.createObjectURL(audioBlob);
      audioPlayer.src = audioUrl;
      audioPlayer.play();
      btnPlayPause.textContent = '⏸';

      enableExportButtons(true);
    } catch (err) {
      alert(`Lỗi tổng hợp giọng nói: ${err.message}`);
    } finally {
      btnSynthesize.disabled = false;
      btnSynthesize.textContent = "▶ Tạo Giọng Nói";
    }
  });

  function hexToBlob(hex, mimeType) {
    const bytes = new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
    return new Blob([bytes], { type: mimeType });
  }

  function enableExportButtons(enable) {
    [btnExportMP3, btnExportWAV, btnExportSRT, btnExportJSON].forEach(btn => btn.disabled = !enable);
  }

  btnPlayPause.addEventListener('click', () => {
    if (audioPlayer.paused) {
      audioPlayer.play();
      btnPlayPause.textContent = '⏸';
    } else {
      audioPlayer.pause();
      btnPlayPause.textContent = '▶';
    }
  });

  audioPlayer.addEventListener('timeupdate', () => {
    if (audioPlayer.duration) {
      const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
      audioProgress.value = progress;
      timeDisplay.textContent = `${formatTime(audioPlayer.currentTime)} / ${formatTime(audioPlayer.duration)}`;
    }
  });

  function formatTime(sec) {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  // Export handlers
  btnExportMP3.addEventListener('click', () => downloadFile(hexToBlob(currentSynthesisResult.audio_hex, 'audio/mpeg'), 'vietnam_speech.mp3'));
  btnExportWAV.addEventListener('click', () => downloadFile(hexToBlob(currentSynthesisResult.audio_hex, 'audio/wav'), 'vietnam_speech.wav'));
  btnExportSRT.addEventListener('click', () => downloadFile(new Blob([currentSynthesisResult.srt_subtitles], { type: 'text/plain' }), 'subtitles.srt'));
  btnExportJSON.addEventListener('click', () => downloadFile(new Blob([JSON.stringify(currentSynthesisResult.metadata_json, null, 2)], { type: 'application/json' }), 'metadata.json'));

  function downloadFile(blob, filename) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
  }
});
