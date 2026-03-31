from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas.note_package import TextAssetPatch, TextAssetResponse
from src.services import note_package_service

router = APIRouter()


def _merchant_uuid(token: dict) -> UUID:
    try:
        return UUID(str(token["sub"]))
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


@router.patch("/{text_asset_id}", response_model=TextAssetResponse)
async def patch_text_asset(
    text_asset_id: UUID,
    body: TextAssetPatch,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """BL-110: inline edit of generated text (titles, body, hashtags, …)."""
    merchant_id = _merchant_uuid(token)
    ta = await note_package_service.patch_text_asset(
        db, text_asset_id, merchant_id, body
    )
    return ta
