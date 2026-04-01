"""
BL-203: Fatigue detection. Compares recent 7-day engagement vs 30-day baseline
per product per dimension (style_family, objective) to detect declining patterns.
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import NotePackage, PerformanceMetrics, Product

# Configurable threshold: fatigue when recent engagement < this ratio of baseline
FATIGUE_THRESHOLD = 0.7  # 0.7 = 30% decline triggers warning


async def get_product_fatigue(
    db: AsyncSession,
    product_id: UUID,
) -> dict:
    """
    Compute fatigue scores per dimension (style_family, objective) for a product.
    Returns dimensions where recent 7-day engagement has declined vs 30-day baseline.
    """
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    now = date.today()
    window_7_end = now
    window_7_start = now - timedelta(days=7)
    window_30_start = now - timedelta(days=30)

    # Aggregate metrics by (style_family, date) and (objective, date) for this product's packages
    # We'll do two passes: 7-day and 30-day, grouped by dimension value

    dimensions: list[dict] = []

    for dimension_col in ("style_family", "objective"):
        col = getattr(NotePackage, dimension_col)
        # Use COALESCE so nulls become a group
        dim_expr = func.coalesce(col, "")

        # 7-day: sum impressions, clicks, saves per dimension value
        stmt_7 = (
            select(
                dim_expr.label("dim_value"),
                func.coalesce(func.sum(PerformanceMetrics.impressions), 0).label("impressions"),
                func.coalesce(func.sum(PerformanceMetrics.clicks), 0).label("clicks"),
                func.coalesce(func.sum(PerformanceMetrics.saves), 0).label("saves"),
            )
            .select_from(PerformanceMetrics)
            .join(NotePackage, PerformanceMetrics.note_package_id == NotePackage.id)
            .where(
                NotePackage.product_id == product_id,
                PerformanceMetrics.date >= window_7_start,
                PerformanceMetrics.date <= window_7_end,
            )
            .group_by(dim_expr)
        )
        rows_7 = (await db.execute(stmt_7)).all()

        # 30-day baseline
        stmt_30 = (
            select(
                dim_expr.label("dim_value"),
                func.coalesce(func.sum(PerformanceMetrics.impressions), 0).label("impressions"),
                func.coalesce(func.sum(PerformanceMetrics.clicks), 0).label("clicks"),
                func.coalesce(func.sum(PerformanceMetrics.saves), 0).label("saves"),
            )
            .select_from(PerformanceMetrics)
            .join(NotePackage, PerformanceMetrics.note_package_id == NotePackage.id)
            .where(
                NotePackage.product_id == product_id,
                PerformanceMetrics.date >= window_30_start,
                PerformanceMetrics.date <= window_7_end,
            )
            .group_by(dim_expr)
        )
        rows_30 = {(r.dim_value or ""): r for r in (await db.execute(stmt_30)).all()}

        for r in rows_7:
            dim_value = r.dim_value or ""
            imp_7 = int(r.impressions or 0)
            clicks_7 = int(r.clicks or 0)
            saves_7 = int(r.saves or 0)
            base = rows_30.get(dim_value)
            imp_30 = int(base.impressions or 0) if base else 0
            clicks_30 = int(base.clicks or 0) if base else 0
            saves_30 = int(base.saves or 0) if base else 0

            if imp_30 == 0:
                fatigue_score = 0.0
                recommendation = "无历史数据，无法计算疲劳度"
            else:
                ctr_7 = clicks_7 / imp_7 if imp_7 else 0
                ctr_30 = clicks_30 / imp_30
                save_rate_7 = saves_7 / imp_7 if imp_7 else 0
                save_rate_30 = saves_30 / imp_30
                # Fatigue: 1 when recent is 0, 0 when recent >= baseline
                ratio_ctr = ctr_30 and (ctr_7 / ctr_30)
                ratio_save = save_rate_30 and (save_rate_7 / save_rate_30)
                ratio = min(ratio_ctr, ratio_save) if (ratio_ctr and ratio_save) else (ratio_ctr or ratio_save or 0)
                fatigue_score = max(0.0, 1.0 - ratio)
                if fatigue_score >= FATIGUE_THRESHOLD:
                    recommendation = f"建议减少使用「{dim_value}」，近期互动率较30日基线下降明显"
                else:
                    recommendation = "当前表现正常"

            dimensions.append({
                "dimension": dimension_col,
                "value": dim_value or "(未设置)",
                "fatigue_score": round(fatigue_score, 3),
                "recent_impressions": imp_7,
                "baseline_impressions": imp_30,
                "recommendation": recommendation,
            })

    return {
        "product_id": str(product_id),
        "dimensions": dimensions,
        "threshold": FATIGUE_THRESHOLD,
    }


async def fatigue_flags_for_packages(
    db: AsyncSession,
    packages: list,
) -> dict:
    """
    Map note_package_id -> {"fatigue_warning": bool, "fatigue_hints": list[str]}.
    Uses per-product fatigue (cached by product_id) and matches style_family / objective.
    """
    if not packages:
        return {}

    cache: dict = {}
    product_ids = {p.product_id for p in packages}
    for pid in product_ids:
        try:
            cache[pid] = await get_product_fatigue(db, pid)
        except HTTPException:
            cache[pid] = {"dimensions": [], "threshold": FATIGUE_THRESHOLD}

    out: dict = {}
    for pkg in packages:
        data = cache.get(pkg.product_id) or {"dimensions": []}
        hints: list[str] = []
        warn = False
        for d in data.get("dimensions", []):
            if float(d.get("fatigue_score", 0)) < FATIGUE_THRESHOLD:
                continue
            dim = d.get("dimension")
            raw = d.get("value") or ""
            if raw == "(未设置)":
                raw = ""
            rec = (d.get("recommendation") or "").strip()
            if dim == "style_family":
                pkg_val = (pkg.style_family or "").strip()
                if pkg_val == raw.strip():
                    warn = True
                    if rec:
                        hints.append(rec)
            elif dim == "objective":
                pkg_val = (pkg.objective or "").strip()
                if pkg_val == raw.strip():
                    warn = True
                    if rec:
                        hints.append(rec)
        out[pkg.id] = {
            "fatigue_warning": warn,
            "fatigue_hints": hints[:4],
        }
    return out
