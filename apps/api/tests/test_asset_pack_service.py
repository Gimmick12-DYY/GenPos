"""Regression tests for asset pack lifecycle rules (BL-301 / BL-304 / BL-305)."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Asset, AssetPack, Merchant, Product
from src.schemas.asset import AssetPatch
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
    effective_from: date | None = None,
    effective_to: date | None = None,
) -> AssetPack:
    p = AssetPack(
        merchant_id=merchant_id,
        quarter_label=quarter_label,
        status=status,
        effective_from=effective_from,
        effective_to=effective_to,
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


async def _packshot(
    db: AsyncSession,
    pack_id,
    *,
    approval_status: str = "pending",
) -> Asset:
    a = Asset(
        asset_pack_id=pack_id,
        type="packshot",
        storage_url="https://example.com/p.jpg",
        width=100,
        height=100,
        checksum="sha",
        approval_status=approval_status,
    )
    db.add(a)
    await db.commit()
    await db.refresh(a)
    return a


@pytest.mark.asyncio
async def test_submit_requires_approved_packshot(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    await _packshot(db_session, pack.id, approval_status="pending")
    with pytest.raises(HTTPException) as exc:
        await asset_service.submit_asset_pack_for_review(db_session, m.id, pack.id)
    assert exc.value.status_code == 400
    assert "packshot" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_submit_draft_to_pending_review(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    await _packshot(db_session, pack.id, approval_status="approved")
    out = await asset_service.submit_asset_pack_for_review(db_session, m.id, pack.id)
    assert out.status == "pending_review"


@pytest.mark.asyncio
async def test_submit_only_from_draft(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id, status="pending_review")
    await _packshot(db_session, pack.id, approval_status="approved")
    with pytest.raises(HTTPException) as exc:
        await asset_service.submit_asset_pack_for_review(db_session, m.id, pack.id)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_activate_only_from_pending_review(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id, status="draft")
    await _packshot(db_session, pack.id, approval_status="approved")
    with pytest.raises(HTTPException) as exc:
        await asset_service.activate_asset_pack(db_session, m.id, pack.id)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_activate_records_activation_audit(
    db_session: AsyncSession,
) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    await _packshot(db_session, pack.id, approval_status="approved")
    await asset_service.submit_asset_pack_for_review(db_session, m.id, pack.id)
    out = await asset_service.activate_asset_pack(db_session, m.id, pack.id, actor_sub="actor-1")
    assert out.metadata_json is not None
    audit = out.metadata_json.get("activation_audit")
    assert isinstance(audit, list) and len(audit) == 1
    assert audit[0].get("actor_sub") == "actor-1"
    assert audit[0].get("at")


@pytest.mark.asyncio
async def test_activate_archives_prior_same_quarter(
    db_session: AsyncSession,
) -> None:
    m = await _merchant(db_session)
    q = "2026_Q1"
    first = await _pack(db_session, m.id, quarter_label=q)
    await _packshot(db_session, first.id, approval_status="approved")
    await asset_service.submit_asset_pack_for_review(db_session, m.id, first.id)
    await asset_service.activate_asset_pack(db_session, m.id, first.id)
    await db_session.refresh(first)
    assert first.status == "active"

    second = await _pack(db_session, m.id, quarter_label=q)
    await _packshot(db_session, second.id, approval_status="approved")
    await asset_service.submit_asset_pack_for_review(db_session, m.id, second.id)
    await asset_service.activate_asset_pack(db_session, m.id, second.id)

    await db_session.refresh(first)
    await db_session.refresh(second)
    assert first.status == "archived"
    assert second.status == "active"


@pytest.mark.asyncio
async def test_activate_rejects_overlapping_effective_range(
    db_session: AsyncSession,
) -> None:
    m = await _merchant(db_session)
    active = await _pack(
        db_session,
        m.id,
        quarter_label="2026_Q1",
        status="active",
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 3, 31),
    )
    await _packshot(db_session, active.id, approval_status="approved")

    pending = await _pack(
        db_session,
        m.id,
        quarter_label="2026_Q2",
        status="pending_review",
        effective_from=date(2026, 3, 1),
        effective_to=date(2026, 6, 30),
    )
    await _packshot(db_session, pending.id, approval_status="approved")

    with pytest.raises(HTTPException) as exc:
        await asset_service.activate_asset_pack(db_session, m.id, pending.id)
    assert exc.value.status_code == 400
    assert "overlap" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_get_pack_for_merchant_wrong_tenant(
    db_session: AsyncSession,
) -> None:
    m1 = await _merchant(db_session)
    m2 = await _merchant(db_session)
    pack = await _pack(db_session, m1.id)
    with pytest.raises(HTTPException) as exc:
        await asset_service.get_pack_for_merchant(db_session, pack.id, m2.id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_patch_asset_conflict_when_approved(
    db_session: AsyncSession,
) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    shot = await _packshot(db_session, pack.id, approval_status="approved")
    with pytest.raises(HTTPException) as exc:
        await asset_service.patch_asset(
            db_session,
            m.id,
            pack.id,
            shot.id,
            AssetPatch(type="logo"),
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_add_asset_blocked_when_pack_not_draft(
    db_session: AsyncSession,
) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    await _packshot(db_session, pack.id, approval_status="approved")
    await asset_service.submit_asset_pack_for_review(db_session, m.id, pack.id)
    with pytest.raises(HTTPException) as exc:
        await asset_service.add_asset_to_pack(
            db_session,
            m.id,
            pack.id,
            file_url="u",
            asset_type="packshot",
            width=1,
            height=1,
            product_id=None,
            checksum="x",
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_patch_rejects_foreign_product(db_session: AsyncSession) -> None:
    m1 = await _merchant(db_session)
    m2 = await _merchant(db_session)
    pack = await _pack(db_session, m1.id)
    shot = await _packshot(db_session, pack.id, approval_status="pending")
    prod = Product(
        merchant_id=m2.id,
        name="Other",
        category="c",
    )
    db_session.add(prod)
    await db_session.commit()
    await db_session.refresh(prod)

    with pytest.raises(HTTPException) as exc:
        await asset_service.patch_asset(
            db_session,
            m1.id,
            pack.id,
            shot.id,
            AssetPatch(product_id=prod.id),
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_list_asset_packs_status_filter(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    await _pack(db_session, m.id, quarter_label="A", status="draft")
    await _pack(db_session, m.id, quarter_label="B", status="active")
    drafts, total_d = await asset_service.list_asset_packs(db_session, m.id, status_filter="draft", limit=20, offset=0)
    assert total_d == 1
    assert drafts[0].quarter_label == "A"
    all_rows, total_all = await asset_service.list_asset_packs(db_session, m.id, status_filter=None, limit=20, offset=0)
    assert total_all == 2


@pytest.mark.asyncio
async def test_approve_and_reject_pending(db_session: AsyncSession) -> None:
    m = await _merchant(db_session)
    pack = await _pack(db_session, m.id)
    shot = await _packshot(db_session, pack.id, approval_status="pending")
    out = await asset_service.approve_asset(db_session, m.id, pack.id, shot.id, "user-1")
    assert out.approval_status == "approved"
    assert out.metadata_json and "approval_audit" in out.metadata_json

    other = await _packshot(db_session, pack.id, approval_status="pending")
    rej = await asset_service.reject_asset(db_session, m.id, pack.id, other.id, "blur", "user-1")
    assert rej.approval_status == "rejected"
    assert rej.metadata_json.get("reject_reason") == "blur"
