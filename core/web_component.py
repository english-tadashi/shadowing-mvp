# core/web_component.py
from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html

UI_PATH = Path(__file__).resolve().parents[1] / "ui" / "component.html"

def render_browser_tts(texts: dict, height: int = 520):
    ch = UI_PATH.read_text(encoding="utf-8")
    ch = (ch.replace("PLACEHOLDER_EASY", repr(texts["easy"]))
             .replace("PLACEHOLDER_STANDARD", repr(texts["standard"]))
             .replace("PLACEHOLDER_HARD", repr(texts["hard"])))
    html(ch, height=height, scrolling=False)
