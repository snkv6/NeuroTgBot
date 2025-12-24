from aiogram import Router

from features.client_bot_handlers.start import router as start_router
from features.client_bot_handlers.help import router as help_router
from features.client_bot_handlers.profile import router as profile_router
from features.client_bot_handlers.role import router as role_router
from features.client_bot_handlers.model import router as model_router
from features.billing_service.billing import router as billing_router
from features.client_bot_handlers.delete_context import router as delete_context_router
from features.client_bot_handlers.text import router as text_router
from features.client_bot_handlers.image import router as photo_router
from features.client_bot_handlers.document import router as document_router

from features.admin_bot_handlers.admin_start import router as admin_start_router
from features.admin_bot_handlers.admin_message import router as admin_message_router
from features.admin_bot_handlers.admin_stat import router as admin_stat_router

client_router = Router()
client_router.include_router(start_router)
client_router.include_router(role_router)
client_router.include_router(help_router)
client_router.include_router(profile_router)
client_router.include_router(model_router)
client_router.include_router(billing_router)
client_router.include_router(delete_context_router)
client_router.include_router(text_router)
client_router.include_router(photo_router)
client_router.include_router(document_router)

admin_router = Router()
admin_router.include_router(admin_start_router)
admin_router.include_router(admin_message_router)
admin_router.include_router(admin_stat_router)
