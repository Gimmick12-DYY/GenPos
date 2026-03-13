from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.services import export_service

router = APIRouter()


@router.post("/{package_id}/note")
async def export_note_bundle(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Export note package as XiaoHongShu 笔记 bundle."""
    return await export_service.export_note_bundle(db, package_id)


@router.post("/{package_id}/juguang")
async def export_juguang_bundle(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Export note package as 聚光 (Spotlight) ad creative bundle."""
    return await export_service.export_juguang_bundle(db, package_id)


@router.post("/{package_id}/pugongying")
async def export_pugongying_bundle(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Export note package as 蒲公英 (Dandelion) KOL brief bundle."""
    return await export_service.export_pugongying_bundle(db, package_id)
