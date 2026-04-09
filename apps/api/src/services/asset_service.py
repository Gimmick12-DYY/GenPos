from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Asset, AssetPack, Product
from src.schemas import AssetPackCreate, AssetPatch


async def get_pack_for_merchant(
    db: AsyncSession, pack_id: UUID, merchant_id: UUID
) -> AssetPack:
    pack = await db.get(AssetPack, pack_id)
    if pack is None or pack.merchant_id != merchant_id:
        raise HTTPException(status_code=404, detail="Asset pack not found")
    return pack


async def create_asset_pack(
    db: AsyncSession, merchant_id: UUID, data: AssetPackCreate
) -> AssetPack:
    pack = AssetPack(
        merchant_id=merchant_id,
        quarter_label=data.quarter_label,
        status="draft",
        effective_from=data.effective_from,
        effective_to=data.effective_to,
    )
    db.add(pack)
    await db.commit()
    await db.refresh(pack)
    return pack


async def get_asset_pack(db: AsyncSession, pack_id: UUID) -> AssetPack | None:
    return await db.get(AssetPack, pack_id)


async def list_asset_packs(
    db: AsyncSession,
    merchant_id: UUID,
    *,
    status_filter: str | None,
    limit: int,
    offset: int,
) -> tuple[list[AssetPack], int]:
    filters = [AssetPack.merchant_id == merchant_id]
    if status_filter:
        filters.append(AssetPack.status == status_filter)

    count_stmt = select(func.count()).select_from(AssetPack).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = (
        select(AssetPack)
        .where(*filters)
        .order_by(AssetPack.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list((await db.execute(items_stmt)).scalars().all())
    return items, total


def _ranges_overlap(
    a_from: date, a_to: date, b_from: date, b_to: date
) -> bool:
    return not (a_to < b_from or a_from > b_to)


async def _assert_activation_date_no_overlap(
    db: AsyncSession, pack: AssetPack, exclude_pack_id: UUID
) -> None:
    if pack.effective_from is None or pack.effective_to is None:
        return
    stmt = select(AssetPack).where(
        AssetPack.merchant_id == pack.merchant_id,
        AssetPack.status == "active",
        AssetPack.id != exclude_pack_id,
    )
    others = (await db.execute(stmt)).scalars().all()
    for o in others:
        if o.effective_from is None or o.effective_to is None:
            continue
        if _ranges_overlap(
            pack.effective_from, pack.effective_to, o.effective_from, o.effective_to
        ):
            raise HTTPException(
                status_code=400,
                detail="Effective date range overlaps another active asset pack",
            )


async def count_approved_packshots(db: AsyncSession, pack_id: UUID) -> int:
    stmt = select(func.count()).select_from(Asset).where(
        Asset.asset_pack_id == pack_id,
        Asset.type == "packshot",
        Asset.approval_status == "approved",
    )
    return int((await db.execute(stmt)).scalar_one() or 0)


async def add_asset_to_pack(
    db: AsyncSession,
    merchant_id: UUID,
    pack_id: UUID,
    file_url: str,
    asset_type: str,
    width: int,
    height: int,
    product_id: UUID | None,
    checksum: str,
) -> Asset:
    await get_pack_for_merchant(db, pack_id, merchant_id)
    pack = await db.get(AssetPack, pack_id)
    if pack and pack.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Assets can only be added while the pack is in draft status",
        )

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


async def patch_asset(
    db: AsyncSession,
    merchant_id: UUID,
    pack_id: UUID,
    asset_id: UUID,
    patch: AssetPatch,
) -> Asset:
    pack = await get_pack_for_merchant(db, pack_id, merchant_id)
    asset = await db.get(Asset, asset_id)
    if asset is None or asset.asset_pack_id != pack_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    if pack.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Assets can only be edited while the pack is in draft status",
        )
    if asset.approval_status == "approved":
        raise HTTPException(
            status_code=409,
            detail="Approved assets cannot be modified",
        )
    if patch.product_id is not None:
        prod = await db.get(Product, patch.product_id)
        if prod is None or prod.merchant_id != merchant_id:
            raise HTTPException(status_code=400, detail="Invalid product_id")
    if patch.type is not None:
        asset.type = patch.type
    if patch.product_id is not None:
        asset.product_id = patch.product_id
    await db.commit()
    await db.refresh(asset)
    return asset


def _append_asset_audit(asset: Asset, action: str, actor_sub: str | None) -> None:
    meta = dict(asset.metadata_json or {})
    log = list(meta.get("approval_audit") or [])
    log.append(
        {
            "at": datetime.now(UTC).isoformat(),
            "action": action,
            "actor_sub": actor_sub,
        }
    )
    meta["approval_audit"] = log
    asset.metadata_json = meta


async def approve_asset(
    db: AsyncSession,
    merchant_id: UUID,
    pack_id: UUID,
    asset_id: UUID,
    actor_sub: str | None,
) -> Asset:
    await get_pack_for_merchant(db, pack_id, merchant_id)
    asset = await db.get(Asset, asset_id)
    if asset is None or asset.asset_pack_id != pack_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.approval_status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending assets can be approved",
        )
    asset.approval_status = "approved"
    _append_asset_audit(asset, "approved", actor_sub)
    await db.commit()
    await db.refresh(asset)
    return asset


async def reject_asset(
    db: AsyncSession,
    merchant_id: UUID,
    pack_id: UUID,
    asset_id: UUID,
    reason: str,
    actor_sub: str | None,
) -> Asset:
    await get_pack_for_merchant(db, pack_id, merchant_id)
    asset = await db.get(Asset, asset_id)
    if asset is None or asset.asset_pack_id != pack_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.approval_status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending assets can be rejected",
        )
    asset.approval_status = "rejected"
    meta = dict(asset.metadata_json or {})
    meta["reject_reason"] = reason
    asset.metadata_json = meta
    _append_asset_audit(asset, "rejected", actor_sub)
    await db.commit()
    await db.refresh(asset)
    return asset


async def submit_asset_pack_for_review(
    db: AsyncSession, merchant_id: UUID, pack_id: UUID
) -> AssetPack:
    pack = await get_pack_for_merchant(db, pack_id, merchant_id)
    if pack.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft packs can be submitted for review",
        )
    n = await count_approved_packshots(db, pack_id)
    if n < 1:
        raise HTTPException(
            status_code=400,
            detail="Pack needs at least one approved packshot before submit",
        )
    pack.status = "pending_review"
    await db.commit()
    await db.refresh(pack)
    return pack


async def activate_asset_pack(
    db: AsyncSession, merchant_id: UUID, pack_id: UUID
) -> AssetPack:
    pack = await get_pack_for_merchant(db, pack_id, merchant_id)
    if pack.status != "pending_review":
        raise HTTPException(
            status_code=400,
            detail="Only packs in pending_review can be activated",
        )
    n = await count_approved_packshots(db, pack_id)
    if n < 1:
        raise HTTPException(
            status_code=400,
            detail="Pack needs at least one approved packshot to activate",
        )
    await _assert_activation_date_no_overlap(db, pack, pack_id)

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
