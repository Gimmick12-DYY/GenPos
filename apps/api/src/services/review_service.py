from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import NotePackage


async def get_review_queue(
    db: AsyncSession,
    merchant_id: UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[NotePackage], int]:
    base_filter = NotePackage.review_status == "pending"

    count_stmt = select(func.count()).select_from(NotePackage).where(base_filter)
    items_stmt = select(NotePackage).where(base_filter)

    if merchant_id is not None:
        merchant_filter = NotePackage.merchant_id == merchant_id
        count_stmt = count_stmt.where(merchant_filter)
        items_stmt = items_stmt.where(merchant_filter)

    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = (
        items_stmt.order_by(NotePackage.ranking_score.desc().nulls_last())
        .limit(limit)
        .offset(offset)
    )
    items = list((await db.execute(items_stmt)).scalars().all())

    return items, total
