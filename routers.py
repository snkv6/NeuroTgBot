from aiogram import Router

from features.start import router as start_router
from features.help import router as help_router
from features.profile import router as profile_router
from features.role import router as role_router
from features.model import router as model_router
from features.billing import router as billing_router
from features.request import router as chat_router

router = Router()
router.include_router(start_router)
router.include_router(help_router)
router.include_router(profile_router)
router.include_router(role_router)
router.include_router(model_router)
router.include_router(billing_router)
router.include_router(chat_router)
