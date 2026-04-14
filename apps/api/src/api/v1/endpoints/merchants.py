from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.core.tenant import resolve_merchant_id
from src.schemas import (
    MerchantCreate,
    MerchantResponse,
    MerchantRulesResponse,
    MerchantRulesUpdate,
    MerchantUpdate,
    ProductListResponse,
    ProductResponse,
)
from src.services import merchant_service, product_service

router = APIRouter()


@router.post(
    "",
    response_model=MerchantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_merchant(
    body: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Create a new merchant."""
    merchant = await merchant_service.create_merchant(db, body)
    return merchant


@router.get("/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get merchant by ID."""
    merchant = await merchant_service.get_merchant(db, merchant_id)
    if merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant


@router.patch("/{merchant_id}", response_model=MerchantResponse)
async def update_merchant(
    merchant_id: UUID,
    body: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Update merchant."""
    return await merchant_service.update_merchant(db, merchant_id, body)


@router.get("/{merchant_id}/rules", response_model=MerchantRulesResponse)
async def get_merchant_rules(
    merchant_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get merchant rules."""
    rules = await merchant_service.get_merchant_rules(db, merchant_id)
    if rules is None:
        raise HTTPException(status_code=404, detail="Merchant rules not found")
    return rules


@router.patch("/{merchant_id}/rules", response_model=MerchantRulesResponse)
async def update_merchant_rules(
    merchant_id: UUID,
    body: MerchantRulesUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Update merchant rules."""
    return await merchant_service.update_merchant_rules(db, merchant_id, body)


@router.get("/{merchant_id}/products", response_model=ProductListResponse)
async def list_merchant_products(
    merchant_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """List all products for a merchant."""
    mid = resolve_merchant_id(merchant_id, token)
    items, total = await product_service.list_products(db, mid, limit, offset)
    counts = await product_service.count_active_assets_for_product_ids(db, mid, [p.id for p in items])
    out = [
        ProductResponse.model_validate(p).model_copy(update={"active_asset_count": counts.get(p.id, 0)}) for p in items
    ]
    return ProductListResponse(items=out, total=total, limit=limit, offset=offset)
