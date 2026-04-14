"""Load merchant products for LLM context (chat + Founder Copilot)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.product_catalog_prompt import format_catalog_text_for_prompt
from src.models import Product


async def load_active_product_catalog(db: AsyncSession, merchant_id: UUID) -> list[dict]:
    """Return active products as plain dicts for prompts and AgentContext."""
    stmt = (
        select(Product)
        .where(
            Product.merchant_id == merchant_id,
            Product.status == "active",
        )
        .order_by(Product.name)
    )
    rows = list((await db.execute(stmt)).scalars().all())
    out: list[dict] = []
    for p in rows:
        desc = (p.description or "").strip()
        if len(desc) > 500:
            desc = desc[:500] + "…"
        out.append(
            {
                "id": str(p.id),
                "name": p.name,
                "category": p.category,
                "primary_objective": (p.primary_objective or "").strip(),
                "description": desc,
            }
        )
    return out


__all__ = ["load_active_product_catalog", "format_catalog_text_for_prompt"]
