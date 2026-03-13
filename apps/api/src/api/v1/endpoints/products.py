from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import ProductCreate, ProductFatigueResponse, ProductResponse, ProductUpdate
from src.services import fatigue_service, product_service

router = APIRouter()


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Create a new product."""
    return await product_service.create_product(db, body)


@router.get("/{product_id}/fatigue", response_model=ProductFatigueResponse)
async def get_product_fatigue(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get fatigue scores per dimension (style_family, objective) for a product."""
    return await fatigue_service.get_product_fatigue(db, product_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get product by ID."""
    product = await product_service.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Update product."""
    return await product_service.update_product(db, product_id, body)
