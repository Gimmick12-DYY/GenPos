from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from .common import BaseSchema


class MetricsIngestRequest(BaseSchema):
    note_package_id: UUID
    date: date
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    cost: float = Field(default=0.0, ge=0)
    conversions: int = Field(default=0, ge=0)
    revenue: float = Field(default=0.0, ge=0)


class MetricsBatchIngestRequest(BaseSchema):
    """BL-202: batch upsert of performance rows in one transaction."""

    items: list[MetricsIngestRequest] = Field(..., min_length=1, max_length=2000)


class MetricsBatchIngestResponse(BaseSchema):
    created: int
    updated: int
    skipped: int


class PerformanceResponse(BaseSchema):
    id: UUID
    note_package_id: UUID
    date: date
    impressions: int
    clicks: int
    saves: int
    comments: int
    cost: float
    conversions: int
    revenue: float
    created_at: datetime


class ProductPerformanceResponse(BaseSchema):
    product_id: UUID
    total_impressions: int
    total_clicks: int
    total_saves: int
    total_conversions: int
    metrics: list[PerformanceResponse]


class MetricsUploadResponse(BaseSchema):
    created: int
    updated: int


class FatigueDimensionResponse(BaseSchema):
    dimension: str
    value: str
    fatigue_score: float
    recent_impressions: int
    baseline_impressions: int
    recommendation: str


class ProductFatigueResponse(BaseSchema):
    product_id: str
    dimensions: list[FatigueDimensionResponse]
    threshold: float
