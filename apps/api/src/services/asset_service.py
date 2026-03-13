from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Asset, AssetPack
from src.schemas import AssetPackCreate


async def create_asset_pack(db: AsyncSession, data: AssetPackCreate) -> AssetPack:
    pack = AssetPack(**data.model_dump())
    db.add(pack)
    await db.commit()
    await db.refresh(pack)
    return pack


async def get_asset_pack(db: AsyncSession, pack_id: UUID) -> AssetPack | None:
    return await db.get(AssetPack, pack_id)


async def add_asset_to_pack(
    db: AsyncSession,
    pack_id: UUID,
    file_url: str,
    asset_type: str,
    width: int,
    height: int,
    product_id: UUID | None,
    checksum: str,
) -> Asset:
    pack = await db.get(AssetPack, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Asset pack not found")

    asset = Asset(
        asset_pack_id=pack_id,
        product_id=product_id,
        type=asset_type,
        storage_url=file_url,
        width=width,
        height=height,
        checksum=checksum,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


async def list_assets(
    db: AsyncSession, pack_id: UUID, limit: int, offset: int
) -> tuple[list[Asset], int]:
    count_stmt = (
        select(func.count())
        .select_from(Asset)
        .where(Asset.asset_pack_id == pack_id)
    )
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = (
        select(Asset)
        .where(Asset.asset_pack_id == pack_id)
        .order_by(Asset.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list((await db.execute(items_stmt)).scalars().all())

    return items, total


async def activate_asset_pack(db: AsyncSession, pack_id: UUID) -> AssetPack:
    pack = await db.get(AssetPack, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Asset pack not found")

    archive_stmt = (
        update(AssetPack)
        .where(
            AssetPack.merchant_id == pack.merchant_id,
            AssetPack.quarter_label == pack.quarter_label,
            AssetPack.status == "active",
            AssetPack.id != pack_id,
        )
        .values(status="archived")
    )
    await db.execute(archive_stmt)

    pack.status = "active"
    await db.commit()
    await db.refresh(pack)
    return pack
