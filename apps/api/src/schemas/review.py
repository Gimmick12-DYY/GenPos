from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from .common import BaseSchema, PaginatedResponse
from .note_package import NotePackageResponse


class ReviewQueueResponse(PaginatedResponse[NotePackageResponse]):
    pass


class HydrateMissingImagesResponse(BaseSchema):
    """Batch backfill for note packages with image rows but empty URLs."""

    processed: int


class ApproveRequest(BaseSchema):
    reason: str | None = None


class RejectRequest(BaseSchema):
    reason: str = Field(..., min_length=1)


class ReviewEventResponse(BaseSchema):
    id: UUID
    note_package_id: UUID
    reviewer_id: UUID
    action: Literal["approve", "reject", "request_revision", "escalate"]
    reason: str | None
    created_at: datetime
