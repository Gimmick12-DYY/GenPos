from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Product
from src.schemas import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_product(db: AsyncSession, product_id: UUID) -> Product | None:
    return await db.get(Product, product_id)


async def update_product(
    db: AsyncSession, product_id: UUID, data: ProductUpdate
) -> Product:
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


async def list_products(
    db: AsyncSession, merchant_id: UUID, limit: int, offset: int
) -> tuple[list[Product], int]:
    count_stmt = (
        select(func.count())
        .select_from(Product)
        .where(Product.merchant_id == merchant_id)
    )
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = (
        select(Product)
        .where(Product.merchant_id == merchant_id)
        .order_by(Product.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list((await db.execute(items_stmt)).scalars().all())

    return items, total
