from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from .common import BaseSchema, PaginatedResponse


class ProductCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., max_length=128)
    merchant_id: UUID
    primary_objective: str | None = Field(default=None, max_length=255)
    description: str | None = None


class ProductUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=128)
    primary_objective: str | None = Field(default=None, max_length=255)
    description: str | None = None
    status: Literal["active", "paused", "archived"] | None = None


class ProductResponse(BaseSchema):
    id: UUID
    merchant_id: UUID
    name: str
    category: str
    status: Literal["active", "paused", "archived"]
    primary_objective: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class ProductListResponse(PaginatedResponse[ProductResponse]):
    pass
