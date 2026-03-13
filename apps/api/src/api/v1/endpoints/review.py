from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    ApproveRequest,
    NotePackageResponse,
    RejectRequest,
    ReviewQueueResponse,
)
from src.services import note_package_service, review_service

router = APIRouter()


@router.get("/queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    merchant_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get review queue for a merchant (note packages pending review, ranked by score)."""
    items, total = await review_service.get_review_queue(
        db, merchant_id=merchant_id, limit=limit, offset=offset
    )
    return ReviewQueueResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("/{package_id}/approve", response_model=NotePackageResponse)
async def approve_note_package(
    package_id: UUID,
    body: ApproveRequest | None = None,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Approve a note package."""
    reviewer_id = UUID(token["sub"])
    reason = body.reason if body else None
    return await note_package_service.approve_note_package(
        db, package_id=package_id, reviewer_id=reviewer_id, reason=reason
    )


@router.post("/{package_id}/reject", response_model=NotePackageResponse)
async def reject_note_package(
    package_id: UUID,
    body: RejectRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Reject a note package with reason."""
    reviewer_id = UUID(token["sub"])
    return await note_package_service.reject_note_package(
        db, package_id=package_id, reviewer_id=reviewer_id, reason=body.reason
    )
