from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    ImageAssetResponse,
    NotePackageDetailResponse,
    TextAssetResponse,
)
from src.services import note_package_service

router = APIRouter()


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
    return pkg


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
