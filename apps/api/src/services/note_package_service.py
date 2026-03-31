from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import NotePackage, ReviewEvent


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
) -> tuple[list[NotePackage], int]:
    conditions = [NotePackage.merchant_id == merchant_id]
    if review_status is not None:
        conditions.append(NotePackage.review_status == review_status)
    if source_mode is not None:
        conditions.append(NotePackage.source_mode == source_mode)

    count_stmt = select(func.count()).select_from(NotePackage).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    base = (
        select(NotePackage)
        .where(*conditions)
        .options(selectinload(NotePackage.product))
    )
    if sort == "ranking":
        order = NotePackage.ranking_score.desc().nulls_last()
    else:
        order = NotePackage.created_at.desc()

    items_stmt = base.order_by(order).limit(limit).offset(offset)
    items = list((await db.execute(items_stmt)).scalars().all())
    return items, total


async def approve_note_package(
    db: AsyncSession,
    package_id: UUID,
    reviewer_id: UUID,
    reason: str | None = None,
) -> NotePackage:
    pkg = await db.get(NotePackage, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")

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
) -> NotePackage:
    pkg = await db.get(NotePackage, package_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")

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
