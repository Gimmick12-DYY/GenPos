from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse(BaseSchema, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]

    @property
    def has_more(self) -> bool:
        return self.offset + self.limit < self.total


class IDResponse(BaseSchema):
    id: UUID
