from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin


class GenerationJob(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "generation_jobs"

    merchant_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_mode: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)
    team_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_teams.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="generation_jobs")
    team: Mapped[AgentTeam | None] = relationship("AgentTeam", back_populates="generation_jobs")
    tasks: Mapped[list[GenerationTask]] = relationship(
        "GenerationTask", back_populates="job", cascade="all, delete-orphan"
    )
    note_packages: Mapped[list[NotePackage]] = relationship("NotePackage", back_populates="generation_job")

    def __repr__(self) -> str:
        return f"<GenerationJob status={self.status!r} id={self.id}>"


class GenerationTask(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "generation_tasks"

    job_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    input_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)
    agent_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    persona_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    job: Mapped[GenerationJob] = relationship("GenerationJob", back_populates="tasks")
    persona: Mapped[Persona | None] = relationship("Persona", back_populates="generation_tasks")

    def __repr__(self) -> str:
        return f"<GenerationTask type={self.task_type!r} id={self.id}>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_team import AgentTeam
    from .merchant import Merchant
    from .note_package import NotePackage
    from .persona import Persona
