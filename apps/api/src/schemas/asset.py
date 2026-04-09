from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from .common import BaseSchema, PaginatedResponse

# ---------------------------------------------------------------------------
# Asset Packs
# ---------------------------------------------------------------------------

class AssetPackCreate(BaseSchema):
    merchant_id: UUID | None = None
    quarter_label: str = Field(..., max_length=16)
    effective_from: date | None = None
    effective_to: date | None = None


class AssetPackResponse(BaseSchema):
    id: UUID
    merchant_id: UUID
    quarter_label: str
    status: Literal["draft", "pending_review", "active", "archived"]
    effective_from: date | None
    effective_to: date | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

class AssetResponse(BaseSchema):
    id: UUID
    asset_pack_id: UUID
    product_id: UUID | None
    type: Literal["packshot", "cutout", "logo", "packaging_ref", "hero", "other"]
    storage_url: str
    width: int | None
    height: int | None
    metadata_json: dict[str, Any] | None
    approval_status: Literal["pending", "approved", "rejected"]
    created_at: datetime


class AssetListResponse(PaginatedResponse[AssetResponse]):
    pass


class AssetPackListResponse(PaginatedResponse[AssetPackResponse]):
    pass


class AssetPatch(BaseSchema):
    """Tag uploaded assets (BL-301 step 3). Cannot change approved assets."""

    type: Literal["packshot", "cutout", "logo", "packaging_ref", "hero", "other"] | None = None
    product_id: UUID | None = None


class AssetRejectRequest(BaseSchema):
    reason: str = Field(default="", max_length=512)
