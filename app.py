# app.py
import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Shadowing MVP", page_icon="🎧", layout="centered")
st.title("シャドーイング（読み上げ）")

st.write(
    "下の『▶ 再生』で読み上げ開始、もう一度で一時停止。"
    "『↩ 最初に戻る』でいつでもリセットできます。"
    "⚙（歯車）から **テキスト表示ON/OFF**、**再生速度（0.10〜2.00×）**、"
    "**声のタイプ（10代/30代/70代 × 男性/女性）**、**難易度（中学生/標準/超難）** を選べます。"
)

# --------------------------
# 3段階の難易度テキスト
# --------------------------
TEXTS = {
    "easy": """It is a bright day in April. The clocks say thirteen. The class is quiet. We sit at our desks. We look at the screen. There is a play button. We press the button. A voice starts. It is clear and slow. We listen and follow.
    
We read one word at a time. We do not hurry. We breathe. If we miss a sound, we stop. We try again. Step by step, we get better.

The room is calm. Light comes in from the window. A bus goes by outside. We hear a small bird. Time moves like a slow river. We do not rush.

We say easy words first. We say “a”, “the”, “and”, “is”. Then we say short verbs: “go”, “come”, “see”, “make”, “like”. We join words to make short lines. We read, we listen, we speak.

Some words are hard. That is okay. We pause and try again. We shape the sound with our mouth. We open our mouth for “a”. We smile a little for “i”. We touch our top teeth for “f”. We feel the air for “th”.

We follow the voice. The voice is our guide. We keep the same beat. Like walking, left foot, right foot. One step, then one more. One word, then one more.

The teacher nods. We nod too. We do not need to be perfect. We only need to try. Small steps make a long road. Today we take small steps. That is enough.

We read short lines about a day. The sky is blue. The air is cold. We hold a book. We turn a page. The page is light in our hand.

We say a full sentence now. 
“It is a bright day in April.” 
“The classroom is quiet.” 
“We press play and speak with the voice.” 
We can say these lines. We can say them well.

Near the end, we slow down. We breathe in and breathe out. We read the last line with care. We stop and smile. We feel a little proud. We know what to do next.

We press play again. We listen again. We speak again. A little stronger, a little clearer. Day by day, our words grow. Step by step, English becomes our friend.""",

    "standard": """It was a bright, cold day in April, and the clocks were striking thirteen. The classroom settled into a careful quiet, the kind born not of fear but of focus. We pressed play, and a steady voice unfurled like a ribbon down the page. We followed word by word, letting the rhythm guide our breath. Some syllables were smooth as glass; others had grit that caught on the tongue. We didn’t hurry. We adjusted, tried again, and let the sentence land.

Shadowing, the text reminded us, is ordinary courage: showing up, repeating, refining. Progress often hides in plain sight, like a seed rooting under dark soil. You won’t hear trumpets. You will feel a new ease when a sound you once dodged suddenly fits. The ear is the patient teacher; the mouth is the late student who eventually arrives.

Outside, a bus exhaled at the curb and pulled away. Sunlight counted tiles across the floor. Someone coughed, then settled. We borrowed the speaker’s cadence, and our scattered timing knit itself into a single pulse. A tricky cluster returned—r after a consonant, a th that wanted to escape—but we met it without drama, pinning it gently in place.

Midway through, the passage painted an evening after rain. Streetlights lifted their halos. Sidewalks carried rumors of footsteps. Windows practiced their soft theater for anyone who cared to watch. We read into the mood and let our voices pick up the hush. Not imitation, exactly—more like harmonizing with a melody we were learning to trust.

In the final paragraph, the voice grew deliberate, as if setting a lantern on each word. Believe in rhythm when you can’t believe in skill. Believe in breath when rhythm deserts you. And when breath is all you have, let it be enough for one more line. We reached the period together. The room felt unchanged and kinder. We looked up, surprised by our own sound. It wasn’t flawless. It was ours, and it was moving forward.""",

    "hard": """On a lucid yet frigid April morning, the clocks insisted upon thirteen, and the hour trembled with a faint sense of misalignment. In the room, silence spread like varnish, deliberate and thin. We depressed the button, and a voice—tempered, unhurried—spiraled outward. We pursued it with deliberate fidelity, harvesting consonants, calibrating vowels, and tolerating the friction that arises wherever articulation and ambition collide.

Shadowing, the passage proposed, is a discipline of increments. No revelation descends; instead, there is an accretion of micro-adjustments—a millimeter of jaw, a degree of tongue, an ounce of breath. The progress is almost subcutaneous, a quiet osmosis by which unfamiliar phonemes acquire residency. The ear becomes curator; the mouth follows as apprentice, sanding roughness from each attempted contour.

Beyond the windows, the city rehearsed its minor symphony: a bus releasing compressed air, a bicycle chain engaging, a newspaper loosened from its twine. Sunlight traversed the floor in precise tessellations, as if auditioning for geometry. Inside, our tempo converged. The difficult cluster returned—a consonant labyrinth that previously undid us—but we resisted melodrama and pursued exactitude. We allowed the cadence to act as metronome and map.

Midway, the text drifted toward images of evening after rain. Sodium lamps coronated intersections; gutters ferried miniature constellations of reflected light. Apartments conversed in murmurs through half-drawn curtains. We matched that atmosphere with restraint, letting sentences land without spectacle. Accuracy first, then ornament, the voice seemed to counsel.

Toward the end, the narration acquired a lucid gravitas. Believe in rhythm when competence wavers. Believe in breath when rhythm thins. And if breath is the last currency, spend it on a single clean line. We approached the terminus with an almost liturgical care, each word set down like a measured stone. Finishing did not feel like triumph so much as alignment: the mouth, at last, cooperating with the ear; the hour, though still labeled thirteen, somehow reconciled with time. We exhaled, not victorious but prepared—for repetition, for refinement, for the quiet work that makes tomorrow sound less foreign than today."""
}


