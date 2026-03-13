from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.orchestrator import orchestrator


async def run_on_demand_generation(
    db: AsyncSession,
    merchant_id: UUID,
    product_id: UUID | None = None,
    user_message: str = "",
    objective: str = "seeding",
    persona: str = "",
    style_preference: str = "",
    special_instructions: str = "",
    is_juguang: bool = False,
    is_pugongying: bool = False,
) -> dict:
    """Run on-demand generation pipeline and return results."""
    return await orchestrator.run_on_demand(
        db=db,
        merchant_id=merchant_id,
        product_id=product_id,
        user_message=user_message,
        objective=objective,
        persona=persona,
        style_preference=style_preference,
        special_instructions=special_instructions,
        is_juguang=is_juguang,
        is_pugongying=is_pugongying,
    )
