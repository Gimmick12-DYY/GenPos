from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from .common import BaseSchema, PaginatedResponse

# ---------------------------------------------------------------------------
# Note Package
# ---------------------------------------------------------------------------


class NotePackageResponse(BaseSchema):
    id: UUID
    merchant_id: UUID
    product_id: UUID
    asset_pack_id: UUID | None
    generation_job_id: UUID | None
    source_mode: Literal["daily_auto", "on_demand", "campaign"]
    # Stored value may be English enums or Chinese labels from generation
    objective: str
    persona: str | None
    style_family: str | None
    compliance_status: Literal["pending", "passed", "failed", "review_needed"]
    ranking_score: float | None
    review_status: Literal["pending", "approved", "rejected", "queued", "live"]
    created_at: datetime
    updated_at: datetime
    product_name: str | None = None
    cover_url: str | None = None
    # BL-208: optional fatigue hints when listing review / today queues (BL-203)
    fatigue_warning: bool | None = None
    fatigue_hints: list[str] | None = None


class NotePackageListResponse(PaginatedResponse[NotePackageResponse]):
    pass


class TextAssetCreate(BaseSchema):
    asset_role: Literal["title", "body", "first_comment", "hashtag", "cta", "cover_text"]
    content: str
    language: str = "zh-CN"
    version: int = 1


class ImageAssetCreate(BaseSchema):
    asset_role: str
    image_url: str = ""
    prompt_version: str | None = "v1"
    metadata_json: dict[str, Any] | None = None


class NotePackageCreate(BaseSchema):
    merchant_id: UUID | None = None
    product_id: UUID
    asset_pack_id: UUID | None = None
    generation_job_id: UUID | None = None
    source_mode: Literal["daily_auto", "on_demand", "campaign"] = "on_demand"
    objective: str = "seeding"
    persona: str | None = None
    style_family: str | None = None
    compliance_status: Literal["pending", "passed", "failed", "review_needed"] = "pending"
    ranking_score: float | None = None
    review_status: Literal["pending", "approved", "rejected", "queued", "live"] = "pending"
    text_assets: list[TextAssetCreate] = []
    image_assets: list[ImageAssetCreate] = []


class NotePackagePatch(BaseSchema):
    review_status: Literal["pending", "approved", "rejected", "queued", "live"] | None = None
    ranking_score: float | None = None
    expected_updated_at: datetime | None = None


class TextAssetPatch(BaseSchema):
    content: str
    expected_updated_at: datetime | None = None


# ---------------------------------------------------------------------------
# Text Assets
# ---------------------------------------------------------------------------


class TextAssetResponse(BaseSchema):
    id: UUID
    note_package_id: UUID
    asset_role: Literal["title", "body", "first_comment", "hashtag", "cta", "cover_text"]
    content: str
    language: str
    version: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Image Assets
# ---------------------------------------------------------------------------


class ImageAssetResponse(BaseSchema):
    id: UUID
    note_package_id: UUID
    asset_role: Literal["cover", "carousel_1", "carousel_2", "carousel_3", "carousel_4", "carousel_5"]
    source_asset_id: UUID | None
    derived_from: str | None
    prompt_version: str | None
    image_url: str
    metadata_json: dict[str, Any] | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Briefs
# ---------------------------------------------------------------------------


class BriefResponse(BaseSchema):
    id: UUID
    note_package_id: UUID
    brief_type: Literal["note_export", "juguang", "pugongying"]
    content_json: dict[str, Any] | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Detail (composite)
# ---------------------------------------------------------------------------


class NotePackageDetailResponse(NotePackageResponse):
    text_assets: list[TextAssetResponse] = []
    image_assets: list[ImageAssetResponse] = []
    briefs: list[BriefResponse] = []
