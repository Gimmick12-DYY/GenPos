"""Dev-only auth for local and demo use. Replace with proper login (BL-007) in production."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import create_access_token
from src.models import Merchant, MerchantRules

router = APIRouter()


class DevTokenRequest(BaseModel):
    merchant_id: str | None = None


class DevTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    merchant_id: str


class BootstrapRequest(BaseModel):
    """Optional fields; defaults used when not provided. Only used when no merchants exist."""

    name: str = Field(default="意睡眠 Easysleep", min_length=1, max_length=255)
    industry: str = Field(default="家居", max_length=128)  # 床垫
    xhs_account_type: str = Field(default="professional", max_length=64)
    uses_juguang: bool = False
    uses_pugongying: bool = False
    language: str = Field(default="zh-CN", max_length=10)
    timezone: str = Field(default="Asia/Shanghai", max_length=64)


class BootstrapResponse(BaseModel):
    merchant_id: str
    message: str


@router.post("/dev-token", response_model=DevTokenResponse)
async def get_dev_token(
    body: DevTokenRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Issue a JWT for development. No auth required.
    If merchant_id is omitted, uses the first merchant in the DB.
    Only for use when DEBUG=true or in local development.
    """
    if body and body.merchant_id:
        try:
            merchant_uuid = UUID(body.merchant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid merchant_id format",
            )
        merchant = await db.get(Merchant, merchant_uuid)
        if merchant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Merchant not found",
            )
    else:
        row = (await db.execute(select(Merchant).limit(1))).scalar_one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No merchant in database. Create a merchant first.",
            )
        merchant = row
        merchant_uuid = merchant.id

    token = create_access_token(data={"sub": str(merchant_uuid), "merchant_id": str(merchant_uuid)})
    from src.core.config import settings

    return DevTokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
        merchant_id=str(merchant_uuid),
    )


@router.post("/bootstrap", response_model=BootstrapResponse)
async def bootstrap_first_merchant(
    body: BootstrapRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create the first merchant when the database has none. No auth required.
    Call once after deploy to unblock dev-token and the app.
    If any merchant already exists, returns 400.
    """
    count = (await db.execute(select(func.count()).select_from(Merchant))).scalar_one()
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bootstrap only allowed when no merchants exist. Merchant table is not empty.",
        )

    data = (body or BootstrapRequest()).model_dump()
    merchant = Merchant(**data)
    db.add(merchant)
    await db.flush()

    rules = MerchantRules(
        merchant_id=merchant.id,
        compliance_level="standard",
        review_mode="all",
    )
    db.add(rules)
    await db.commit()
    await db.refresh(merchant)

    return BootstrapResponse(
        merchant_id=str(merchant.id),
        message="First merchant created. You can now use POST /auth/dev-token to get a token.",
    )
