# core/ssml.py
from .tokens import is_word

def ssml_escape(s: str) -> str:
    return (s.replace("&","&amp;").replace("<","&lt;")
              .replace(">","&gt;").replace('"',"&quot;"))

def build_ssml_with_marks_and_gaps(tokens, gap_ms: int = 0) -> str:
    # 最小のSSML (必要に応じて <sub> や <phoneme> を追加していけます)
    parts = ["<speak>"]
    wi = 0
    for tk in tokens:
        if is_word(tk):
            parts.append(ssml_escape(tk))
            parts.append(f'<mark name="w{wi:04d}"/>')
            parts.append(" " if gap_ms == 0 else f'<break time="{gap_ms}ms"/>')
            wi += 1
        elif tk == "\n":
            parts.append('<break time="300ms"/>')
        else:
            parts.append(ssml_escape(tk))
    parts.append("</speak>")
    return "".join(parts)
