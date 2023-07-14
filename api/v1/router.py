from fastapi import APIRouter

from .audio import router as audio_router
from .auth import router as auth_router
from .comparison import router as comparison_router
from .image import router as image_router
from .task import router as task_router

router = APIRouter(prefix="/v1")

router.include_router(audio_router)
router.include_router(image_router)
router.include_router(auth_router)
router.include_router(comparison_router)
router.include_router(task_router)
