from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.orchestrator import orchestrator
from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    ApproveRequest,
    ImageAssetResponse,
    NotePackageCreate,
    NotePackageDetailResponse,
    NotePackageListResponse,
    NotePackagePatch,
    NotePackageResponse,
    RejectRequest,
    TextAssetResponse,
)
from src.services import note_package_service

router = APIRouter()


def _assert_merchant(merchant_id: UUID, token: dict) -> None:
    if str(merchant_id) != str(token.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another merchant's data",
        )


@router.get("", response_model=NotePackageListResponse)
async def list_note_packages_endpoint(
    merchant_id: UUID = Query(..., description="Merchant scope"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    review_status: str | None = Query(
        None,
        description="Filter by review_status (pending, approved, rejected, …)",
    ),
    source_mode: str | None = Query(None),
    sort: str = Query("recent", description="recent | ranking"),
    product_id: UUID | None = Query(None),
    compliance_status: str | None = Query(None),
    created_after: datetime | None = Query(None),
    created_before: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """List note packages for a merchant (内容工厂 / filtered queues)."""
    _assert_merchant(merchant_id, token)
    sort_key = "ranking" if sort == "ranking" else "recent"
    items, total = await note_package_service.list_note_packages(
        db,
        merchant_id,
        limit,
        offset,
        review_status=review_status,
        source_mode=source_mode,
        sort=sort_key,
        product_id=product_id,
        compliance_status=compliance_status,
        created_after=created_after,
        created_before=created_before,
    )
    out = [note_package_service.note_package_to_response(p) for p in items]
    return NotePackageListResponse(items=out, total=total, limit=limit, offset=offset)


@router.post("", response_model=NotePackageDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_note_package_endpoint(
    body: NotePackageCreate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """BL-110: create a note package (manual / import path)."""
    _assert_merchant(body.merchant_id, token)
    pkg = await note_package_service.create_note_package(db, body)
    base = NotePackageDetailResponse.model_validate(pkg, from_attributes=True)
    return note_package_service.detail_with_client_image_urls(pkg, base)


@router.post("/{package_id}/hydrate-images", response_model=NotePackageResponse)
async def hydrate_note_package_images(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Upload cover/carousel PNGs when image_url rows are still empty (recovery)."""
    merchant_id = UUID(str(token["sub"]))
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None or pkg.merchant_id != merchant_id:
        raise HTTPException(status_code=404, detail="Note package not found")
    if not pkg.image_assets:
        raise HTTPException(
            status_code=400,
            detail="No image assets to hydrate; generate a package first",
        )
    await orchestrator.hydrate_stale_package_images(db, pkg)
    await db.commit()
    refreshed = await note_package_service.get_note_package_detail(db, package_id)
    if refreshed is None:
        raise HTTPException(status_code=500, detail="Failed to reload note package")
    return note_package_service.note_package_to_response(refreshed)


@router.patch("/{package_id}", response_model=NotePackageResponse)
async def patch_note_package_endpoint(
    package_id: UUID,
    body: NotePackagePatch,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """BL-110: update review_status / ranking_score."""
    merchant_id = UUID(str(token["sub"]))
    pkg = await note_package_service.patch_note_package(
        db, package_id, merchant_id, body
    )
    return note_package_service.note_package_to_response(pkg)


@router.post("/{package_id}/approve", response_model=NotePackageResponse)
async def approve_note_package_note_route(
    package_id: UUID,
    body: ApproveRequest | None = None,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """BL-110: alias of review approve on note-packages resource."""
    reviewer_id = UUID(str(token["sub"]))
    reason = body.reason if body else None
    await note_package_service.approve_note_package(
        db, package_id=package_id, reviewer_id=reviewer_id, reason=reason, merchant_id=reviewer_id
    )
    full = await note_package_service.get_note_package_detail(db, package_id)
    if full is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    return note_package_service.note_package_to_response(full)


@router.post("/{package_id}/reject", response_model=NotePackageResponse)
async def reject_note_package_note_route(
    package_id: UUID,
    body: RejectRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    reviewer_id = UUID(str(token["sub"]))
    await note_package_service.reject_note_package(
        db,
        package_id=package_id,
        reviewer_id=reviewer_id,
        reason=body.reason,
        merchant_id=reviewer_id,
    )
    full = await note_package_service.get_note_package_detail(db, package_id)
    if full is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    return note_package_service.note_package_to_response(full)


@router.get("/{package_id}", response_model=NotePackageDetailResponse)
async def get_note_package(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Get full note package detail (includes text assets, image assets, briefs)."""
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    _assert_merchant(pkg.merchant_id, token)
    base = NotePackageDetailResponse.model_validate(pkg, from_attributes=True)
    return note_package_service.detail_with_client_image_urls(pkg, base)


@router.get("/{package_id}/text-assets", response_model=list[TextAssetResponse])
async def get_text_assets(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Get text assets for a note package."""
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    _assert_merchant(pkg.merchant_id, token)
    return pkg.text_assets


@router.get("/{package_id}/image-assets", response_model=list[ImageAssetResponse])
async def get_image_assets(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Get image assets for a note package."""
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    _assert_merchant(pkg.merchant_id, token)
    return note_package_service.image_assets_for_api(pkg)
