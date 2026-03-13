from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from .common import BaseSchema, PaginatedResponse


class PersonaCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    communication_style: str | None = Field(default=None, max_length=128)
    decision_style: str | None = Field(default=None, max_length=128)
    tone_rules: list[str] = Field(default_factory=list)
    forbidden_behaviors: list[str] = Field(default_factory=list)


class PersonaUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    communication_style: str | None = Field(default=None, max_length=128)
    decision_style: str | None = Field(default=None, max_length=128)
    tone_rules: list[str] | None = None
    forbidden_behaviors: list[str] | None = None


class PersonaResponse(BaseSchema):
    id: UUID
    name: str
    description: str | None
    communication_style: str | None
    decision_style: str | None
    tone_rules: list[str]
    forbidden_behaviors: list[str]
    version: int
    active: bool
    created_at: datetime
    updated_at: datetime


class PersonaListResponse(PaginatedResponse[PersonaResponse]):
    pass
