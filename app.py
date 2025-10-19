# app.py
# Shadowing MVP — Browser TTS / Google Cloud TTS 切替版（安定・互換）
# - data/texts.json / ui/component.html を外部ファイルから読み込み
# - Google Cloud TTS は SSML <mark> の timepoints で正確同期
# - v1 と v1beta1 を自動判定（timepoints対応の方を使用）
# - HTML/XML のエスケープで表示欠落・早期停止を防止
# - Secrets は「gcp_json」または「[gcp_service_account_key]」の両方に対応（Streamlit Cloud）

import base64
import json
import os
import re
from pathlib import Path

import streamlit as st
from streamlit.components.v1 import html

# =========================
# Secrets / 認証セットアップ
# =========================
def setup_gcp_credentials():
    """
    優先度:
    1) 環境変数 GOOGLE_APPLICATION_CREDENTIALS があれば何もしない（ローカル想定）
    2) st.secrets["gcp_json"] 形式（JSON文字列 or dict）
    3) st.secrets["gcp_service_account_key"] 形式（TOMLテーブル→dict）
    どちらでも /tmp にJSONを書き出して環境変数をセット
    """
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return

    gcp_payload = None
    try:
        # A) gcp_json（JSON文字列 or dict）
        if "gcp_json" in st.secrets:
            g = st.secrets["gcp_json"]
            if isinstance(g, str):
                try:
                    gcp_payload = json.loads(g)  # JSON文字列なら dict 化
                except Exception:
                    gcp_payload = g             # そのまま文字列で保存
            else:
                gcp_payload = dict(g)
        # B) gcp_service_account_key（TOMLテーブル -> dict）
        elif "gcp_service_account_key" in st.secrets:
            g = dict(st.secrets["gcp_service_account_key"])
            # private_key の \n を実際の改行へ
            if "private_key" in g and isinstance(g["private_key"], str):
                g["private_key"] = g["private_key"].replace("\\n", "\n")
            gcp_payload = g
    except Exception:
        gcp_payload = None

    if not gcp_payload:
        return  # Cloud 側にSecrets未設定ならスルー（ブラウザTTSだけで動く）

    cred_path = "/tmp/gcp-tts-sa.json"
    with open(cred_path, "w", encoding="utf-8") as f:
        if isinstance(gcp_payload, str):
            f.write(gcp_payload)
        else:
            json.dump(gcp_payload, f)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

setup_gcp_credentials()

# =========================
# Google Cloud TTS import（timepoints 対応モジュールを自動選択）
# =========================
_GCTTS_AVAILABLE = True

def _supports_timepoints(mod):
    try:
        if hasattr(mod.SynthesizeSpeechRequest, "enable_time_pointing"):
            return True
    except Exception:
        pass
    try:
        import importlib
        ty = importlib.import_module(mod.__name__ + ".types")
        return hasattr(ty.SynthesizeSpeechRequest, "enable_time_pointing")
    except Exception:
        return False

try:
    from google.cloud import texttospeech_v1 as _tts_v1
    if _supports_timepoints(_tts_v1):
        tts = _tts_v1
        _TTS_VARIANT = "v1"
    else:
        from google.cloud import texttospeech_v1beta1 as _tts_v1b
        if _supports_timepoints(_tts_v1b):
            tts = _tts_v1b
            _TTS_VARIANT = "v1beta1"
        else:
            _GCTTS_AVAILABLE = False
            tts = None  # type: ignore
            _TTS_VARIANT = "none"
except Exception:
    try:
        from google.cloud import texttospeech_v1beta1 as _tts_v1b
        if _supports_timepoints(_tts_v1b):
            tts = _tts_v1b
            _TTS_VARIANT = "v1beta1"
        else:
            _GCTTS_AVAILABLE = False
            tts = None  # type: ignore
            _TTS_VARIANT = "none"
    except Exception:
        _GCTTS_AVAILABLE = False
        tts = None  # type: ignore
        _TTS_VARIANT = "none"

