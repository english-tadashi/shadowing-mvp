# core/texts.py
from pathlib import Path
import json
import streamlit as st

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "texts.json"

@st.cache_data(show_spinner=False)
def load_texts() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    for k in ("easy", "standard", "hard"):
        d.setdefault(k, "")
    return d
