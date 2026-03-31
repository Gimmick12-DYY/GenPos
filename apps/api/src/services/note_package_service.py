from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.storage import client_facing_asset_url
from src.models import ImageAsset, NotePackage, ReviewEvent, TextAsset
from src.schemas.note_package import (
    ImageAssetResponse,
    NotePackageCreate,
    NotePackageDetailResponse,
    NotePackagePatch,
    NotePackageResponse,
    TextAssetPatch,
)

_COVER_ROLE_ORDER = (
    "cover",
    "carousel_1",
    "carousel_2",
    "carousel_3",
    "carousel_4",
    "carousel_5",
)


def pick_cover_url(pkg: NotePackage) -> str | None:
    """First non-empty image URL: prefer cover, then carousel slots, then any."""
    assets = pkg.image_assets or []
    for role in _COVER_ROLE_ORDER:
        for a in assets:
            if a.asset_role == role and (a.image_url or "").strip():
                return a.image_url.strip()
    for a in assets:
        if (a.image_url or "").strip():
            return a.image_url.strip()
    return None


def image_assets_for_api(pkg: NotePackage) -> list[ImageAssetResponse]:
    """Image rows with browser-loadable URLs when S3_PUBLIC_BASE_URL is set."""
    return [
        ImageAssetResponse.model_validate(ia, from_attributes=True).model_copy(
            update={"image_url": client_facing_asset_url(ia.image_url) or (ia.image_url or "")}
        )
        for ia in (pkg.image_assets or [])
    ]


def detail_with_client_image_urls(
    pkg: NotePackage, base: NotePackageDetailResponse
) -> NotePackageDetailResponse:
    row = note_package_to_response(pkg)
    return base.model_copy(
        update={
            "product_name": row.product_name,
            "cover_url": row.cover_url,
            "image_assets": image_assets_for_api(pkg),
        }
    )


def note_package_to_response(pkg: NotePackage) -> NotePackageResponse:
    """Build API row; expects product and/or image_assets loaded when available."""
    row = NotePackageResponse.model_validate(pkg, from_attributes=True)
    pname = pkg.product.name if pkg.product is not None else None
    cover = client_facing_asset_url(pick_cover_url(pkg))
    return row.model_copy(update={"product_name": pname, "cover_url": cover})


async def get_note_package(
    db: AsyncSession, package_id: UUID
) -> NotePackage | None:
    return await db.get(NotePackage, package_id)


async def get_note_package_detail(
    db: AsyncSession, package_id: UUID
) -> NotePackage | None:
    stmt = (
        select(NotePackage)
        .where(NotePackage.id == package_id)
        .options(
            selectinload(NotePackage.product),
            selectinload(NotePackage.text_assets),
            selectinload(NotePackage.image_assets),
            selectinload(NotePackage.briefs),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_note_packages(
    db: AsyncSession,
    merchant_id: UUID,
    limit: int,
    offset: int,
    review_status: str | None = None,
    source_mode: str | None = None,
    sort: str = "recent",
    product_id: UUID | None = None,
    compliance_status: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> tuple[list[NotePackage], int]:
    conditions = [NotePackage.merchant_id == merchant_id]
    if review_status is not None:
        conditions.append(NotePackage.review_status == review_status)
    if source_mode is not None:
        conditions.append(NotePackage.source_mode == source_mode)
    if product_id is not None:
        conditions.append(NotePackage.product_id == product_id)
    if compliance_status is not None:
        conditions.append(NotePackage.compliance_status == compliance_status)
    if created_after is not None:
        conditions.append(NotePackage.created_at >= created_after)
    if created_before is not None:
        conditions.append(NotePackage.created_at <= created_before)

    count_stmt = select(func.count()).select_from(NotePackage).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    base = (
        select(NotePackage)
        .where(*conditions)
        .options(
            selectinload(NotePackage.product),
            selectinload(NotePackage.image_assets),
        )
    )
    if sort == "ranking":
        order = NotePackage.ranking_score.desc().nulls_last()
    else:
        order = NotePackage.created_at.desc()

    items_stmt = base.order_by(order).limit(limit).offset(offset)
    items = list((await db.execute(items_stmt)).scalars().all())
    return items, total


async def create_note_package(
    db: AsyncSession, data: NotePackageCreate
) -> NotePackage:
    payload = data.model_dump(exclude={"text_assets", "image_assets"})
    pkg = NotePackage(**payload)
    db.add(pkg)
    await db.flush()
    for t in data.text_assets:
        db.add(
            TextAsset(
                note_package_id=pkg.id,
                asset_role=t.asset_role,
                content=t.content,
                language=t.language,
                version=t.version,
            )
        )
    for img in data.image_assets:
        db.add(
            ImageAsset(
                note_package_id=pkg.id,
                asset_role=img.asset_role,
                prompt_version=img.prompt_version,
                image_url=img.image_url or "",
                metadata_json=img.metadata_json,
            )
        )
    await db.commit()
    out = await get_note_package_detail(db, pkg.id)
    if out is None:
        raise HTTPException(status_code=500, detail="Failed to load created package")
    return out


async def patch_note_package(
    db: AsyncSession,
    package_id: UUID,
    merchant_id: UUID,
    patch: NotePackagePatch,
) -> NotePackage:
    pkg = await db.get(NotePackage, package_id)
    if pkg is None or pkg.merchant_id != merchant_id:
        raise HTTPException(status_code=404, detail="Note package not found")
    if patch.expected_updated_at is not None and pkg.updated_at != patch.expected_updated_at:
        raise HTTPException(
            status_code=409,
            detail="Note package was modified by another request",
        )
    if patch.review_status is not None:
        pkg.review_status = patch.review_status
    if patch.ranking_score is not None:
        pkg.ranking_score = patch.ranking_score
    await db.commit()
    reloaded = await get_note_package_detail(db, package_id)
    if reloaded is None:
        raise HTTPException(status_code=500, detail="Failed to reload note package")
    return reloaded


async def patch_text_asset(
    db: AsyncSession,
    text_asset_id: UUID,
    merchant_id: UUID,
    patch: TextAssetPatch,
) -> TextAsset:
    ta = await db.get(TextAsset, text_asset_id)
    if ta is None:
        raise HTTPException(status_code=404, detail="Text asset not found")
    pkg = await db.get(NotePackage, ta.note_package_id)
    if pkg is None or pkg.merchant_id != merchant_id:
        raise HTTPException(status_code=404, detail="Text asset not found")
    ta.content = patch.content
    await db.commit()
    await db.refresh(ta)
    return ta


async def approve_note_package(
    db: AsyncSession,
    package_id: UUID,
    reviewer_id: UUID,
    reason: str | None = None,
    merchant_id: UUID | None = None,
) -> NotePackage:
    pkg = await db.get(NotePackage, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    if merchant_id is not None and pkg.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    pkg.review_status = "approved"

    event = ReviewEvent(
        note_package_id=package_id,
        reviewer_id=reviewer_id,
        action="approve",
        reason=reason,
    )
    db.add(event)
    await db.commit()
    await db.refresh(pkg)
    return pkg


async def reject_note_package(
    db: AsyncSession,
    package_id: UUID,
    reviewer_id: UUID,
    reason: str,
    merchant_id: UUID | None = None,
) -> NotePackage:
    pkg = await db.get(NotePackage, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    if merchant_id is not None and pkg.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    pkg.review_status = "rejected"

    event = ReviewEvent(
        note_package_id=package_id,
        reviewer_id=reviewer_id,
        action="reject",
        reason=reason,
    )
    db.add(event)
    await db.commit()
    await db.refresh(pkg)
    return pkg
