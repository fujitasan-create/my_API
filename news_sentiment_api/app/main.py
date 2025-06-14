from fastapi import FastAPI
from app.routers import analyzer

app = FastAPI()
app.include_router(analyzer.router)