# =========================
# 基本設定 / パス
# =========================
st.set_page_config(page_title="Shadowing MVP", page_icon="🎧", layout="centered")
st.title("シャドーイング（読み上げ）")

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
UI_DIR = ROOT_DIR / "ui"
TEXTS_PATH = DATA_DIR / "texts.json"
COMPONENT_PATH = UI_DIR / "component.html"

# =========================
# ユーティリティ（エスケープ/読み込み）
# =========================
def _html_escape(s: str) -> str:
    if s is None:
        return ""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )

def _xml_escape(s: str) -> str:
    return _html_escape(s)

@st.cache_data(show_spinner=False)
def load_texts() -> dict:
    with TEXTS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    for k in ("easy", "standard", "hard"):
        data.setdefault(k, "")
    return data

@st.cache_data(show_spinner=False)
def load_component_html() -> str:
    return COMPONENT_PATH.read_text(encoding="utf-8")

# =========================
# ブラウザTTS（外部 component.html を使用）
# =========================
def render_browser_tts(texts: dict, height: int = 520):
    ch = (
        load_component_html()
        .replace("PLACEHOLDER_EASY", repr(texts["easy"]))
        .replace("PLACEHOLDER_STANDARD", repr(texts["standard"]))
        .replace("PLACEHOLDER_HARD", repr(texts["hard"]))
    )
    html(ch, height=height, scrolling=False)
    st.caption("※ ブラウザの Web Speech API を使用（端末依存）。Android 端末では境界イベントが取れない場合があり、疑似同期でハイライトします。")

# =========================
# Google Cloud TTS（SSML <mark>）実装
# =========================
VOICE_MAP = {
    "adult_f":  ("en-US-Neural2-F", 0.0),
    "adult_m":  ("en-US-Neural2-D", 0.0),
    "teen_f":   ("en-US-Neural2-F", 2.0),
    "teen_m":   ("en-US-Neural2-D", 1.0),
    "senior_f": ("en-US-Neural2-F", -2.0),
    "senior_m": ("en-US-Neural2-D", -3.0),
}

def _split_words_for_marks(text: str):
    """
    - tokens: 表示用（空白・改行・句読点を含む）
    - words : SSML <mark> に対応させる単語列
    """
    tokens = re.findall(r"\w+|\s+|[^\w\s]", text, flags=re.UNICODE)
    words = [t for t in tokens if re.match(r"\w+", t)]
    return tokens, words

def _build_ssml_with_marks(words):
    parts = ["<speak>"]
    for i, w in enumerate(words):
        parts.append(_xml_escape(w or ""))
        parts.append(f'<mark name="w{i:04d}"/> ')
    parts.append("</speak>")
    return "".join(parts)

def _resolve_ssml_mark_enum():
    """
    版差を吸収して SSML_MARK の列挙値（または数値）を返す
    """
    try:
        return tts.SynthesizeSpeechRequest.TimepointType.SSML_MARK  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        mod = __import__(tts.__name__ + ".types", fromlist=["types"])  # type: ignore
        return mod.SynthesizeSpeechRequest.TimepointType.SSML_MARK  # type: ignore
    except Exception:
        pass
    try:
        return getattr(tts, "TimepointType").SSML_MARK  # type: ignore[attr-defined]
    except Exception:
        pass
    return 1  # 最後の砦（SSML_MARK の値）

