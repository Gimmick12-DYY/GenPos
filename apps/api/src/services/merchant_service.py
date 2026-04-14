from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Merchant, MerchantRules
from src.schemas import MerchantCreate, MerchantRulesUpdate, MerchantUpdate


async def create_merchant(db: AsyncSession, data: MerchantCreate) -> Merchant:
    merchant = Merchant(**data.model_dump())
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)
    return merchant


async def get_merchant(db: AsyncSession, merchant_id: UUID) -> Merchant | None:
    return await db.get(Merchant, merchant_id)


async def update_merchant(db: AsyncSession, merchant_id: UUID, data: MerchantUpdate) -> Merchant:
    merchant = await db.get(Merchant, merchant_id)
    if merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(merchant, field, value)

    await db.commit()
    await db.refresh(merchant)
    return merchant


async def get_merchant_rules(db: AsyncSession, merchant_id: UUID) -> MerchantRules | None:
    stmt = select(MerchantRules).where(MerchantRules.merchant_id == merchant_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_merchant_rules(db: AsyncSession, merchant_id: UUID, data: MerchantRulesUpdate) -> MerchantRules:
    merchant = await db.get(Merchant, merchant_id)
    if merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")

    stmt = select(MerchantRules).where(MerchantRules.merchant_id == merchant_id)
    result = await db.execute(stmt)
    rules = result.scalar_one_or_none()

    update_data = data.model_dump(exclude_unset=True)

    if rules is None:
        rules = MerchantRules(merchant_id=merchant_id, **update_data)
        db.add(rules)
    else:
        for field, value in update_data.items():
            setattr(rules, field, value)

    await db.commit()
    await db.refresh(rules)
    return rules
