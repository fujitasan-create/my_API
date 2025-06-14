from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import plotting, search

app = FastAPI(
    title="Graph Plot API",
    description="銘柄のチャートを描画したり、銘柄名で検索できるAPIです。",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #後で変える
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(search.router)
app.include_router(plotting.router)