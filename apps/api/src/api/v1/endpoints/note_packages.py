from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    ImageAssetResponse,
    NotePackageDetailResponse,
    NotePackageListResponse,
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
    )
    out = [note_package_service.note_package_to_response(p) for p in items]
    return NotePackageListResponse(items=out, total=total, limit=limit, offset=offset)


@router.get("/{package_id}", response_model=NotePackageDetailResponse)
async def get_note_package(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get full note package detail (includes text assets, image assets, briefs)."""
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    base = NotePackageDetailResponse.model_validate(pkg, from_attributes=True)
    row = note_package_service.note_package_to_response(pkg)
    return base.model_copy(
        update={"product_name": row.product_name, "cover_url": row.cover_url}
    )


@router.get("/{package_id}/text-assets", response_model=list[TextAssetResponse])
async def get_text_assets(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get text assets for a note package."""
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    return pkg.text_assets


@router.get("/{package_id}/image-assets", response_model=list[ImageAssetResponse])
async def get_image_assets(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get image assets for a note package."""
    pkg = await note_package_service.get_note_package_detail(db, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    return pkg.image_assets
