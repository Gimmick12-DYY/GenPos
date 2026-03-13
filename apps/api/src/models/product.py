from __future__ import annotations

import uuid as _uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"

    merchant_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(16), default="active", nullable=False, index=True
    )
    primary_objective: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="products")
    note_packages: Mapped[list[NotePackage]] = relationship(
        "NotePackage", back_populates="product", cascade="all, delete-orphan"
    )
    assets: Mapped[list[Asset]] = relationship(
        "Asset", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product {self.name!r} id={self.id}>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .merchant import Merchant
    from .note_package import NotePackage
    from .asset import Asset
