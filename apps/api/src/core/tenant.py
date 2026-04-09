"""
Single-tenant deployment helpers: merchant scope defaults to JWT `sub`.

When `merchant_id` is omitted on queries or request bodies, it resolves to the
authenticated merchant. If provided, it must match `sub` (403 otherwise).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, Query, status

from src.core.security import verify_token


def resolve_merchant_id(merchant_id: UUID | None, token: dict) -> UUID:
    sub = token.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    sub_uuid = UUID(str(sub))
    if merchant_id is None:
        return sub_uuid
    if str(merchant_id) != str(sub_uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another merchant's data",
        )
    return merchant_id


def parse_optional_merchant_id_str(raw: str | None, token: dict) -> UUID:
    """For JSON bodies that carry merchant_id as string (chat)."""
    if raw is None or not str(raw).strip():
        return resolve_merchant_id(None, token)
    try:
        return resolve_merchant_id(UUID(str(raw).strip()), token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid merchant_id",
        ) from e


async def merchant_id_from_token(
    merchant_id: UUID | None = Query(
        None,
        description="Optional; defaults to JWT sub (single-merchant: omit).",
    ),
    token: dict = Depends(verify_token),
) -> UUID:
    return resolve_merchant_id(merchant_id, token)
