from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import NotePackage, PerformanceMetrics, Product
from src.schemas import MetricsIngestRequest


async def ingest_metrics(
    db: AsyncSession, data: MetricsIngestRequest
) -> PerformanceMetrics:
    pkg = await db.get(NotePackage, data.note_package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")

    stmt = select(PerformanceMetrics).where(
        PerformanceMetrics.note_package_id == data.note_package_id,
        PerformanceMetrics.date == data.date,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing is not None:
        for field, value in data.model_dump(exclude={"note_package_id", "date"}).items():
            setattr(existing, field, value)
        metrics = existing
    else:
        metrics = PerformanceMetrics(**data.model_dump())
        db.add(metrics)

    await db.commit()
    await db.refresh(metrics)
    return metrics


async def get_product_performance(db: AsyncSession, product_id: UUID) -> dict:
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    agg_stmt = (
        select(
            func.coalesce(func.sum(PerformanceMetrics.impressions), 0).label(
                "total_impressions"
            ),
            func.coalesce(func.sum(PerformanceMetrics.clicks), 0).label(
                "total_clicks"
            ),
            func.coalesce(func.sum(PerformanceMetrics.saves), 0).label(
                "total_saves"
            ),
            func.coalesce(func.sum(PerformanceMetrics.conversions), 0).label(
                "total_conversions"
            ),
        )
        .select_from(PerformanceMetrics)
        .join(NotePackage, PerformanceMetrics.note_package_id == NotePackage.id)
        .where(NotePackage.product_id == product_id)
    )
    agg_row = (await db.execute(agg_stmt)).one()

    metrics_stmt = (
        select(PerformanceMetrics)
        .join(NotePackage, PerformanceMetrics.note_package_id == NotePackage.id)
        .where(NotePackage.product_id == product_id)
        .order_by(PerformanceMetrics.date.desc())
    )
    metrics = list((await db.execute(metrics_stmt)).scalars().all())

    return {
        "product_id": product_id,
        "total_impressions": int(agg_row.total_impressions),
        "total_clicks": int(agg_row.total_clicks),
        "total_saves": int(agg_row.total_saves),
        "total_conversions": int(agg_row.total_conversions),
        "metrics": metrics,
    }


async def get_note_package_performance(
    db: AsyncSession, package_id: UUID
) -> list[PerformanceMetrics]:
    pkg = await db.get(NotePackage, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")

    stmt = (
        select(PerformanceMetrics)
        .where(PerformanceMetrics.note_package_id == package_id)
        .order_by(PerformanceMetrics.date.desc())
    )
    return list((await db.execute(stmt)).scalars().all())
