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


app = create_app()
