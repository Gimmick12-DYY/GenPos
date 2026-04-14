"""BL-304 bulk approve/reject."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Asset
from src.services import asset_service
from tests.test_product_assets import _merchant, _pack


async def _pending_asset(db: AsyncSession, pack_id, n: int = 1) -> list:
    out = []
    for i in range(n):
        a = Asset(
            asset_pack_id=pack_id,
            product_id=None,
            type="packshot",
            storage_url=f"https://x/{i}",
            approval_status="pending",
            checksum=f"c{i}",
        )
        db.add(a)
        out.append(a)
    await db.commit()
    for a in out:
        await db.refresh(a)
    return out


@pytest.mark.asyncio
async def test_bulk_approve_all_pending(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    assets = await _pending_asset(db_session, pack.id, 3)
    ids = [a.id for a in assets]
    out = await asset_service.bulk_approve_assets(db_session, m.id, pack.id, ids, actor_sub="u1")
    assert len(out) == 3
    for a in out:
        assert a.approval_status == "approved"


@pytest.mark.asyncio
async def test_bulk_approve_rejects_mixed_status(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    a1, a2 = await _pending_asset(db_session, pack.id, 2)
    a1.approval_status = "approved"
    await db_session.commit()
    with pytest.raises(HTTPException) as exc:
        await asset_service.bulk_approve_assets(db_session, m.id, pack.id, [a1.id, a2.id], actor_sub=None)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_bulk_reject_shared_reason(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    assets = await _pending_asset(db_session, pack.id, 2)
    ids = [a.id for a in assets]
    out = await asset_service.bulk_reject_assets(db_session, m.id, pack.id, ids, "blur", actor_sub="u2")
    assert len(out) == 2
    for a in out:
        assert a.approval_status == "rejected"
        assert a.metadata_json.get("reject_reason") == "blur"
