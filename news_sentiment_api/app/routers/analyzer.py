from fastapi import APIRouter
from app.services.scraper import scrape_titles_yahoo_business
from app.services.sentiment import load_sentiment_words, compute_emotion_score
import random

router = APIRouter()

# 起動時に一度だけ辞書を読み込む
sentiment_dict = load_sentiment_words()

@router.get("/analyze-yahoo-business", response_model=dict)
def analyze_yahoo_business():
    url = "https://news.yahoo.co.jp/categories/business"
    
    # Yahooニュースのタイトルを取得
    titles = scrape_titles_yahoo_business(url)
    
    # 各タイトルにスコアを付ける
    scores = [compute_emotion_score(title, sentiment_dict) for title in titles]

    if not scores:
        return {"representative_score": 3}  # デフォルト（何も取れなかったとき）

    # 平均スコアを四捨五入
    avg = sum(scores) / len(scores)
    rounded = round(avg)

    # -1, 0, +1 のどれかをランダムで加える
    random_bias = random.choice([-1, 0, 1])
    adjusted = rounded + random_bias

    # スコアは 0〜5 の範囲に制限
    final_score = max(0, min(5, adjusted))

    return {
        "representative_score": final_score
    }