# --------------------------
# Webコンポーネント（HTML/JS/CSS）
# --------------------------
component_html = """
<style>
  .wrap { max-height: 440px; overflow: auto; border:1px solid #e3e3e3; border-radius:10px; background:#f1f1f1; }
  .reader {
    padding: 1rem .9rem .5rem; line-height: 2.1rem; font-size: 1.25rem; background:#CCC;
    white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere;
  }
  .reader.hide-text { visibility: hidden; }
  .word { transition: background-color 120ms ease; padding:2px 1px; border-radius:4px; }
  .active { background:#fff2a8; }
  .controls { position: sticky; bottom:0; z-index:10; padding:0; background:transparent; }
  .controls-inner {
    position: relative; display:flex; justify-content:center; align-items:center; gap:.6rem;
    padding:.6rem .8rem; background:#ffffffcc; backdrop-filter: blur(4px); border-top:1px solid #e5e5e5;
  }
  button.ui { padding:.55rem .9rem; border:1px solid #ccc; border-radius:8px; cursor:pointer; font-size:1rem; background:#f7f7f7; }
  button.ui:hover { background:#efefef; }
  .settings-btn {
    position:absolute; right:.6rem; top:50%; transform:translateY(-50%); display:inline-flex; align-items:center; justify-content:center;
    width:2.2rem; height:2.2rem; border-radius:8px; border:1px solid #ccc; background:#f7f7f7; cursor:pointer;
  }
  .settings-btn:hover { background:#efefef; } .settings-btn svg { width:18px; height:18px; }
  .settings-panel {
    position:absolute; right:.6rem; bottom:calc(100% + 8px); min-width: 320px; background:#fff; border:1px solid #ddd;
    border-radius:10px; padding:.85rem; box-shadow:0 10px 25px rgba(0,0,0,.08);
  }
  .hidden { display:none; }
  .row { display:flex; align-items:center; justify-content:space-between; gap:.75rem; margin:.6rem 0; font-size:.95rem; }
  .col { display:flex; align-items:center; gap:.6rem; width:100%; }
  .desc { font-size:.8rem; color:#666; margin-top:.25rem; }
  .rate-wrap, .gap-wrap { width:100%; display:flex; align-items:center; gap:.6rem; }
  .rate-wrap input[type="range"], .gap-wrap input[type="range"] { width:100%; }
  .rate-value, .gap-value { min-width:3.6rem; text-align:right; font-variant-numeric:tabular-nums; }
</style>

<div class="wrap" id="wrap">
  <div class="reader" id="reader" aria-live="polite"></div>

  <div class="controls">
    <div class="controls-inner">
      <button id="toggleBtn"  class="ui" aria-label="play/pause">▶ 再生</button>
      <button id="restartBtn" class="ui" aria-label="restart">↩ 最初に戻る</button>

      <!-- 歯車（設定） -->
      <button id="settingsBtn" class="settings-btn" aria-label="settings" aria-haspopup="true" aria-expanded="false" title="設定">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M19.14,12.94a7.49,7.49,0,0,0,.05-.94,7.49,7.49,0,0,0-.05-.94l2.11-1.65a.5.5,0,0,0,.12-.63l-2-3.46a.5.5,0,0,0-.6-.22l-2.49,1a7.28,7.28,0,0,0-1.63-.94l-.38-2.65A.5.5,0,0,0,13.7,2H10.3a.5.5,0,0,0-.49.41L9.43,5.06a7.28,7.28,0,0,0-1.63.94l-2.49-1a.5.5,0,0,0-.6.22l-2,3.46a.5.5,0,0,0,.12.63L4.94,11.06a7.49,7.49,0,0,0-.05.94,7.49,7.49,0,0,0,.05.94L2.83,14.59a.5.5,0,0,0-.12.63l2,3.46a.5.5,0,0,0,.6.22l2.49-1a7.28,7.28,0,0,0,1.63.94l.38,2.65a.5.5,0,0,0,.49.41h3.4a.5.5,0,0,0,.49-.41l.38-2.65a7.28,7.28,0,0,0,1.63-.94l2.49,1a.5.5,0,0,0,.6-.22l2-3.46a.5.5,0,0,0-.12-.63Zm-7.14,2.56A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"/></svg>
      </button>

      <!-- 設定パネル -->
      <div id="settingsPanel" class="settings-panel hidden" role="dialog" aria-label="設定">
        <div class="row"><div class="col">
          <label for="toggleTextChk" style="min-width:5.5rem;">テキスト</label>
          <input id="toggleTextChk" type="checkbox" checked />
          <span style="font-size:.85rem; color:#666;">（表示/非表示）</span>
        </div></div>

        <div class="row"><div class="col">
          <label for="difficulty" style="min-width:5.5rem;">難易度</label>
          <select id="difficulty">
            <option value="easy">中学生</option>
            <option value="standard" selected>標準</option>
            <option value="hard">超難（非日常語）</option>
          </select>
        </div></div>

        <div class="row"><div class="col">
          <label for="voiceProfile" style="min-width:5.5rem;">声のタイプ</label>
          <select id="voiceProfile">
            <option value="adult_f" selected>30代 女性</option>
            <option value="adult_m">30代 男性</option>
            <option value="teen_f">10代 女性</option>
            <option value="teen_m">10代 男性</option>
            <option value="senior_f">70代 女性</option>
            <option value="senior_m">70代 男性</option>
          </select>
        </div></div>

        <div class="row"><div class="col">
          <label for="rateSlider" style="min-width:5.5rem;">再生速度</label>
          <div class="rate-wrap">
            <input id="rateSlider" type="range" min="0.10" max="2.00" step="0.05" value="1.00" />
            <span id="rateValue" class="rate-value">1.00×</span>
          </div>
        </div></div>

        <div class="row"><div class="col">
          <label for="gapSlider" style="min-width:5.5rem;">文間ポーズ</label>
          <div class="gap-wrap">
            <input id="gapSlider" type="range" min="0" max="600" step="50" value="250" />
            <span id="gapValue" class="gap-value">250ms</span>
          </div>
        </div></div>

        <div class="desc">※ 端末で単語境界が取れない場合は推定テンポでハイライトします。文ごとに再生し、文の終わりにポーズを入れます。</div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  // 3レベルの本文（Python側で埋め込み）
  const TEXTS = { easy: PLACEHOLDER_EASY, standard: PLACEHOLDER_STANDARD, hard: PLACEHOLDER_HARD };

  // refs
  const wrap = document.getElementById('wrap');
  const reader = document.getElementById('reader');
  const btn = document.getElementById('toggleBtn');
  const rbtn = document.getElementById('restartBtn');
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsPop = document.getElementById('settingsPanel');
  const chkText = document.getElementById('toggleTextChk');
  const rateSlider = document.getElementById('rateSlider');
  const rateValue = document.getElementById('rateValue');
  const gapSlider = document.getElementById('gapSlider');
  const gapValue = document.getElementById('gapValue');
  const voiceSelect = document.getElementById('voiceProfile');
  const diffSelect = document.getElementById('difficulty');

  // state
  let original = TEXTS[diffSelect.value] || '';
  let spans = [], charOffsets = [];
  let sentences = []; // [{start,end,text}]
  let utter = null;
  let speaking = false, paused = false, finished = false;
  let currentIdx = -1, baseChar = 0;
  let rate = 1.0, profile = voiceSelect.value;
  let resumeIdx = 0; // 再開位置（単語idx）
  let sentCursor = 0; // 再生中の文インデックス
  let sentenceGapMs = 250;

  // Android fallback
  let boundaryWorks = false;
  let tick = null; // setTimeout のID
  function clearTick(){ if (tick){ clearTimeout(tick); tick = null; } }

  // pitch map
  const PROFILE_PITCH = { teen_f:1.25, teen_m:1.10, adult_f:1.00, adult_m:0.95, senior_f:0.85, senior_m:0.80 };

  // voice pick
  const isEnglish = v => /^en[-_]/i.test(v.lang) || /English/i.test(v.name);
  const isMaleName = v => /(male|boy|david|mark|michael|john|james|brian|daniel|matt(hew)?|alex|george|tom|peter|sam|ben)/i.test(v.name);
  const isFemaleName = v => /(female|girl|aria|amy|zoe|zoey|susan|samantha|linda|emma|olivia|jenny|joanna|salli|kimberly|allison|kendra|martha|jessica|hannah|lisa|sarah|katy|heidi)/i.test(v.name);
  const targetGenderOf = p => /_f$/.test(p) ? 'female' : 'male';
  function pickVoice(targetGender){
    const voices = window.speechSynthesis.getVoices();
    const en = voices.filter(isEnglish);
    if (!en.length) return voices[0]||null;
    let cs = targetGender==='female' ? en.filter(isFemaleName) : en.filter(isMaleName);
    if (!cs.length) cs = en;
    return cs[0]||voices[0]||null;
  }

  // html escape
  function escapeHTML(s){
    return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  // 文分割（終止記号 . ! ? と改行で大まかに）
  function splitIntoSentences(text){
    const res = [];
    let start = 0, m;
    const re = /[^.!?\\n\\r]+[.!?]?(?:\\s+|$)/g;
    while ((m = re.exec(text)) !== null) {
      const seg = m[0];
      const end = m.index + seg.length;
      if (seg.trim().length > 0) res.push({ start: m.index, end: end, text: seg });
    }
    if (!res.length) res.push({ start: 0, end: text.length, text });
    return res;
  }

  // tokenize（単語span化）
  function tokenize(text){
    spans = []; charOffsets = [];
    const re = /(\\w+|\\s+|[^\\w\\s]+)/g;
    let m, offset = 0, html = '';
    while ((m = re.exec(text)) !== null) {
      const tk = m[0], isWord = /\\w+/.test(tk);
      if (isWord) {
        const idx = spans.length;
        html += `<span class="word" data-idx="${idx}">${escapeHTML(tk)}</span>`;
        charOffsets.push(offset);
        spans.push(null);
      } else {
        html += escapeHTML(tk);
      }
      offset += tk.length;
    }
    reader.innerHTML = html;
    spans = Array.from(reader.querySelectorAll('.word'));
    sentences = splitIntoSentences(text);
  }

  function clearActive(){ spans.forEach(s=>s.classList.remove('active')); }
  function scrollToSpan(el){ if(!el) return; const t = el.offsetTop - wrap.clientHeight*0.35; wrap.scrollTo({ top: Math.max(0,t), behavior:'smooth' }); }
  function highlightByCharIndex(charIndex){
    let idx=0; for (let i=0;i<charOffsets.length;i++){ if (charIndex>=charOffsets[i]) idx=i; else break; }
    if (idx!==currentIdx && spans[idx]){ clearActive(); spans[idx].classList.add('active'); currentIdx=idx; scrollToSpan(spans[idx]); }
  }
  function highlightByIndex(idx){
    idx = Math.max(0, Math.min(idx, spans.length-1));
    if (idx!==currentIdx && spans[idx]){ clearActive(); spans[idx].classList.add('active'); currentIdx=idx; scrollToSpan(spans[idx]); }
  }

  // 直後テキスト取得＆可変ディレイ（Android fallback用）
  function nextTextAfterSpan(span) {
    let n = span && span.nextSibling;
    while (n && n.nodeType !== 3) n = n.nextSibling;
    return n && n.nodeValue ? n.nodeValue : "";
  }
  function estimateWordMs(idx, rate) {
    const w = (spans[idx]?.textContent || "").trim();
    const len = w.length || 1;
    let lenFactor =
      len <= 2 ? 0.55 :
      len <= 4 ? 0.80 :
      len <= 7 ? 1.00 :
      len <= 10 ? 1.15 : 1.30;
    const nextTxt = nextTextAfterSpan(spans[idx]);
    let pause = 0;
    if (/^\\s*[\\n\\r]/.test(nextTxt)) pause += 280;
    if (/^\\s*,/.test(nextTxt))        pause += 140;
    if (/^\\s*[;:]/.test(nextTxt))     pause += 180;
    if (/^\\s*[.!?]/.test(nextTxt))    pause += 320;
    const base = 320;
    const ms = (base * lenFactor + pause) / Math.max(0.10, rate);
    return Math.max(90, Math.min(ms, 900));
  }

  // fallback（可変setTimeout）
  function startFallbackTicker(){
    if (tick) return;
    let idx = currentIdx >= 0 ? currentIdx : 0;
    const step = () => {
      if (paused || finished) { tick = null; return; }
      idx = Math.min(idx + 1, spans.length - 1);
      highlightByIndex(idx);
      if (idx >= spans.length - 1) { tick = null; return; }
      const nextMs = estimateWordMs(idx, rate);
      tick = setTimeout(step, nextMs);
    };
    const firstMs = estimateWordMs(idx, rate);
    tick = setTimeout(step, firstMs);
  }

  function updateToggleLabel(){
    if (!speaking && !paused && !finished) btn.textContent='▶ 再生';
    else if (speaking && !paused) btn.textContent='⏸ 一時停止';
    else if (!speaking && paused) btn.textContent='▶ 再開';
    else if (finished) btn.textContent='▶ 再生';
  }

  function resetUI(){
    try{ window.speechSynthesis.cancel(); }catch(e){}
    speaking=false; paused=false; finished=false;
    currentIdx=-1; baseChar=0; resumeIdx=0; sentCursor=0;
    boundaryWorks=false; clearTick();
    clearActive(); wrap.scrollTo({top:0,behavior:'smooth'}); updateToggleLabel();
  }

  // 単語idx → その単語が属する文インデックスを返す
  function sentenceIndexForWordIdx(widx){
    const ch = charOffsets[Math.max(0, Math.min(widx, charOffsets.length-1))] || 0;
    let i = 0;
    for (; i < sentences.length; i++){
      if (ch < sentences[i].end) return i;
    }
    return sentences.length - 1;
  }

  // 文ごとに再生（gapを挟みながらシーケンス）
  function speakSentenceAt(si){
    if (si < 0 || si >= sentences.length) { speaking=false; finished=true; updateToggleLabel(); return; }
    sentCursor = si;
    const seg = sentences[si];
    baseChar = seg.start;

    try{ window.speechSynthesis.cancel(); }catch(e){}
    boundaryWorks=false; clearTick();

    const u = new SpeechSynthesisUtterance(original.slice(seg.start, seg.end));
    utter = u;
    u.lang = 'en-US';
    u.rate = rate;
    u.pitch = PROFILE_PITCH[profile] ?? 1.0;
    u.volume = 1.0;

    u.onstart = ()=>{ speaking=true; paused=false; finished=false; updateToggleLabel(); };
    u.onend   = ()=>{
      speaking=false;
      if (paused) { updateToggleLabel(); return; } // ポーズ中はここで止める
      if (si >= sentences.length - 1) {
        finished = true; updateToggleLabel(); return;
      }
      // 文間ポーズ後に次の文へ
      setTimeout(()=>{ if (!paused) speakSentenceAt(si + 1); }, sentenceGapMs);
    };
    u.onerror = ()=>{ speaking=false; updateToggleLabel(); };

    u.onboundary = (e)=>{ boundaryWorks = true; if (e.name==='word' || e.charIndex>=0){ highlightByCharIndex(baseChar + e.charIndex); } };

    const startSpeak = ()=>{ const v = pickVoice(targetGenderOf(profile)); if (v) u.voice = v; window.speechSynthesis.speak(u); };
    if (window.speechSynthesis.getVoices().length===0) window.speechSynthesis.onvoiceschanged = startSpeak; else startSpeak();

    // onboundary来なければフォールバック開始
    setTimeout(()=>{ if (!boundaryWorks && !paused) startFallbackTicker(); }, 800);
  }

  // 初期描画
  tokenize(original);

  // ボタン
  btn.addEventListener('click', ()=>{
    if (finished){ resetUI(); speakSentenceAt(0); return; }

    // 未再生/停止中 → 再生
    if (!speaking && !paused){
      const startWord = currentIdx <= 0 ? 0 : currentIdx;
      const si = sentenceIndexForWordIdx(startWord);
      speakSentenceAt(si);
      return;
    }

    // 再生中 → ソフト一時停止（位置保存→cancel）
    if (speaking && !paused){
      resumeIdx = Math.max(0, currentIdx);
      try{ window.speechSynthesis.cancel(); }catch(e){}
      paused = true; speaking = false; clearTick(); updateToggleLabel();
      return;
    }

    // 一時停止中 → 再開（保存位置の文から）
    if (!speaking && paused){
      paused = false; updateToggleLabel();
      const si = sentenceIndexForWordIdx(resumeIdx);
      speakSentenceAt(si);
      return;
    }
  });

  rbtn.addEventListener('click', ()=>{ resetUI(); });

  // 設定（開閉）
  function toggleSettings(open){
    const willOpen = (open===undefined) ? settingsPop.classList.contains('hidden') : open;
    if (willOpen){ settingsPop.classList.remove('hidden'); settingsBtn.setAttribute('aria-expanded','true'); }
    else { settingsPop.classList.add('hidden'); settingsBtn.setAttribute('aria-expanded','false'); }
  }
  settingsBtn.addEventListener('click', (e)=>{ e.stopPropagation(); toggleSettings(); });
  document.addEventListener('click', (e)=>{ if(!settingsPop.classList.contains('hidden')){ if(!settingsPop.contains(e.target) && e.target!==settingsBtn){ toggleSettings(false); } } });

  // テキスト表示ON/OFF
  chkText.addEventListener('change', ()=>{ if (chkText.checked) reader.classList.remove('hide-text'); else reader.classList.add('hide-text'); });

  // 速度
  const clampRate = v => Math.min(2.0, Math.max(0.10, parseFloat(v)||1.0));
  const renderRateLabel = v => rateValue.textContent = Number(v).toFixed(2) + '×';
  rate = clampRate(rateSlider.value); renderRateLabel(rate);
  rateSlider.addEventListener('input', ()=>{ renderRateLabel(clampRate(rateSlider.value)); });
  rateSlider.addEventListener('change', ()=>{
    rate = clampRate(rateSlider.value); renderRateLabel(rate);
    if (speaking && !paused){
      // 進行中の文から設定を反映し直す
      const si = sentCursor;
      try{ window.speechSynthesis.cancel(); }catch(e){}
      speakSentenceAt(si);
    }
  });

  // 文間ポーズ
  function renderGapLabel(v){ gapValue.textContent = Math.round(v) + 'ms'; }
  sentenceGapMs = Math.round(parseFloat(gapSlider.value)||250);
  renderGapLabel(sentenceGapMs);
  gapSlider.addEventListener('input', ()=>{ renderGapLabel(parseFloat(gapSlider.value)||0); });
  gapSlider.addEventListener('change', ()=>{
    sentenceGapMs = Math.round(parseFloat(gapSlider.value)||0);
  });

  // 声・難易度
  voiceSelect.addEventListener('change', ()=>{ profile = voiceSelect.value; if (speaking && !paused){ const si = sentCursor; try{ window.speechSynthesis.cancel(); }catch(e){} speakSentenceAt(si);} });
  diffSelect.addEventListener('change', ()=>{
    const wasPlaying = speaking && !paused;
    resetUI();
    original = TEXTS[diffSelect.value] || '';
    tokenize(original);
    if (wasPlaying) speakSentenceAt(0);
  });
})();
</script>
"""

# PythonのTEXTSをHTMLに埋め込む
component_html = (
    component_html
    .replace("PLACEHOLDER_EASY", repr(TEXTS["easy"]))
    .replace("PLACEHOLDER_STANDARD", repr(TEXTS["standard"]))
    .replace("PLACEHOLDER_HARD", repr(TEXTS["hard"]))
)

# 描画
html(component_html, height=480, scrolling=False)

st.caption(
    "※ ブラウザのWeb Speech APIを利用しています。Chromeの最新安定版を推奨。"
    "音声は端末側のTTSエンジン・ボイスに依存します。"
)
