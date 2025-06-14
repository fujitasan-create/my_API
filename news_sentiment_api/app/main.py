from fastapi import FastAPI
from .routers import analyzer

app = FastAPI()
app.include_router(analyzer.router)