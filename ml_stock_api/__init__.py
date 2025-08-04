from fastapi import APIRouter
from .predict import router as predict_router
from .predict_5d import router as predict_5d_router
from .predict_20d import router as predict_20d_router

router = APIRouter()
router.include_router(predict_router)
router.include_router(predict_5d_router)
router.include_router(predict_20d_router)