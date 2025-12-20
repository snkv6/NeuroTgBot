import os
import uvicorn

from features.billing_service.webhook_app import app

async def run_webhook_server() -> None:
    port = int(os.getenv("PORT", "8000"))
    if not port:
        raise Exception("PORT environment variable not set")

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        loop="asyncio",
        lifespan="on",
    )
    server = uvicorn.Server(config)
    await server.serve()