import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_router
from src.core.config import settings
from src.core.storage import storage

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Ensuring S3 bucket '%s' exists…", settings.s3_bucket)
    try:
        storage.ensure_bucket()
    except Exception:
        logger.warning("Could not connect to S3/MinIO – bucket check skipped", exc_info=True)
    yield


app = FastAPI(
    title="GenPos API",
    description="XiaoHongShu AI Ads Workspace Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "genpos-api"}
