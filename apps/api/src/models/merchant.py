from __future__ import annotations

import uuid as _uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Merchant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "merchants"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    xhs_account_type: Mapped[str] = mapped_column(String(64), nullable=False)
    uses_juguang: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uses_pugongying: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="zh-CN", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai", nullable=False)

    rules: Mapped[MerchantRules | None] = relationship(
        "MerchantRules", back_populates="merchant", uselist=False, cascade="all, delete-orphan"
    )
    products: Mapped[list[Product]] = relationship(
        "Product", back_populates="merchant", cascade="all, delete-orphan"
    )
    asset_packs: Mapped[list[AssetPack]] = relationship(
        "AssetPack", back_populates="merchant", cascade="all, delete-orphan"
    )
    generation_jobs: Mapped[list[GenerationJob]] = relationship(
        "GenerationJob", back_populates="merchant", cascade="all, delete-orphan"
    )
    note_packages: Mapped[list[NotePackage]] = relationship(
        "NotePackage", back_populates="merchant", cascade="all, delete-orphan"
    )
    agent_teams: Mapped[list[AgentTeam]] = relationship(
        "AgentTeam", back_populates="merchant", cascade="all, delete-orphan"
    )
    policy_rules: Mapped[list[PolicyRule]] = relationship(
        "PolicyRule", back_populates="merchant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Merchant {self.name!r} id={self.id}>"


class MerchantRules(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "merchant_rules"

    merchant_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    tone_preset: Mapped[str] = mapped_column(String(64), nullable=True)
    banned_words: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    required_claims: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    banned_claims: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    compliance_level: Mapped[str] = mapped_column(
        String(16), default="standard", nullable=False
    )
    review_mode: Mapped[str] = mapped_column(
        String(16), default="all", nullable=False
    )

    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="rules")

    def __repr__(self) -> str:
        return f"<MerchantRules merchant_id={self.merchant_id}>"


# Avoid circular import issues — type strings used in relationship()
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product
    from .asset import AssetPack
    from .generation import GenerationJob
    from .note_package import NotePackage
    from .agent_team import AgentTeam
    from .prompt import PolicyRule
