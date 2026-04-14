from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import MerchantRules, NotePackage, ReviewEvent

# Well-known ID for system-generated review actions
SYSTEM_REVIEWER_ID = UUID("00000000-0000-0000-0000-000000000001")

_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


def shanghai_day_utc_bounds(for_day: date | None) -> tuple[datetime, datetime]:
    """Start (inclusive) and end (exclusive) of calendar day in Asia/Shanghai, as UTC."""
    if for_day is None:
        for_day = datetime.now(_SHANGHAI_TZ).date()
    start_local = datetime.combine(for_day, time.min, tzinfo=_SHANGHAI_TZ)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


AUTO_APPROVE_SCORE_THRESHOLD = 0.85
AUTO_APPROVE_COMPLIANCE_STATUSES = ("passed", "review_needed")


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
        .options(
            selectinload(NotePackage.product),
            selectinload(NotePackage.image_assets),
        )
        .limit(limit)
        .offset(offset)
    )
    items = list((await db.execute(items_stmt)).scalars().all())

    return items, total


async def get_review_queue_today(
    db: AsyncSession,
    merchant_id: UUID | None,
    limit: int,
    offset: int,
    for_date: date | None = None,
) -> tuple[list[NotePackage], int]:
    """今日推荐: pending daily_auto packages created on `for_date` (Shanghai), ranked by score."""
    start_utc, end_utc = shanghai_day_utc_bounds(for_date)
    base_filter = and_(
        NotePackage.review_status == "pending",
        NotePackage.source_mode == "daily_auto",
        NotePackage.created_at >= start_utc,
        NotePackage.created_at < end_utc,
    )
    count_stmt = select(func.count()).select_from(NotePackage).where(base_filter)
    items_stmt = select(NotePackage).where(base_filter)

    if merchant_id is not None:
        merchant_filter = NotePackage.merchant_id == merchant_id
        count_stmt = count_stmt.where(merchant_filter)
        items_stmt = items_stmt.where(merchant_filter)

    total = (await db.execute(count_stmt)).scalar_one()
    items_stmt = (
        items_stmt.order_by(NotePackage.ranking_score.desc().nulls_last())
        .options(
            selectinload(NotePackage.product),
            selectinload(NotePackage.image_assets),
        )
        .limit(limit)
        .offset(offset)
    )
    items = list((await db.execute(items_stmt)).scalars().all())
    return items, total


async def process_auto_approve(
    db: AsyncSession,
    merchant_id: UUID,
    score_threshold: float = AUTO_APPROVE_SCORE_THRESHOLD,
) -> int:
    """
    For merchants with review_mode=auto, approve pending packages that meet
    score and compliance thresholds. Returns count of auto-approved packages.
    """
    rules = (
        await db.execute(select(MerchantRules).where(MerchantRules.merchant_id == merchant_id))
    ).scalar_one_or_none()
    if not rules or rules.review_mode != "auto":
        return 0

    stmt = select(NotePackage).where(
        NotePackage.merchant_id == merchant_id,
        NotePackage.review_status == "pending",
        NotePackage.compliance_status.in_(AUTO_APPROVE_COMPLIANCE_STATUSES),
        NotePackage.ranking_score >= score_threshold,
    )
    packages = list((await db.execute(stmt)).scalars().all())
    for pkg in packages:
        pkg.review_status = "approved"
        db.add(
            ReviewEvent(
                note_package_id=pkg.id,
                reviewer_id=SYSTEM_REVIEWER_ID,
                action="approve",
                reason="auto_approved",
            )
        )
    await db.commit()
    return len(packages)
