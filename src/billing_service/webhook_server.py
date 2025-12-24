import os
import uvicorn

from src.billing_service.webhook_app import app

async def run_webhook_server():
    port = int(os.environ.get("PORT", "8000"))
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