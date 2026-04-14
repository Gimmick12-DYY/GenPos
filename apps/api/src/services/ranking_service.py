"""
BL-206: Ranking and scoring engine. Computes composite score from compliance confidence,
optional performance signals (CTR, save rate), and style diversity.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import NotePackage, PerformanceMetrics

# Weights for composite score (must sum to 1.0)
WEIGHT_COMPLIANCE = 0.5
WEIGHT_ENGAGEMENT = 0.3
WEIGHT_DIVERSITY = 0.2


async def compute_composite_scores(
    db: AsyncSession,
    package_ids: list[UUID],
) -> list[tuple[UUID, float]]:
    """
    Compute composite ranking score for each note package.
    Returns list of (package_id, score) sorted by score descending.
    """
    if not package_ids:
        return []

    stmt = select(NotePackage).where(NotePackage.id.in_(package_ids))
    packages = list((await db.execute(stmt)).scalars().all())
    # Engagement: get recent performance per package (sum last 30 days)
    perf_stmt = (
        select(
            PerformanceMetrics.note_package_id,
            func.coalesce(func.sum(PerformanceMetrics.impressions), 0).label("impressions"),
            func.coalesce(func.sum(PerformanceMetrics.clicks), 0).label("clicks"),
            func.coalesce(func.sum(PerformanceMetrics.saves), 0).label("saves"),
        )
        .where(
            PerformanceMetrics.note_package_id.in_(package_ids),
        )
        .group_by(PerformanceMetrics.note_package_id)
    )
    perf_result = await db.execute(perf_stmt)
    perf_map = {r.note_package_id: r for r in perf_result.all()}

    # Pre-count styles for diversity
    style_counts: dict[str, int] = {}
    for pkg in packages:
        style_key = pkg.style_family or "default"
        style_counts[style_key] = style_counts.get(style_key, 0) + 1
    total_packages = len(packages)

    max_ctr = 0.08
    max_save_rate = 0.15
    scored: list[tuple[UUID, float]] = []
    for pkg in packages:
        comp = float(pkg.ranking_score or 0.5)
        comp = max(0, min(1, comp))

        perf = perf_map.get(pkg.id)
        if perf and perf.impressions and int(perf.impressions) > 0:
            ctr = int(perf.clicks or 0) / int(perf.impressions)
            save_rate = int(perf.saves or 0) / int(perf.impressions)
            eng = 0.5 * min(1, ctr / max_ctr) + 0.5 * min(1, save_rate / max_save_rate)
        else:
            eng = 0.5  # neutral when no data

        style_key = pkg.style_family or "default"
        count = style_counts.get(style_key, 0)
        diversity = 1.0 - (count - 1) / total_packages if total_packages else 0.5
        diversity = max(0, min(1, diversity))

        composite = WEIGHT_COMPLIANCE * comp + WEIGHT_ENGAGEMENT * eng + WEIGHT_DIVERSITY * diversity
        composite = round(composite, 4)
        scored.append((pkg.id, composite))

    # Sort by composite descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


async def update_ranking_scores(
    db: AsyncSession,
    package_ids: list[UUID],
) -> list[tuple[UUID, float]]:
    """
    Compute composite scores and persist to note_packages.ranking_score.
    Returns sorted list of (package_id, score).
    """
    scored = await compute_composite_scores(db, package_ids)
    for pkg_id, score in scored:
        pkg = await db.get(NotePackage, pkg_id)
        if pkg:
            pkg.ranking_score = score
    await db.commit()
    return scored
