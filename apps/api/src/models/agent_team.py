from __future__ import annotations

import uuid as _uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentRole(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "agent_roles"

    role_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_output_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_required_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    team_members: Mapped[list[AgentTeamMember]] = relationship(
        "AgentTeamMember", back_populates="role"
    )

    def __repr__(self) -> str:
        return f"<AgentRole {self.role_key!r}>"


class AgentTeam(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_teams"

    merchant_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    team_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    merchant: Mapped[Merchant | None] = relationship("Merchant", back_populates="agent_teams")
    members: Mapped[list[AgentTeamMember]] = relationship(
        "AgentTeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    collaboration_edges: Mapped[list[AgentCollaborationEdge]] = relationship(
        "AgentCollaborationEdge", back_populates="team", cascade="all, delete-orphan"
    )
    experiments: Mapped[list[PersonaExperiment]] = relationship(
        "PersonaExperiment", back_populates="team", cascade="all, delete-orphan"
    )
    generation_jobs: Mapped[list[GenerationJob]] = relationship(
        "GenerationJob", back_populates="team"
    )

    def __repr__(self) -> str:
        return f"<AgentTeam {self.team_name!r} v={self.version}>"


class AgentTeamMember(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "agent_team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "role_id", name="uq_team_role"),
    )

    team_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    persona_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ordering: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    team: Mapped[AgentTeam] = relationship("AgentTeam", back_populates="members")
    role: Mapped[AgentRole] = relationship("AgentRole", back_populates="team_members")
    persona: Mapped[Persona | None] = relationship("Persona", back_populates="team_members")

    def __repr__(self) -> str:
        return f"<AgentTeamMember team={self.team_id} role={self.role_id}>"


class AgentCollaborationEdge(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "agent_collaboration_edges"
    __table_args__ = (
        CheckConstraint("from_role_id != to_role_id", name="ck_no_self_edge"),
    )

    team_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_role_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_roles.id", ondelete="CASCADE"), nullable=False
    )
    to_role_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_roles.id", ondelete="CASCADE"), nullable=False
    )
    edge_type: Mapped[str] = mapped_column(String(24), nullable=False)
    rule_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    team: Mapped[AgentTeam] = relationship("AgentTeam", back_populates="collaboration_edges")

    def __repr__(self) -> str:
        return f"<AgentCollaborationEdge {self.edge_type} {self.from_role_id}->{self.to_role_id}>"


class PersonaExperiment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "persona_experiments"

    team_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    experiment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hypothesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft", nullable=False)
    result_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    team: Mapped[AgentTeam] = relationship("AgentTeam", back_populates="experiments")

    def __repr__(self) -> str:
        return f"<PersonaExperiment {self.experiment_name!r} status={self.status}>"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .generation import GenerationJob
    from .merchant import Merchant
    from .persona import Persona
