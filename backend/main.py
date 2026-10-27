"""DocuMind AI - FastAPI Application Entry Point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import init_db
from routers import (
    documents,
    chat,
    summarization,
    extraction,
    comparison,
    quiz,
    reports,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("documind")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hook: run on startup and shutdown."""
    logger.info("Initializing DocuMind AI database...")
    init_db()
    logger.info("Database initialized successfully.")

    # Warm up local embedding model so subsequent uploads process in <1s
    try:
        from services.embedding_service import _get_model
        _get_model()
        logger.info("Embedding model loaded and ready.")
    except Exception as e:
        logger.warning("Could not pre-load embedding model: %s", e)

    yield
    logger.info("Shutting down DocuMind AI backend...")


app = FastAPI(
    title="DocuMind AI API",
    description="Intelligent Document Intelligence & RAG Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(summarization.router)
app.include_router(extraction.router)
app.include_router(comparison.router)
app.include_router(quiz.router)
app.include_router(reports.router)


@app.get("/api/health", tags=["system"])
def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "service": "DocuMind AI Backend",
        "groq_configured": bool(settings.GROQ_API_KEY),
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_model": settings.LLM_MODEL,
    }


@app.get("/", tags=["system"])
def root():
    return {
        "message": "Welcome to DocuMind AI API",
        "docs_url": "/docs",
        "health_url": "/api/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to avoid leaking secrets or system paths."""
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
