import os
from app.config import SENTIMENT_DICT_PATH

POSITIVE_CATEGORIES = ['suki', 'yasu', 'yorokobi', 'odoroki']
NEGATIVE_CATEGORIES = ['ikari', 'iya', 'kowa', 'aware', 'haji', 'takaburi']

def load_sentiment_words() -> dict:
    sentiment_map = {}
    for fname in os.listdir(SENTIMENT_DICT_PATH):
        if fname.endswith(".txt"):
            category = fname.replace("_uncoded.txt", "")
            with open(os.path.join(SENTIMENT_DICT_PATH, fname), encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
                sentiment_map[category] = words
    return sentiment_map

def compute_emotion_score(text: str, sentiment_dict: dict) -> int:
    pos_score = 0
    neg_score = 0

    for category, words in sentiment_dict.items():
        match_count = sum(1 for word in words if word in text)
        if category in POSITIVE_CATEGORIES:
            pos_score += match_count
        elif category in NEGATIVE_CATEGORIES:
            neg_score += match_count

    raw_score = pos_score - neg_score

    # 中立回避のため、±0は±1へ寄せる
    if raw_score == 0:
        raw_score = 1 if pos_score >= neg_score else -1

    # スコアを -3〜+3 にクリップ（最大3段階）
    if raw_score > 3:
        raw_score = 3
    elif raw_score < -3:
        raw_score = -3

    # -3〜+3 → 0〜5 へ変換
    return raw_score + 3
