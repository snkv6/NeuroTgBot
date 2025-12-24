import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from src.billing_service.webhook_app import app

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def unhandled_http_error(request: Request, exc: Exception):
    logger.exception(
        "unhandled http error method=%s path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse({"detail": "Internal error"}, status_code=500)