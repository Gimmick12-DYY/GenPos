from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.core.tenant import resolve_merchant_id
from src.schemas import (
    AssetListResponse,
    ProductCreate,
    ProductFatigueResponse,
    ProductResponse,
    ProductUpdate,
)
from src.services import asset_service, fatigue_service, product_service

router = APIRouter()


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Create a new product."""
    mid = resolve_merchant_id(body.merchant_id, token)
    body_eff = body.model_copy(update={"merchant_id": mid})
    return await product_service.create_product(db, body_eff)


@router.get("/{product_id}/fatigue", response_model=ProductFatigueResponse)
async def get_product_fatigue(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Get fatigue scores per dimension (style_family, objective) for a product."""
    mid = resolve_merchant_id(None, token)
    await product_service.require_product_for_merchant(db, product_id, mid)
    return await fatigue_service.get_product_fatigue(db, product_id)


@router.get("/{product_id}/assets", response_model=AssetListResponse)
async def list_product_assets(
    product_id: UUID,
    pack_status: str | None = Query(
        None,
        alias="pack_status",
        description="Optional filter: pack status (e.g. active).",
    ),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """List assets linked to this product (BL-306 gallery data)."""
    mid = resolve_merchant_id(None, token)
    items, total = await asset_service.list_assets_by_product(
        db,
        mid,
        product_id,
        pack_status=pack_status,
        limit=limit,
        offset=offset,
    )
    return AssetListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Get product by ID."""
    mid = resolve_merchant_id(None, token)
    return await product_service.require_product_for_merchant(db, product_id, mid)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Update product."""
    mid = resolve_merchant_id(None, token)
    return await product_service.update_product(db, product_id, body, merchant_id=mid)
