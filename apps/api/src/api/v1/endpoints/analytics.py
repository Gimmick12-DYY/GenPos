from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    MetricsBatchIngestRequest,
    MetricsBatchIngestResponse,
    MetricsIngestRequest,
    MetricsUploadResponse,
    PerformanceResponse,
    ProductPerformanceResponse,
)
from src.services import analytics_service

router = APIRouter()


@router.post("/upload", response_model=MetricsUploadResponse)
async def upload_metrics_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """
    Upload a CSV of performance metrics. Headers: note_package_id,date,impressions,clicks,saves,comments,cost,conversions,revenue
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    content = await file.read()
    return await analytics_service.ingest_metrics_csv(db, content)


@router.post(
    "/ingest",
    response_model=PerformanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_metrics(
    body: MetricsIngestRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Ingest XiaoHongShu performance metrics (upsert by note_package_id + date)."""
    return await analytics_service.ingest_metrics(db, body)


@router.post(
    "/ingest-batch",
    response_model=MetricsBatchIngestResponse,
    status_code=status.HTTP_200_OK,
)
async def ingest_metrics_batch(
    body: MetricsBatchIngestRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """BL-202: batch upsert (single transaction)."""
    return await analytics_service.ingest_metrics_batch(db, body.items)


@router.get(
    "/products/{product_id}/performance",
    response_model=ProductPerformanceResponse,
)
async def get_product_performance(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get aggregated performance metrics for a product across all its note packages."""
    return await analytics_service.get_product_performance(db, product_id)


@router.get(
    "/note-packages/{package_id}/performance",
    response_model=list[PerformanceResponse],
)
async def get_note_package_performance(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get daily performance metrics for a specific note package."""
    return await analytics_service.get_note_package_performance(db, package_id)
