"""Product-scoped asset listing and tenant isolation."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Asset, AssetPack, Merchant, Product
from src.services import asset_service


async def _merchant(db: AsyncSession) -> Merchant:
    m = Merchant(
        name="Test Merchant",
        industry="retail",
        xhs_account_type="brand",
    )
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m


async def _pack(
    db: AsyncSession,
    merchant_id,
    *,
    quarter_label: str = "2026_Q1",
    status: str = "draft",
) -> AssetPack:
    p = AssetPack(
        merchant_id=merchant_id,
        quarter_label=quarter_label,
        status=status,
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@pytest.mark.asyncio
async def test_list_assets_by_product_filters_pack_status(
    db_session: AsyncSession,
) -> None:
    m = await _merchant(db_session)
    prod = Product(merchant_id=m.id, name="P1", category="c")
    db_session.add(prod)
    await db_session.commit()
    await db_session.refresh(prod)

    pack_draft = await _pack(db_session, m.id, quarter_label="Q_D", status="draft")
    pack_active = await _pack(db_session, m.id, quarter_label="Q_A", status="active")

    a1 = Asset(
        asset_pack_id=pack_draft.id,
        product_id=prod.id,
        type="packshot",
        storage_url="http://a",
        approval_status="pending",
        checksum="1",
    )
    a2 = Asset(
        asset_pack_id=pack_active.id,
        product_id=prod.id,
        type="logo",
        storage_url="http://b",
        approval_status="approved",
        checksum="2",
    )
    db_session.add_all([a1, a2])
    await db_session.commit()

    active_only, t1 = await asset_service.list_assets_by_product(
        db_session,
        m.id,
        prod.id,
        pack_status="active",
        limit=20,
        offset=0,
    )
    assert t1 == 1
    assert active_only[0].id == a2.id

    all_rows, t2 = await asset_service.list_assets_by_product(
        db_session,
        m.id,
        prod.id,
        pack_status=None,
        limit=20,
        offset=0,
    )
    assert t2 == 2


@pytest.mark.asyncio
async def test_list_assets_by_product_wrong_merchant(
    db_session: AsyncSession,
) -> None:
    m1 = await _merchant(db_session)
    m2 = await _merchant(db_session)
    prod = Product(merchant_id=m1.id, name="P", category="c")
    db_session.add(prod)
    await db_session.commit()
    await db_session.refresh(prod)

    with pytest.raises(HTTPException) as exc:
        await asset_service.list_assets_by_product(
            db_session,
            m2.id,
            prod.id,
            pack_status=None,
            limit=10,
            offset=0,
        )
    assert exc.value.status_code == 404
