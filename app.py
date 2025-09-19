import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Shadowing MVP", page_icon="🎧", layout="centered")
st.title("シャドーイング（読み上げ）")

# ====== 表示するテキスト（必要に応じて編集してください） ======
TEXT = (
    "It was a bright cold day in April, and the clocks were striking thirteen. "
    "The classroom was quiet, save for the soft rustle of pages turning."
)

st.write(
    "下のボタンを押すと、テキストを読み上げます。"
    "読み上げ中は現在の単語が強調表示されます。"
    "もう一度押すと停止します。"
    "最後まで読み上げたら『最初に戻る』ボタンになります。"
)

# ====== Web Speech API（ブラウザTTS）で読み上げ＆ハイライト ======
component_html = """
<style>
  .reader {
    font-size: 1.25rem;
    line-height: 2.1rem;
    background-color: #CCCCCC;   /* ← 薄いグレー背景 */
    padding: 1rem;               /* 内側に余白 */
    border-radius: 8px;          /* 角を丸める */
  }
  .word {
    transition: background-color 120ms ease;
    padding: 2px 1px;
    border-radius: 4px;
  }
  .active {
    background-color: #fff2a8;
  }
  .controls { margin-top: 1rem; }
  button.ui {
    padding: .6rem 1rem; border: 1px solid #ccc; border-radius: 8px; cursor: pointer;
    font-size: 1rem; background: #f7f7f7;
  }
  button.ui:hover { background: #efefef; }
</style>
<div class="reader" id="reader"></div>
<div class="controls">
  <button id="toggleBtn" class="ui">▶ 読み上げ開始</button>
</div>
<script>
(function() {
  const original = PLACEHOLDER_TEXT;
  const reader = document.getElementById('reader');
  const btn = document.getElementById('toggleBtn');

  // テキストを単語＋区切りでspan化（空白や記号も保持）
  const tokens = [];
  let spans = [];
  let charOffsets = [];
  (function tokenize() {
    const re = /(\\w+|\\s+|[^\\w\\s]+)/g;
    let m; let offset = 0; let html = '';
    while ((m = re.exec(original)) !== null) {
      const tk = m[0];
      const isWord = /\\w+/.test(tk);
      if (isWord) {
        const idx = spans.length;
        html += `<span class="word" data-idx="${idx}">${tk}</span>`;
        charOffsets.push(offset);
        spans.push(null);
      } else {
        html += tk;
      }
      offset += tk.length;
    }
    reader.innerHTML = html;
    spans = Array.from(reader.querySelectorAll('.word'));
  })();

  let utter = null;
  let speaking = false;
  let finished = false;
  let currentIdx = -1;

  function clearActive() {
    spans.forEach(s => s.classList.remove('active'));
  }

  function highlightByCharIndex(charIndex) {
    let idx = 0;
    for (let i = 0; i < charOffsets.length; i++) {
      if (charIndex >= charOffsets[i]) idx = i; else break;
    }
    if (idx !== currentIdx && spans[idx]) {
      clearActive();
      spans[idx].classList.add('active');
      currentIdx = idx;
      const rect = spans[idx].getBoundingClientRect();
      const inView = rect.top >= 0 && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight);
      if (!inView) spans[idx].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function resetUI() {
    speaking = false;
    finished = false;
    currentIdx = -1;
    clearActive();
    btn.textContent = '▶ 読み上げ開始';
  }

  function setToRestart() {
    speaking = false;
    finished = true;
    btn.textContent = '↩ 最初に戻る';
  }

  function startSpeak() {
    if (!('speechSynthesis' in window)) {
      alert('このブラウザは読み上げに対応していません（Chrome推奨）。');
      return;
    }
    window.speechSynthesis.cancel();

    utter = new SpeechSynthesisUtterance(original);
    utter.lang = 'en-US'; 
    utter.rate = 1.0;
    utter.pitch = 1.0;

    utter.onstart = () => { speaking = true; btn.textContent = '■ 停止'; };
    utter.onend   = () => { setToRestart(); };
    utter.onerror = () => { resetUI(); };
    utter.onboundary = (e) => {
      if (e.name === 'word' || e.charIndex >= 0) {
        highlightByCharIndex(e.charIndex);
      }
    };

    const voices = window.speechSynthesis.getVoices();
    const pref = voices.find(v => /en-US/i.test(v.lang) && /female/i.test(v.name)) ||
                 voices.find(v => /en-US/i.test(v.lang)) || voices[0];
    if (pref) utter.voice = pref;

    window.speechSynthesis.speak(utter);
  }

  btn.addEventListener('click', () => {
    if (finished) {
      resetUI();
      reader.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    if (!speaking) {
      startSpeak();
    } else {
      window.speechSynthesis.cancel();
      resetUI();
    }
  });
})();
</script>
"""

# PythonのTEXTを安全に埋め込む
component_html = component_html.replace("PLACEHOLDER_TEXT", repr(TEXT))

html(component_html, height=350, scrolling=True)

st.caption(
    "※ ブラウザのWeb Speech APIを利用しています。"
    "Chromeの最新安定版での利用を推奨します。音声は端末側のTTSエンジンに依存します。"
)
