from __future__ import annotations

from temporalio import activity

from src.core.database import async_session_factory
from src.core.shanghai_calendar import shanghai_date_iso
from src.services import generation_service


@activity.defn(name="run_daily_run_all_activity")
async def run_daily_run_all_activity(payload: dict) -> dict:
    """
    BL-201: run sync daily batch for every merchant with active products.
    Used by Temporal schedule (no HTTP); respects skip_if_already_run per merchant.
    """
    packages = int(payload.get("packages_per_product") or 3)
    async with async_session_factory() as db:
        merchant_ids = await generation_service.list_all_merchant_ids(db)
        results: list[dict] = []
        for mid in merchant_ids:
            try:
                out = await generation_service.run_daily_batch(
                    db,
                    merchant_id=mid,
                    packages_per_product=packages,
                    max_concurrent=1,
                    force=False,
                    skip_if_already_run=True,
                )
                results.append(
                    {
                        "merchant_id": str(mid),
                        "skipped": bool(out.get("skipped")),
                        "packages_created": int(out.get("packages_created") or 0),
                        "failures": int(out.get("failures") or 0),
                        "products_processed": int(out.get("products_processed") or 0),
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "merchant_id": str(mid),
                        "error": str(exc),
                    }
                )
        return {
            "shanghai_date": shanghai_date_iso(),
            "packages_per_product": packages,
            "merchant_count": len(merchant_ids),
            "results": results,
        }
