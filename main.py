from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 各APIのrouterをインポート（router = APIRouter() が定義されているもの）
from ContactAPI import main as contact_router
from graph_plot_api.app import plotting as plot_router
from graph_plot_api.app import search as search_router
from news_sentiment_api.app.routers import analyzer as sentiment_router

app = FastAPI(
    title="かぶちゃんAPI",
    description="株価予測・感情分析・問い合わせなど統合したAPI",
    version="1.0.0"
)

# CORS設定（必要に応じて変更）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # セキュリティ上制限するならここを明示的に
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 各APIルーターを登録
app.include_router(contact_router.router, prefix="/contact", tags=["Contact"])
app.include_router(plot_router.router, prefix="/plot", tags=["Graph Plot"])
app.include_router(search_router.router, prefix="/search", tags=["Search"])
app.include_router(sentiment_router.router, prefix="/sentiment", tags=["Sentiment"])