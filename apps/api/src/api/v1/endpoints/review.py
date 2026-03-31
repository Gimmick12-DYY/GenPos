from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.orchestrator import orchestrator
from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    ApproveRequest,
    HydrateMissingImagesResponse,
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
    out = [note_package_service.note_package_to_response(p) for p in items]
    return ReviewQueueResponse(items=out, total=total, limit=limit, offset=offset)


@router.get("/queue/today", response_model=ReviewQueueResponse)
async def get_review_queue_today(
    merchant_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    for_date: date | None = Query(
        None,
        description="Calendar day in Asia/Shanghai (default: today); filters daily_auto slate.",
    ),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """今日推荐: pending daily_auto packages for the given Shanghai calendar day."""
    items, total = await review_service.get_review_queue_today(
        db,
        merchant_id=merchant_id,
        limit=limit,
        offset=offset,
        for_date=for_date,
    )
    out = [note_package_service.note_package_to_response(p) for p in items]
    return ReviewQueueResponse(items=out, total=total, limit=limit, offset=offset)


@router.post("/hydrate-missing-images", response_model=HydrateMissingImagesResponse)
async def hydrate_missing_review_images(
    merchant_id: UUID = Query(...),
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Backfill PNGs for pending packages that have image rows but empty image_url."""
    if str(merchant_id) != str(token.get("sub")):
        raise HTTPException(status_code=403, detail="Cannot access another merchant's data")
    items, _ = await review_service.get_review_queue(
        db, merchant_id=merchant_id, limit=200, offset=0
    )
    processed = 0
    for p in items:
        if note_package_service.pick_cover_url(p) is not None:
            continue
        if not p.image_assets:
            continue
        detail = await note_package_service.get_note_package_detail(db, p.id)
        if detail is None:
            continue
        await orchestrator.hydrate_stale_package_images(db, detail)
        processed += 1
        if processed >= limit:
            break
    await db.commit()
    return HydrateMissingImagesResponse(processed=processed)


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
    await note_package_service.approve_note_package(
        db,
        package_id=package_id,
        reviewer_id=reviewer_id,
        reason=reason,
        merchant_id=reviewer_id,
    )
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    return note_package_service.note_package_to_response(pkg)


@router.post("/{package_id}/reject", response_model=NotePackageResponse)
async def reject_note_package(
    package_id: UUID,
    body: RejectRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Reject a note package with reason."""
    reviewer_id = UUID(token["sub"])
    await note_package_service.reject_note_package(
        db,
        package_id=package_id,
        reviewer_id=reviewer_id,
        reason=body.reason,
        merchant_id=reviewer_id,
    )
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    return note_package_service.note_package_to_response(pkg)
