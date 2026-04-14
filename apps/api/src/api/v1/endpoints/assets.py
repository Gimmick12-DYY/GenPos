import hashlib
import io
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.core.storage import storage
from src.core.tenant import merchant_id_from_token, resolve_merchant_id
from src.schemas import (
    AssetListResponse,
    AssetPackCreate,
    AssetPackListResponse,
    AssetPackResponse,
    AssetPatch,
    AssetRejectRequest,
    AssetResponse,
)
from src.services import asset_service
from src.services.image_upload_normalize import normalize_image_upload

router = APIRouter()


@router.post(
    "",
    response_model=AssetPackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_asset_pack(
    body: AssetPackCreate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Create a new asset pack (draft)."""
    mid = resolve_merchant_id(body.merchant_id, token)
    return await asset_service.create_asset_pack(db, mid, body)


@router.get("", response_model=AssetPackListResponse)
async def list_asset_packs(
    merchant_id: UUID = Depends(merchant_id_from_token),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by pack status",
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List asset packs for the authenticated merchant."""
    items, total = await asset_service.list_asset_packs(
        db,
        merchant_id,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )
    return AssetPackListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{pack_id}", response_model=AssetPackResponse)
async def get_asset_pack(
    pack_id: UUID,
    merchant_id: UUID = Depends(merchant_id_from_token),
    db: AsyncSession = Depends(get_db),
):
    """Get asset pack by ID (tenant-scoped)."""
    return await asset_service.get_pack_for_merchant(db, pack_id, merchant_id)


def _image_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) using Pillow, falling back to (0, 0)."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(data))
        return img.size
    except Exception:
        return 0, 0


@router.post(
    "/{pack_id}/submit",
    response_model=AssetPackResponse,
)
async def submit_asset_pack(
    pack_id: UUID,
    merchant_id: UUID = Depends(merchant_id_from_token),
    db: AsyncSession = Depends(get_db),
):
    """Move pack from draft to pending_review (requires ≥1 approved packshot)."""
    return await asset_service.submit_asset_pack_for_review(db, merchant_id, pack_id)


@router.post("/{pack_id}/activate", response_model=AssetPackResponse)
async def activate_asset_pack(
    pack_id: UUID,
    merchant_id: UUID = Depends(merchant_id_from_token),
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Activate pack from pending_review (archives prior active pack for same quarter)."""
    sub = token.get("sub")
    actor = str(sub) if sub is not None else None
    return await asset_service.activate_asset_pack(
        db, merchant_id, pack_id, actor_sub=actor
    )


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
    merchant_id = resolve_merchant_id(None, token_payload)
    raw = await file.read()
    normalized = normalize_image_upload(raw, asset_type)
    if normalized:
        contents, content_type, width, height = normalized
        ext = "png" if "png" in content_type else "jpg"
        upload_name = f"upload.{ext}"
    else:
        contents = raw
        content_type = file.content_type or "application/octet-stream"
        width, height = _image_dimensions(contents)
        upload_name = file.filename or "upload.bin"

    checksum = hashlib.sha256(contents).hexdigest()

    file_url = await storage.upload_file(
        file_content=contents,
        content_type=content_type,
        merchant_id=str(merchant_id),
        asset_pack_id=str(pack_id),
        original_filename=upload_name,
    )

    return await asset_service.add_asset_to_pack(
        db,
        merchant_id=merchant_id,
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
    merchant_id: UUID = Depends(merchant_id_from_token),
    db: AsyncSession = Depends(get_db),
):
    """List assets in a pack."""
    await asset_service.get_pack_for_merchant(db, pack_id, merchant_id)
    items, total = await asset_service.list_assets(db, pack_id, limit, offset)
    return AssetListResponse(items=items, total=total, limit=limit, offset=offset)


@router.patch("/{pack_id}/assets/{asset_id}", response_model=AssetResponse)
async def patch_pack_asset(
    pack_id: UUID,
    asset_id: UUID,
    body: AssetPatch,
    merchant_id: UUID = Depends(merchant_id_from_token),
    db: AsyncSession = Depends(get_db),
):
    """Tag asset type / product while pack is draft."""
    return await asset_service.patch_asset(
        db, merchant_id, pack_id, asset_id, body
    )


@router.post("/{pack_id}/assets/{asset_id}/approve", response_model=AssetResponse)
async def approve_pack_asset(
    pack_id: UUID,
    asset_id: UUID,
    merchant_id: UUID = Depends(merchant_id_from_token),
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending asset (BL-304; RBAC roles deferred)."""
    sub = token.get("sub")
    actor = str(sub) if sub is not None else None
    return await asset_service.approve_asset(
        db, merchant_id, pack_id, asset_id, actor
    )


@router.post("/{pack_id}/assets/{asset_id}/reject", response_model=AssetResponse)
async def reject_pack_asset(
    pack_id: UUID,
    asset_id: UUID,
    body: AssetRejectRequest,
    merchant_id: UUID = Depends(merchant_id_from_token),
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending asset with optional reason."""
    sub = token.get("sub")
    actor = str(sub) if sub is not None else None
    return await asset_service.reject_asset(
        db, merchant_id, pack_id, asset_id, body.reason, actor
    )
