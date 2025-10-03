import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Shadowing MVP", page_icon="🎧", layout="centered")
st.title("シャドーイング（読み上げ）")

# ====== 表示するテキスト（必要に応じて編集してください） ======
TEXT = (
"""It was a bright cold day in April, and the clocks were striking thirteen.
The classroom was quiet, save for the soft rustle of pages turning. 
A faint breeze slipped through a narrow window, and the curtains breathed in and out like a calm animal. 
On the board, someone had written a single question: Why do we speak at all? 
No one answered. 
We were busy lining up our pencils and courage.

The teacher nodded, pressed play, and the voice began. 
It was clear and steady, like a path through a forest. 
We followed, one step at a time, word after word, testing our balance on each sound. 
Some words felt smooth, and our tongues slid across them. 
Others had small stones hidden inside, and our mouths stumbled for a moment. 
But the voice did not stop, so neither did we.

I watched the second hand sweep, a thin silver scythe. 
It cut the hour into equal slices and fed them to our nerves. 
We breathed together. 
We borrowed the rhythm from the speaker, and the room found a single heartbeat. 
No one looked up. 
Even the fluorescent lights seemed to hum in the same key.

Outside, a bus sighed at the corner and pulled away. 
A sparrow made three short hops along the windowsill and blinked at its reflection. 
Somewhere down the corridor a locker door clapped shut and then apologized with a soft rattle. 
April sunlight touched the floor tile by tile, as if counting them. 
Time, for once, was not our enemy. 
It was a rope we could hold.

The passage shifted. 
Now it spoke about ordinary courage: showing up, trying again, speaking even when the first sound is shaky. 
It said progress is quiet work, like grass growing at night. 
It said the ear is a patient teacher, and the mouth is a late student who needs extra time. 
We repeated, and each echo seemed less like an echo and more like our own voice discovering its shoes.

I glanced sideways and saw a profile, steady as a lighthouse. 
The eyes tracked the words, line by line, never rushing the sea. 
A strand of hair escaped, drew a question mark in the air, and then settled back into place. 
We matched the model voice together, a small duet inside a larger choir. 
No one announced it, but everyone heard it.

Halfway through, the speaker paused for breath, and the silence felt soft, not empty. 
We held that softness for a beat, then stepped forward again. 
The new paragraph described a city evening after rain. 
Streetlights lifted their halos. 
Sidewalks remembered footsteps. 
Windows told stories to anyone who looked long enough.

The text did not promise miracles. 
It promised practice. 
It promised that a voice grows by walking, not by waiting. 
It asked us to plant a seed of sound today and water it tomorrow. 
It warned that some days the soil is stubborn. 
It reminded us that roots hide their victories until the leaf is ready.

Near the end, the classroom air felt warmer, though the breeze still moved like a quiet hand. 
I heard my own words arrive almost on time, like a friend who used to be late. 
The tricky sounds came back, but this time they knocked politely before entering. 
Even my mistakes seemed honest, like footprints that refuse to lie. 
I did not chase perfection. 
I kept a steady step.

The voice slowed with intention, guiding us toward the last lines. 
It said, speak as if you are leaving a small light for your future self to find. 
It said, when you cannot believe in skill, believe in rhythm. 
When you cannot believe in rhythm, believe in breath. 
And when breath is all you have, let that be enough for one more sentence. 
We reached the final period.

The teacher looked up. 
We looked up. 
The room was the same, yet kinder. 
Outside, the bus stop waited for its next story. 
Inside, our mouths remembered a new route home. 
It was still April. 
The clocks still chose thirteen. 
But now the hour felt wide open, and our voices knew where to go."""
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
  .wrap {
    max-height: 440px;          /* 内部スクロール枠 */
    overflow: auto;
    border: 1px solid #e3e3e3;
    border-radius: 10px;
    background: #f1f1f1;
  }
  .reader {
    padding: 1rem .9rem 0.5rem;
    line-height: 2.1rem;
    font-size: 1.25rem;
    background-color: #CCCCCC;

    /* 改行と折返し */
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
  }
  .reader.hide-text { visibility: hidden; } /* テキスト非表示 */

  .word {
    transition: background-color 120ms ease;
    padding: 2px 1px;
    border-radius: 4px;
  }
  .active { background-color: #fff2a8; }

  /* 下部センター・常時表示のコントロール */
  .controls {
    position: sticky;
    bottom: 0;
    z-index: 10;
    padding: 0;                 /* 内側に別レイヤー */
    background: transparent;
  }
  .controls-inner {
    position: relative;         /* 設定パネルの基点 */
    display: flex;
    justify-content: center;
    align-items: center;
    gap: .6rem;
    padding: .6rem .8rem;
    background: #ffffffcc;
    backdrop-filter: blur(4px);
    border-top: 1px solid #e5e5e5;
  }
  button.ui {
    padding: .55rem .9rem; border: 1px solid #ccc; border-radius: 8px; cursor: pointer;
    font-size: 1rem; background: #f7f7f7;
  }
  button.ui:hover { background: #efefef; }

  /* 右側の歯車ボタン */
  .settings-btn {
    position: absolute;
    right: .6rem;
    top: 50%;
    transform: translateY(-50%);
    display: inline-flex; align-items: center; justify-content: center;
    width: 2.2rem; height: 2.2rem;
    border-radius: 8px;
    border: 1px solid #ccc;
    background: #f7f7f7;
    cursor: pointer;
  }
  .settings-btn:hover { background: #efefef; }
  .settings-btn svg { width: 18px; height: 18px; }

  /* 設定パネル */
  .settings-panel {
    position: absolute;
    right: .6rem;
    bottom: calc(100% + 8px);
    min-width: 220px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: .75rem;
    box-shadow: 0 10px 25px rgba(0,0,0,.08);
  }
  .hidden { display: none; }
  .settings-panel .row {
    display: flex; align-items: center; justify-content: space-between;
    gap: .5rem; margin: .5rem 0;
    font-size: .95rem;
  }
  .settings-panel .row label { user-select: none; }
  .settings-panel .desc { font-size: .8rem; color: #666; margin-top: .25rem; }
  .settings-panel select {
    padding: .35rem .5rem; border: 1px solid #ccc; border-radius: 6px; background: #fafafa;
  }
</style>

<div class="wrap" id="wrap">
  <div class="reader" id="reader" aria-live="polite"></div>

  <div class="controls">
    <div class="controls-inner">
      <button id="toggleBtn"  class="ui" aria-label="play/pause">▶ 再生</button>
      <button id="restartBtn" class="ui" aria-label="restart">↩ 最初に戻る</button>

      <!-- 歯車（設定） -->
      <button id="settingsBtn" class="settings-btn" aria-label="settings" aria-haspopup="true" aria-expanded="false" title="設定">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M19.14,12.94a7.49,7.49,0,0,0,.05-.94,7.49,7.49,0,0,0-.05-.94l2.11-1.65a.5.5,0,0,0,.12-.63l-2-3.46a.5.5,0,0,0-.6-.22l-2.49,1a7.28,7.28,0,0,0-1.63-.94l-.38-2.65A.5.5,0,0,0,13.7,2H10.3a.5.5,0,0,0-.49.41L9.43,5.06a7.28,7.28,0,0,0-1.63.94l-2.49-1a.5.5,0,0,0-.6.22l-2,3.46a.5.5,0,0,0,.12.63L4.94,11.06a7.49,7.49,0,0,0-.05.94,7.49,7.49,0,0,0,.05.94L2.83,14.59a.5.5,0,0,0-.12.63l2,3.46a.5.5,0,0,0,.6.22l2.49-1a7.28,7.28,0,0,0,1.63.94l.38,2.65a.5.5,0,0,0,.49.41h3.4a.5.5,0,0,0,.49-.41l.38-2.65a7.28,7.28,0,0,0,1.63-.94l2.49,1a.5.5,0,0,0,.6-.22l2-3.46a.5.5,0,0,0-.12-.63Zm-7.14,2.56A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"/>
        </svg>
      </button>

      <!-- 設定パネル -->
      <div id="settingsPanel" class="settings-panel hidden" role="dialog" aria-label="設定">
        <div class="row">
          <label for="toggleTextChk">テキストを表示</label>
          <input id="toggleTextChk" type="checkbox" checked />
        </div>
        <div class="row">
          <label for="rateSelect">再生速度</label>
          <select id="rateSelect">
            <option value="0.10">0.10×</option>
            <option value="0.15">0.15×</option>
            <option value="0.20">0.20×</option>
            <option value="0.25">0.25×</option>
            <option value="0.50">0.50×</option>
            <option value="0.75">0.75×</option>
            <option value="0.9">0.90×</option>
            <option value="1.0" selected>1.00×（標準）</option>
            <option value="1.1">1.10×</option>
            <option value="1.25">1.25×</option>
            <option value="1.5">1.50×</option>
            <option value="1.75">1.75×</option>
            <option value="2.0">2.00×</option>
          </select>
        </div>
        <div class="desc">※ 再生中に速度を変えると、現在位置から新速度で再開します。</div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  const original = PLACEHOLDER_TEXT;

  const wrap        = document.getElementById('wrap');
  const reader      = document.getElementById('reader');
  const btn         = document.getElementById('toggleBtn');
  const rbtn        = document.getElementById('restartBtn');
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsPop = document.getElementById('settingsPanel');
  const chkText     = document.getElementById('toggleTextChk');
  const rateSelect  = document.getElementById('rateSelect');

  // HTMLエスケープ
  function escapeHTML(s) {
    return s.replace(/[&<>"']/g, c => (
      {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
    ));
  }

  // --- tokenization（単語ごとに span 化、空白/改行/記号も保持） ---
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
        html += `<span class="word" data-idx="${idx}">${escapeHTML(tk)}</span>`;
        charOffsets.push(offset);
        spans.push(null);
      } else {
        html += escapeHTML(tk); // 空白・改行・記号
      }
      offset += tk.length;
    }
    reader.innerHTML = html;
    spans = Array.from(reader.querySelectorAll('.word'));
  })();

  // --- 状態管理 ---
  let utter = null;
  let speaking = false;   // 再生が始まっている（終了まで true）
  let paused   = false;   // 一時停止中
  let finished = false;   // 再生完了
  let currentIdx = -1;    // 現在ハイライト中の単語インデックス
  let baseChar = 0;       // 現在のUtterance開始位置（original基準の先頭オフセット）
  let rate = 1.0;         // 再生速度

  function clearActive() { spans.forEach(s => s.classList.remove('active')); }

  // テキスト追従スクロール（表示枠の上から35%位置へ）
  function scrollToSpan(el) {
    if (!el) return;
    const targetTop = el.offsetTop - wrap.clientHeight * 0.35;
    wrap.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' });
  }

  // original 先頭からの charIndex でハイライト
  function highlightByCharIndex(charIndex) {
    let idx = 0;
    for (let i = 0; i < charOffsets.length; i++) {
      if (charIndex >= charOffsets[i]) idx = i; else break;
    }
    if (idx !== currentIdx && spans[idx]) {
      clearActive();
      spans[idx].classList.add('active');
      currentIdx = idx;
      scrollToSpan(spans[idx]);
    }
  }

  function updateToggleLabel() {
    if (!speaking && !paused && !finished) {
      btn.textContent = '▶ 再生';
    } else if (speaking && !paused) {
      btn.textContent = '⏸ 一時停止';
    } else if (speaking && paused) {
      btn.textContent = '▶ 再開';
    } else if (finished) {
      btn.textContent = '▶ 再生';
    }
  }

  function resetUI() {
    try { window.speechSynthesis.cancel(); } catch(e) {}
    speaking = false;
    paused   = false;
    finished = false;
    currentIdx = -1;
    baseChar = 0;
    clearActive();
    wrap.scrollTo({ top: 0, behavior: 'smooth' });
    updateToggleLabel();
  }

  function chooseVoiceFor(utterance) {
    const voices = window.speechSynthesis.getVoices();
    const pref = voices.find(v => /en-US/i.test(v.lang) && /female/i.test(v.name)) ||
                 voices.find(v => /en-US/i.test(v.lang)) || voices[0];
    if (pref) utterance.voice = pref;
  }

  function speakFrom(startIdx) {
    // startIdx の単語先頭から話し始める
    const safeIdx = Math.max(0, Math.min(startIdx || 0, charOffsets.length - 1));
    baseChar = charOffsets[safeIdx] || 0;

    try { window.speechSynthesis.cancel(); } catch(e) {}

    utter = new SpeechSynthesisUtterance(original.slice(baseChar));
    utter.lang  = 'en-US';
    utter.rate  = rate;
    utter.pitch = 1.0;

    utter.onstart = () => {
      speaking = true;
      paused   = false;
      finished = false;
      updateToggleLabel();
    };
    utter.onend = () => {
      speaking = false;
      paused   = false;
      finished = true;
      updateToggleLabel();
    };
    utter.onerror = () => {
      speaking = false;
      paused   = false;
      finished = false;
      updateToggleLabel();
    };
    utter.onboundary = (e) => {
      if (e.name === 'word' || e.charIndex >= 0) {
        const globalChar = baseChar + e.charIndex; // original基準へ戻す
        highlightByCharIndex(globalChar);
      }
    };

    const startSpeak = () => {
      chooseVoiceFor(utter);
      window.speechSynthesis.speak(utter);
    };
    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = startSpeak;
    } else {
      startSpeak();
    }
  }

  // --- ボタン動作 ---
  btn.addEventListener('click', () => {
    if (finished) {
      // 完了後は最初から
      resetUI();
      speakFrom(0);
      return;
    }
    if (!speaking && !paused) {
      // 未再生 → 再生
      if (currentIdx <= 0) {
        speakFrom(0);
      } else {
        speakFrom(currentIdx);
      }
      return;
    }
    if (speaking && !paused) {
      // 再生中 → 一時停止
      try { window.speechSynthesis.pause(); } catch(e) {}
      paused = true;
      updateToggleLabel();
      return;
    }
    if (speaking && paused) {
      // 一時停止中 → 再開
      try { window.speechSynthesis.resume(); } catch(e) {}
      paused = false;
      updateToggleLabel();
      return;
    }
  });

  rbtn.addEventListener('click', () => {
    resetUI(); // いつでも最初に戻す
  });

  // --- 設定（歯車） ---
  function toggleSettings(open) {
    const willOpen = (open === undefined) ? settingsPop.classList.contains('hidden') : open;
    if (willOpen) {
      settingsPop.classList.remove('hidden');
      settingsBtn.setAttribute('aria-expanded', 'true');
    } else {
      settingsPop.classList.add('hidden');
      settingsBtn.setAttribute('aria-expanded', 'false');
    }
  }
  settingsBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleSettings();
  });
  // 外側クリックで閉じる
  document.addEventListener('click', (e) => {
    if (!settingsPop.classList.contains('hidden')) {
      if (!settingsPop.contains(e.target) && e.target !== settingsBtn) {
        toggleSettings(false);
      }
    }
  });

  // テキスト表示ON/OFF
  chkText.addEventListener('change', () => {
    if (chkText.checked) {
      reader.classList.remove('hide-text');
    } else {
      reader.classList.add('hide-text');
    }
  });

  // 再生速度
  rateSelect.addEventListener('change', () => {
    rate = Math.min(2.0, Math.max(0.10, parseFloat(rateSelect.value) || 1.0));
    // 再生中に速度変更 → 現在の単語から新速度で再開
    if (speaking && !paused) {
      const restartIdx = (currentIdx >= 0) ? currentIdx : 0;
      speakFrom(restartIdx);
    }
  });
})();
</script>
"""



# PythonのTEXTを安全に埋め込む
component_html = component_html.replace("PLACEHOLDER_TEXT", repr(TEXT))

html(component_html, height=480, scrolling=False)

st.caption(
    "※ ブラウザのWeb Speech APIを利用しています。"
    "Chromeの最新安定版での利用を推奨します。音声は端末側のTTSエンジンに依存します。"
)
