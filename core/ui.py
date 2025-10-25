# core/ui.py
import streamlit as st

def layout_basic_sidebar():
    st.subheader("設定")
    difficulty = st.selectbox(
        "難易度", options=[("easy","中学生"),("standard","標準"),("hard","超難")],
        index=1, format_func=lambda x: x[1]
    )[0]
    return difficulty

def page_header():
    st.set_page_config(page_title="Shadowing MVP", page_icon="🎧", layout="centered")
    st.title("シャドーイング（読み上げ）")
    st.write("▶ 再生 / ⏸ 一時停止 / ↩ 最初に戻る。ブラウザTTSは端末依存です。")
