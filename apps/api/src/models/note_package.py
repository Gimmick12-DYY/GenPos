from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class NotePackage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "note_packages"

    merchant_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_pack_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_packs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    generation_job_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    objective: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    persona: Mapped[str | None] = mapped_column(String(128), nullable=True)
    style_family: Mapped[str | None] = mapped_column(String(64), nullable=True)
    compliance_status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False, index=True)
    ranking_score: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True, index=True)
    review_status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)

    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="note_packages")
    product: Mapped[Product] = relationship("Product", back_populates="note_packages")
    asset_pack: Mapped[AssetPack | None] = relationship("AssetPack", back_populates="note_packages")
    generation_job: Mapped[GenerationJob | None] = relationship("GenerationJob", back_populates="note_packages")
    text_assets: Mapped[list[TextAsset]] = relationship(
        "TextAsset", back_populates="note_package", cascade="all, delete-orphan"
    )
    image_assets: Mapped[list[ImageAsset]] = relationship(
        "ImageAsset", back_populates="note_package", cascade="all, delete-orphan"
    )
    briefs: Mapped[list[Brief]] = relationship("Brief", back_populates="note_package", cascade="all, delete-orphan")
    performance_metrics: Mapped[list[PerformanceMetrics]] = relationship(
        "PerformanceMetrics", back_populates="note_package", cascade="all, delete-orphan"
    )
    review_events: Mapped[list[ReviewEvent]] = relationship(
        "ReviewEvent", back_populates="note_package", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<NotePackage objective={self.objective!r} id={self.id}>"


class TextAsset(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "text_assets"

    note_package_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("note_packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="zh-CN", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    note_package: Mapped[NotePackage] = relationship("NotePackage", back_populates="text_assets")

    def __repr__(self) -> str:
        return f"<TextAsset role={self.asset_role!r} id={self.id}>"


class ImageAsset(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "image_assets"

    note_package_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("note_packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_role: Mapped[str] = mapped_column(String(32), nullable=False)
    source_asset_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    derived_from: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    note_package: Mapped[NotePackage] = relationship("NotePackage", back_populates="image_assets")
    source_asset: Mapped[Asset | None] = relationship("Asset", back_populates="image_assets")

    def __repr__(self) -> str:
        return f"<ImageAsset role={self.asset_role!r} id={self.id}>"


class Brief(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "briefs"

    note_package_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("note_packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brief_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    note_package: Mapped[NotePackage] = relationship("NotePackage", back_populates="briefs")

    def __repr__(self) -> str:
        return f"<Brief type={self.brief_type!r} id={self.id}>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analytics import PerformanceMetrics, ReviewEvent
    from .asset import Asset, AssetPack
    from .generation import GenerationJob
    from .merchant import Merchant
    from .product import Product
