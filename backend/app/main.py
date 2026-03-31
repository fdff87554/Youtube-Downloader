"""YouTube Downloader FastAPI application."""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance with CORS middleware and exception handlers.
    """
    app = FastAPI(
        title="YouTube Downloader API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    _configure_cors(app)
    _configure_exception_handlers(app)
    _include_routers(app)
    _add_health_check(app)

    return app


def _configure_cors(app: FastAPI) -> None:
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )


def _configure_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception")
        debug = os.environ.get("DEBUG", "false").lower() == "true"
        detail = str(exc) if debug else "Internal server error"
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": detail}},
        )


def _add_health_check(app: FastAPI) -> None:
    @app.get("/api/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}


def _include_routers(app: FastAPI) -> None:
    from app.routers.download import router as download_router
    from app.routers.info import router as info_router

    app.include_router(info_router)
    app.include_router(download_router)


app = create_app()
