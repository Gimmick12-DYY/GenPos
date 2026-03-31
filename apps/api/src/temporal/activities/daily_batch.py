from __future__ import annotations

from uuid import UUID

from temporalio import activity

from src.core.database import async_session_factory
from src.services.generation_service import run_daily_batch


@activity.defn(name="run_daily_batch_activity")
async def run_daily_batch_activity(payload: dict) -> dict:
    """Run daily_auto generation for all active products of one merchant (BL-201)."""
    merchant_id = UUID(payload["merchant_id"])
    packages = int(payload.get("packages_per_product") or 3)
    async with async_session_factory() as db:
        return await run_daily_batch(
            db,
            merchant_id=merchant_id,
            packages_per_product=packages,
            max_concurrent=1,
        )