@st.cache_data(show_spinner=False)
def synth_with_timepoints_gcp(
    words,
    voice_name: str = "en-US-Neural2-F",
    speaking_rate: float = 1.0,
    pitch_semitones: float = 0.0,
):
    """
    Google TTS で音声(MP3)と <mark> の timepoints を取得（同一引数ならキャッシュ）
    """
    if not _GCTTS_AVAILABLE:
        raise RuntimeError("google-cloud-texttospeech が未インストールです。`pip install google-cloud-texttospeech` を実行してください。")

    ssml = _build_ssml_with_marks(words)
    client = tts.TextToSpeechClient()

    input_ = tts.SynthesisInput(ssml=ssml)
    voice  = tts.VoiceSelectionParams(language_code="en-US", name=voice_name)
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.MP3,
        speaking_rate=float(speaking_rate),
        pitch=float(pitch_semitones),
    )

    # enable_time_pointing は Request 側（AudioConfig ではない）
    request = tts.SynthesizeSpeechRequest(
        input=input_,
        voice=voice,
        audio_config=audio_config,
        enable_time_pointing=[_resolve_ssml_mark_enum()],
    )
    try:
        resp = client.synthesize_speech(request=request)
    except Exception:
        # 非対応版などの保険（同期なしで合成）
        resp = client.synthesize_speech(
            request=tts.SynthesizeSpeechRequest(
                input=input_, voice=voice, audio_config=audio_config
            )
        )
        st.warning("この環境の google-cloud-texttospeech は timepoints 未対応です。単語同期は無効になります。対応版へアップグレードをご検討ください。")

    audio_b64 = base64.b64encode(resp.audio_content).decode("ascii")
    tps = [{"name": tp.mark_name, "t": tp.time_seconds} for tp in getattr(resp, "timepoints", [])]
    return audio_b64, tps

def render_cloud_tts(text: str, rate: float, voice_profile: str, height: int = 520):
    tokens, words = _split_words_for_marks(text)
    voice_name, pitch = VOICE_MAP.get(voice_profile, ("en-US-Neural2-F", 0.0))

    audio_b64, tps = synth_with_timepoints_gcp(
        words=words, voice_name=voice_name, speaking_rate=rate, pitch_semitones=pitch
    )

    # 単語は <span class="w">、空白/改行/句読点はそのまま（必ずエスケープ）
    spans_html_parts = []
    w_idx = 0
    for tk in tokens:
        if tk.strip() == "":
            spans_html_parts.append(_html_escape(tk).replace("\n", "<br/>"))
        elif tk.isalnum() or (tk and tk[0].isalnum()):
            spans_html_parts.append(f'<span class="w" data-i="{w_idx}">{_html_escape(tk)}</span>')
            w_idx += 1
        else:
            spans_html_parts.append(_html_escape(tk))
    spans_html = "".join(spans_html_parts)

    cloud_html = f"""
    <style>
      .cloud-wrap {{ max-height: 440px; overflow: auto; border:1px solid #e3e3e3; border-radius:10px; background:#f1f1f1; }}
      .cloud-reader {{ padding: 1rem .9rem .5rem; line-height: 2.1rem; font-size: 1.25rem; background:#CCC; }}
      .cloud-reader .w {{ transition: background-color 120ms ease; padding:2px 1px; border-radius:4px; }}
      .cloud-reader .w.active {{ background:#fff2a8; }}
      .cloud-controls {{ display:flex; gap:.6rem; align-items:center; margin-top:.6rem; }}
      .cloud-controls button {{ padding:.4rem .8rem;border:1px solid #ccc;border-radius:8px;background:#f7f7f7;cursor:pointer; }}
      .cloud-controls button:hover {{ background:#efefef; }}
    </style>

    <div class="cloud-wrap" id="cwrap">
      <div id="creader" class="cloud-reader">{spans_html}</div>
    </div>
    <div class="cloud-controls">
      <audio id="audio" controls src="data:audio/mp3;base64,{audio_b64}"></audio>
      <button id="restartBtn">↩ 最初に戻る</button>
    </div>

    <script>
    (function(){{
      const tps = {json.dumps(tps)};
      const audio = document.getElementById('audio');
      const wrap  = document.getElementById('cwrap');
      const spans = Array.from(document.querySelectorAll('#creader .w'));
      const restartBtn = document.getElementById('restartBtn');

      const marks = tps.map(tp => [parseInt(tp.name.replace('w','')), tp.t]).sort((a,b)=>a[1]-b[1]);

      function clearActive(){{ spans.forEach(s => s.classList.remove('active')); }}
      function hi(i){{
        clearActive();
        const s = spans[i];
        if (!s) return;
        s.classList.add('active');
        const y = s.offsetTop - wrap.clientHeight * 0.35;
        wrap.scrollTo({{ top: Math.max(0, y), behavior:'smooth' }});
      }}

      let cursor = 0;
      function syncTick(){{
        const t = audio.currentTime;
        while (cursor < marks.length && t >= marks[cursor][1]) {{
          hi(marks[cursor][0]);
          cursor++;
        }}
        if (!audio.paused && !audio.ended) requestAnimationFrame(syncTick);
      }}

      audio.playbackRate = {float(st.session_state.get("cloud_rate", 1.0))};
      audio.addEventListener('play', ()=>{{ cursor=0; requestAnimationFrame(syncTick); }});
      audio.addEventListener('seeking', ()=>{{
        const t = audio.currentTime;
        cursor = 0;
        while (cursor < marks.length && marks[cursor][1] < t) cursor++;
      }});
      audio.addEventListener('ratechange', ()=>{{ }});

      restartBtn.addEventListener('click', ()=>{{
        audio.pause();
        audio.currentTime = 0;
        cursor = 0;
        clearActive();
      }});
    }})();
    </script>
    """
    html(cloud_html, height=height, scrolling=False)
    st.caption(f"※ Google Cloud TTS（{_TTS_VARIANT} / SSML <mark> timepoints）で正確に単語同期します。速度は <audio>.playbackRate で即時反映。")

