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
