from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin


class PromptVersion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("prompt_family", "version", name="uq_prompt_family_version"),)

    prompt_family: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="draft", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PromptVersion family={self.prompt_family!r} v={self.version}>"


class PolicyRule(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "policy_rules"

    merchant_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    scope: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    rule_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    merchant: Mapped[Merchant | None] = relationship("Merchant", back_populates="policy_rules")

    def __repr__(self) -> str:
        return f"<PolicyRule type={self.rule_type!r} scope={self.scope!r} id={self.id}>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .merchant import Merchant
