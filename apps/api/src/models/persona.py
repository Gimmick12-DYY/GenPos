from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Persona(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "personas"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    communication_style: Mapped[str | None] = mapped_column(String(128), nullable=True)
    decision_style: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tone_rules_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    forbidden_behaviors_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    constraints: Mapped[list[PersonaConstraint]] = relationship(
        "PersonaConstraint", back_populates="persona", cascade="all, delete-orphan"
    )
    team_members: Mapped[list[AgentTeamMember]] = relationship(
        "AgentTeamMember", back_populates="persona"
    )
    generation_tasks: Mapped[list[GenerationTask]] = relationship(
        "GenerationTask", back_populates="persona"
    )

    def __repr__(self) -> str:
        return f"<Persona {self.name!r} v={self.version}>"


class PersonaConstraint(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "persona_constraints"

    persona_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    constraint_type: Mapped[str] = mapped_column(String(64), nullable=False)
    constraint_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    persona: Mapped[Persona] = relationship("Persona", back_populates="constraints")

    def __repr__(self) -> str:
        return f"<PersonaConstraint type={self.constraint_type!r} id={self.id}>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_team import AgentTeamMember
    from .generation import GenerationTask
