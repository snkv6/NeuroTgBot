from aiogram import Router

from features.client_bot_handlers.start import router as start_router
from features.client_bot_handlers.help import router as help_router
from features.client_bot_handlers.profile import router as profile_router
from features.client_bot_handlers.role import router as role_router
from features.client_bot_handlers.model import router as model_router
from features.billing_service.billing import router as billing_router
from features.client_bot_handlers.request import router as chat_router
from features.client_bot_handlers.delete_context import router as delete_context_router

from features.admin_bot_handlers.test_handler import router as test_router

client_router = Router()
client_router.include_router(start_router)
client_router.include_router(role_router)
client_router.include_router(help_router)
client_router.include_router(profile_router)
client_router.include_router(model_router)
client_router.include_router(billing_router)
client_router.include_router(chat_router)
client_router.include_router(delete_context_router)

admin_router = Router()

admin_router.include_router(test_router)
