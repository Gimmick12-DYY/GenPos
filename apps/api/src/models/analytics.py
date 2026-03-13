from __future__ import annotations

import uuid as _uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin


class PerformanceMetrics(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "performance_metrics"
    __table_args__ = (
        UniqueConstraint("note_package_id", "date", name="uq_perf_note_date"),
    )

    note_package_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("note_packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    saves: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    conversions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revenue: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    note_package: Mapped[NotePackage] = relationship("NotePackage", back_populates="performance_metrics")

    def __repr__(self) -> str:
        return f"<PerformanceMetrics date={self.date} note_package_id={self.note_package_id}>"


class ReviewEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "review_events"

    note_package_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("note_packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    note_package: Mapped[NotePackage] = relationship("NotePackage", back_populates="review_events")

    def __repr__(self) -> str:
        return f"<ReviewEvent action={self.action!r} id={self.id}>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .note_package import NotePackage
