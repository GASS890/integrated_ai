from pathlib import Path

path = Path("static/index.html")
text = path.read_text(encoding="utf-8")

# 1. 設定UIを追加
insert_after = '''<body>'''

ui = '''<body>
<div id="tts-settings-panel" style="padding:8px; border-bottom:1px solid #444;">
  <span>音声:</span>
  <select id="ttsBackend">
    <option value="piper_plus">Piper Plus</option>
    <option value="voicevox">VOICEVOX</option>
    <option value="piper">Piper</option>
    <option value="auto">Auto</option>
  </select>
  <button onclick="saveTtsSettings()">音声設定保存</button>
  <span id="ttsStatusText"></span>
</div>
'''

if 'id="tts-settings-panel"' not in text:
    text = text.replace(insert_after, ui, 1)

# 2. JS追加
insert_before = '''</script>'''

js = '''
async function loadTtsSettings() {
  try {
    const res = await fetch("/tts/status");
    const data = await res.json();

    const backend = data.default_backend || "voicevox";
    const select = document.getElementById("ttsBackend");
    const status = document.getElementById("ttsStatusText");

    if (select) select.value = backend;
    if (status) {
      status.textContent = ` 現在: ${backend} / Piper Plus: ${data.piper_plus_ready ? "OK" : "NG"}`;
    }
  } catch (e) {
    console.error("tts status error", e);
  }
}

async function saveTtsSettings() {
  const select = document.getElementById("ttsBackend");
  const backend = select ? select.value : "voicevox";

  const res = await fetch("/tts/settings", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      backend: backend,
      fallback_backend: "voicevox",
      speaker: 1,
      auto_fallback: true
    })
  });

  if (!res.ok) {
    alert("音声設定の保存に失敗しました");
    return;
  }

  await loadTtsSettings();
  alert("音声設定を保存しました");
}

window.addEventListener("load", loadTtsSettings);
'''

if "async function loadTtsSettings()" not in text:
    text = text.replace(insert_before, js + "\n" + insert_before, 1)

path.write_text(text, encoding="utf-8")
print("TTS UI patched.")
