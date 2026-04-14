from __future__ import annotations

import uuid as _uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .merchant import Merchant
    from .note_package import ImageAsset, NotePackage
    from .product import Product


class AssetPack(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "asset_packs"

    merchant_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quarter_label: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="draft", nullable=False, index=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="asset_packs")
    assets: Mapped[list[Asset]] = relationship("Asset", back_populates="asset_pack", cascade="all, delete-orphan")
    note_packages: Mapped[list[NotePackage]] = relationship("NotePackage", back_populates="asset_pack")

    def __repr__(self) -> str:
        return f"<AssetPack {self.quarter_label!r} id={self.id}>"


class Asset(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "assets"

    asset_pack_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_packs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    asset_pack: Mapped[AssetPack] = relationship("AssetPack", back_populates="assets")
    product: Mapped[Product | None] = relationship("Product", back_populates="assets")
    image_assets: Mapped[list[ImageAsset]] = relationship("ImageAsset", back_populates="source_asset")

    def __repr__(self) -> str:
        return f"<Asset type={self.type!r} id={self.id}>"
