"""
Enterprise Knowledge Assistant
FastAPI Application

Application entry point.

Responsibilities
----------------
- Create FastAPI application
- Configure metadata
- Register middleware
- Register exception handlers
- Include API routes
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger(__name__)


# =====================================================================
# Application Lifespan
# =====================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    """

    logger.info("=" * 60)
    logger.info("%s starting...", settings.APP_NAME)
    logger.info("Environment : %s", settings.APP_ENV)
    logger.info("LLM         : %s", settings.GROQ_MODEL)
    logger.info("Embeddings  : %s", settings.EMBEDDING_MODEL)
    logger.info("=" * 60)

    yield

    logger.info("=" * 60)
    logger.info("%s shutting down...", settings.APP_NAME)
    logger.info("=" * 60)


# =====================================================================
# FastAPI Application
# =====================================================================


app = FastAPI(

    title=settings.APP_NAME,

    description="""
        Enterprise Knowledge Assistant

        Production-grade Retrieval-Augmented Generation (RAG)
        application for querying enterprise documents using
        natural language.

        Features

        - Semantic Search
        - ChromaDB Vector Store
        - MMR Retrieval
        - Groq LLM
        - Source Citations
        - Hallucination Prevention
    """,

    version="1.0.0",

    docs_url="/docs",

    redoc_url="/redoc",

    openapi_url="/openapi.json",

    lifespan=lifespan,

)


# =====================================================================
# Middleware
# =====================================================================


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):
    """
    Logs every HTTP request.
    """

    start = time.perf_counter()

    response = await call_next(request)

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    logger.info(
        "%s %s -> %d (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )

    response.headers["X-Process-Time"] = (
        f"{elapsed:.2f} ms"
    )

    return response


# =====================================================================
# Exception Handlers
# =====================================================================


@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Handles validation errors.
    """

    logger.warning(
        "Validation error: %s",
        exc.errors(),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Invalid request.",
        },
    )


@app.exception_handler(
    Exception
)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Global exception handler.
    """

    logger.exception(
        "Unhandled exception: %s",
        exc,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "message": "Internal server error.",
        },
    )


# =====================================================================
# Include Routers
# =====================================================================


app.include_router(router)


# =====================================================================
# Entry Point
# =====================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )