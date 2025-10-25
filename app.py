# app_basic.py — Public (Browser TTS only)

import streamlit as st
from core.ui import page_header, layout_basic_sidebar
from core.texts import load_texts
from core.web_component import render_browser_tts

# ページヘッダ
page_header()

# サイドバー
with st.sidebar:
    difficulty = layout_basic_sidebar()

# テキスト読込
texts = load_texts()

# 本文
render_browser_tts(texts)
st.caption("※ この公開版はブラウザTTSのみ。音声は端末のエンジンを使用します。")