# =========================
# サイドバー（共通UI）
# =========================
with st.sidebar:
    st.subheader("設定")
    engine = st.radio(
        "音声エンジン",
        options=["ブラウザTTS（端末依存）", "Google Cloud TTS（高精度同期）"],
        index=0,
        help="Android のズレを根本解消したい場合は Google TTS を選択（要: GCP 設定）",
    )
    difficulty = st.selectbox(
        "難易度",
        options=[("easy", "中学生"), ("standard", "標準"), ("hard", "超難")],
        index=1,
        format_func=lambda x: x[1],
    )[0]
    rate = st.slider("再生速度", 0.10, 2.00, 1.00, 0.05)
    st.session_state["cloud_rate"] = rate
    voice_profile = st.selectbox(
        "声のタイプ",
        options=[
            ("adult_f", "30代 女性"),
            ("adult_m", "30代 男性"),
            ("teen_f", "10代 女性"),
            ("teen_m", "10代 男性"),
            ("senior_f", "70代 女性"),
            ("senior_m", "70代 男性"),
        ],
        index=0,
        format_func=lambda x: x[1],
    )[0]

# =========================
# 描画本体
# =========================
try:
    texts = load_texts()
except FileNotFoundError:
    st.warning("data/texts.json が見つかりません。サンプルで起動します。")
    texts = {
        "easy": "It is a bright day in April.",
        "standard": "It was a bright, cold day in April.",
        "hard": "On a lucid yet frigid April morning...",
    }

st.write("▶ 再生 / ⏸ 一時停止 / ↩ 最初に戻る。⚙（ブラウザTTS側）で **テキスト表示**・**速度**・**声タイプ**・**難易度** を調整できます。")

if engine.startswith("Google"):
    if not _GCTTS_AVAILABLE:
        st.error("google-cloud-texttospeech が未インストールです。`pip install google-cloud-texttospeech` を実行してください。")
    elif not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        st.warning("GOOGLE_APPLICATION_CREDENTIALS が未設定です。サービスアカウント JSON のパスを環境変数で指定してください。")
    else:
        render_cloud_tts(text=texts.get(difficulty, ""), rate=rate, voice_profile=voice_profile)
else:
    render_browser_tts(texts)

# EOF
