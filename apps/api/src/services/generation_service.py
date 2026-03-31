from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.orchestrator import orchestrator
from src.models import Product
from src.services import ranking_service, review_service


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
    job_id: UUID | None = None,
    session_id: UUID | None = None,
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
        job_id=job_id,
        session_id=session_id,
    )


async def run_daily_batch(
    db: AsyncSession,
    merchant_id: UUID,
    packages_per_product: int = 1,
    max_concurrent: int = 3,
) -> dict:
    """
    Run daily generation for all active products of a merchant.
    Uses semaphore to limit concurrent product pipelines.
    """
    stmt = select(Product).where(
        Product.merchant_id == merchant_id,
        Product.status == "active",
    )
    result = await db.execute(stmt)
    products = list(result.scalars().all())
    if not products:
        return {
            "merchant_id": str(merchant_id),
            "products_processed": 0,
            "packages_created": 0,
            "failures": 0,
            "details": [],
        }

    details: list[dict] = []
    packages_created = 0
    failures = 0

    # Run products sequentially to avoid DB conflicts; each product can have multiple packages
    for product in products:
        for _ in range(packages_per_product):
            out = await orchestrator.run_daily_product(
                db, merchant_id=merchant_id, product_id=product.id
            )
            if out.get("note_package_id"):
                packages_created += 1
                details.append({"product_id": str(product.id), "note_package_id": out["note_package_id"]})
            else:
                failures += 1
                details.append({"product_id": str(product.id), "error": out.get("error", "failed")})

    new_package_ids: list[UUID] = []
    for row in details:
        nid = row.get("note_package_id")
        if nid:
            new_package_ids.append(UUID(str(nid)))
    if new_package_ids:
        await ranking_service.update_ranking_scores(db, new_package_ids)

    # Apply auto-approve for merchants with review_mode=auto (uses composite ranking_score)
    auto_approved = await review_service.process_auto_approve(db, merchant_id)

    return {
        "merchant_id": str(merchant_id),
        "products_processed": len(products),
        "packages_created": packages_created,
        "failures": failures,
        "auto_approved": auto_approved,
        "details": details,
    }
