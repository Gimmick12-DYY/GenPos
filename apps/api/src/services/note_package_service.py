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
) -> tuple[list[NotePackage], int]:
    base = select(NotePackage).where(NotePackage.merchant_id == merchant_id)
    count_base = (
        select(func.count())
        .select_from(NotePackage)
        .where(NotePackage.merchant_id == merchant_id)
    )

    if review_status is not None:
        base = base.where(NotePackage.review_status == review_status)
        count_base = count_base.where(NotePackage.review_status == review_status)
    if source_mode is not None:
        base = base.where(NotePackage.source_mode == source_mode)
        count_base = count_base.where(NotePackage.source_mode == source_mode)

    total = (await db.execute(count_base)).scalar_one()

    items_stmt = (
        base.order_by(NotePackage.ranking_score.desc().nulls_last())
        .limit(limit)
        .offset(offset)
    )
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
