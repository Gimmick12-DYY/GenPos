import hashlib
import io
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.core.storage import storage
from src.schemas import (
    AssetListResponse,
    AssetPackCreate,
    AssetPackResponse,
    AssetResponse,
)
from src.services import asset_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=AssetPackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_asset_pack(
    body: AssetPackCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Create a new asset pack."""
    return await asset_service.create_asset_pack(db, body)


@router.get("/{pack_id}", response_model=AssetPackResponse)
async def get_asset_pack(
    pack_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get asset pack by ID."""
    pack = await asset_service.get_asset_pack(db, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Asset pack not found")
    return pack


def _image_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) using Pillow, falling back to (0, 0)."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(data))
        return img.size
    except Exception:
        return 0, 0


@router.post(
    "/{pack_id}/assets",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_asset(
    pack_id: UUID,
    file: UploadFile,
    asset_type: str = Form(...),
    product_id: UUID | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    token_payload: dict = Depends(verify_token),
):
    """Upload an asset to a pack via S3-compatible storage."""
    contents = await file.read()
    checksum = hashlib.sha256(contents).hexdigest()

    width, height = _image_dimensions(contents)

    merchant_id = token_payload.get("merchant_id", "unknown")

    file_url = await storage.upload_file(
        file_content=contents,
        content_type=file.content_type or "application/octet-stream",
        merchant_id=str(merchant_id),
        asset_pack_id=str(pack_id),
        original_filename=file.filename or "upload.bin",
    )

    return await asset_service.add_asset_to_pack(
        db,
        pack_id=pack_id,
        file_url=file_url,
        asset_type=asset_type,
        width=width,
        height=height,
        product_id=product_id,
        checksum=checksum,
    )


@router.get("/{pack_id}/assets", response_model=AssetListResponse)
async def list_pack_assets(
    pack_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """List assets in a pack."""
    items, total = await asset_service.list_assets(db, pack_id, limit, offset)
    return AssetListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("/{pack_id}/activate", response_model=AssetPackResponse)
async def activate_asset_pack(
    pack_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Activate an asset pack (archives the previously active pack for the same quarter)."""
    return await asset_service.activate_asset_pack(db, pack_id)
