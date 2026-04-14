from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import NotePackage


async def _load_full_package(db: AsyncSession, package_id: UUID) -> NotePackage:
    stmt = (
        select(NotePackage)
        .where(NotePackage.id == package_id)
        .options(
            selectinload(NotePackage.text_assets),
            selectinload(NotePackage.image_assets),
            selectinload(NotePackage.briefs),
            selectinload(NotePackage.product),
        )
    )
    result = await db.execute(stmt)
    pkg = result.scalar_one_or_none()
    if pkg is None:
        raise HTTPException(status_code=404, detail="Note package not found")
    return pkg


def _extract_text_map(pkg: NotePackage) -> dict[str, str]:
    return {ta.asset_role: ta.content for ta in pkg.text_assets}


def _extract_image_list(pkg: NotePackage) -> list[dict]:
    return [
        {
            "role": ia.asset_role,
            "image_url": ia.image_url,
            "derived_from": ia.derived_from,
        }
        for ia in pkg.image_assets
    ]


async def export_note_bundle(db: AsyncSession, package_id: UUID) -> dict:
    pkg = await _load_full_package(db, package_id)
    return {
        "note_package_id": str(pkg.id),
        "brief_type": "note_export",
        "product_name": pkg.product.name if pkg.product else None,
        "objective": pkg.objective,
        "persona": pkg.persona,
        "style_family": pkg.style_family,
        "text": _extract_text_map(pkg),
        "images": _extract_image_list(pkg),
        "briefs": [{"type": b.brief_type, "content": b.content_json} for b in pkg.briefs],
    }


async def export_juguang_bundle(db: AsyncSession, package_id: UUID) -> dict:
    """Assemble a 聚光-ready ad creative bundle."""
    pkg = await _load_full_package(db, package_id)
    text_map = _extract_text_map(pkg)
    return {
        "note_package_id": str(pkg.id),
        "brief_type": "juguang",
        "product_name": pkg.product.name if pkg.product else None,
        "objective": pkg.objective,
        "ad_title": text_map.get("title", ""),
        "ad_body": text_map.get("body", ""),
        "cta": text_map.get("cta", ""),
        "cover_text": text_map.get("cover_text", ""),
        "images": _extract_image_list(pkg),
        "hashtags": text_map.get("hashtag", ""),
    }


async def export_pugongying_bundle(db: AsyncSession, package_id: UUID) -> dict:
    """Assemble a 蒲公英-ready KOL brief."""
    pkg = await _load_full_package(db, package_id)
    text_map = _extract_text_map(pkg)
    return {
        "note_package_id": str(pkg.id),
        "brief_type": "pugongying",
        "product_name": pkg.product.name if pkg.product else None,
        "objective": pkg.objective,
        "persona": pkg.persona,
        "style_family": pkg.style_family,
        "brief_title": text_map.get("title", ""),
        "talking_points": text_map.get("body", ""),
        "first_comment": text_map.get("first_comment", ""),
        "hashtags": text_map.get("hashtag", ""),
        "reference_images": _extract_image_list(pkg),
    }
