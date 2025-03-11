from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from app.entrypoint.fastapi.routers import routers
from app.config.config import config
from app.application import application_startup, application_shutdown


__all__ = ("create_app", )


def create_app() -> FastAPI:

    async def on_startup(app: FastAPI) -> None:
        print("Starting up")
        await application_startup()

    async def on_shutdown(app: FastAPI) -> None:
        print("Shutting down")
        await application_shutdown()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        await on_startup(app)
        try:
            yield
        finally:
            await on_shutdown(app)

    app = FastAPI(
        title=config.app.title,
        description=config.app.description,
        version=config.app.version,
        lifespan=lifespan,
    )

    for router in routers:
        app.include_router(router)

    return app
