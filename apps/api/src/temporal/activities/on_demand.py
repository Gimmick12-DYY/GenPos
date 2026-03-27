from __future__ import annotations

from uuid import UUID

from temporalio import activity

from src.core.database import async_session_factory
from src.services.generation_service import run_on_demand_generation


@activity.defn(name="run_on_demand_pipeline_activity")
async def run_on_demand_pipeline_activity(payload: dict) -> dict:
    """Execute the full on-demand pipeline inside a Temporal activity (own DB session)."""
    job_id = UUID(payload["job_id"])
    merchant_id = UUID(payload["merchant_id"])
    product_id = UUID(payload["product_id"]) if payload.get("product_id") else None

    async with async_session_factory() as db:
        return await run_on_demand_generation(
            db,
            merchant_id=merchant_id,
            product_id=product_id,
            user_message=payload.get("user_message") or "",
            objective=payload.get("objective") or "seeding",
            persona=payload.get("persona") or "",
            style_preference=payload.get("style_preference") or "",
            special_instructions=payload.get("special_instructions") or "",
            is_juguang=bool(payload.get("is_juguang", False)),
            is_pugongying=bool(payload.get("is_pugongying", False)),
            job_id=job_id,
        )
