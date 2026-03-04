from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import logging

from app.database import engine, Base
from app.routes import router
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup — wrapped so a DB connection failure
    # doesn't crash uvicorn (exit status 3). The error is logged instead.
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created / verified successfully.")
    except Exception as exc:
        logger.error(
            "Could not connect to the database at startup: %s\n"
            "Make sure DATABASE_URL is set correctly in the Render environment variables.",
            exc,
        )
    yield


app = FastAPI(
    title="Bitespeed Identity Reconciliation",
    description="Link different contact identities to the same person.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["Identity"])

# Serve frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))