# core/tokens.py
import re
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?", re.UNICODE)

def is_word(token: str) -> bool:
    return bool(WORD_RE.fullmatch(token))

def split_tokens(text: str):
    # 単語/空白/記号へ分割
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\s+|[^\w\s]", text, flags=re.UNICODE)
