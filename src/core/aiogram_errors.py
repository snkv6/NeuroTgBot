import logging
from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)

def build_error_router() -> Router:
    router = Router()

    @router.errors()
    async def on_error(event: ErrorEvent):
        e = event.exception
        logger.error(
            "unhandled aiogram error",
            exc_info=(type(e), e, e.__traceback__),
        )
        return True

    return router
