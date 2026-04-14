from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from .common import BaseSchema
from .persona import PersonaResponse

# ---------------------------------------------------------------------------
# Agent Roles
# ---------------------------------------------------------------------------


class AgentRoleResponse(BaseSchema):
    id: UUID
    role_key: str
    display_name: str
    description: str | None
    is_required_default: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Agent Teams
# ---------------------------------------------------------------------------


class AgentTeamCreate(BaseSchema):
    merchant_id: UUID | None = None
    team_name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None


class AgentTeamUpdate(BaseSchema):
    team_name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None


class AgentTeamResponse(BaseSchema):
    id: UUID
    merchant_id: UUID | None
    team_name: str
    description: str | None
    version: int
    active: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Agent Team Members
# ---------------------------------------------------------------------------


class AgentTeamMemberCreate(BaseSchema):
    role_id: UUID
    persona_id: UUID
    is_required: bool = True
    ordering: int = 0


class AgentTeamMemberResponse(BaseSchema):
    id: UUID
    team_id: UUID
    role_id: UUID
    persona_id: UUID
    is_required: bool
    ordering: int
    created_at: datetime
    role: AgentRoleResponse
    persona: PersonaResponse


# ---------------------------------------------------------------------------
# Detail (composite)
# ---------------------------------------------------------------------------


class AgentTeamDetailResponse(AgentTeamResponse):
    members: list[AgentTeamMemberResponse] = []


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


class ExperimentCreate(BaseSchema):
    experiment_name: str = Field(..., min_length=1, max_length=255)
    hypothesis: str | None = None


class ExperimentResponse(BaseSchema):
    id: UUID
    team_id: UUID
    experiment_name: str
    hypothesis: str | None
    status: Literal["draft", "running", "completed", "cancelled"]
    result_summary: dict[str, Any] | None
    created_at: datetime
    completed_at: datetime | None
