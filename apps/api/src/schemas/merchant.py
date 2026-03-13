from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from .common import BaseSchema


# ---------------------------------------------------------------------------
# Merchant
# ---------------------------------------------------------------------------

class MerchantCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., max_length=128)
    xhs_account_type: str = Field(..., max_length=64)
    uses_juguang: bool = False
    uses_pugongying: bool = False
    language: str = Field(default="zh-CN", max_length=10)
    timezone: str = Field(default="Asia/Shanghai", max_length=64)


class MerchantUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    industry: str | None = Field(default=None, max_length=128)
    xhs_account_type: str | None = Field(default=None, max_length=64)
    uses_juguang: bool | None = None
    uses_pugongying: bool | None = None
    language: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=64)


class MerchantResponse(BaseSchema):
    id: UUID
    name: str
    industry: str
    xhs_account_type: str
    uses_juguang: bool
    uses_pugongying: bool
    language: str
    timezone: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Merchant Rules
# ---------------------------------------------------------------------------

class MerchantRulesUpdate(BaseSchema):
    tone_preset: str | None = Field(default=None, max_length=128)
    banned_words: list[str] | None = None
    required_claims: list[str] | None = None
    banned_claims: list[str] | None = None
    compliance_level: Literal["strict", "standard", "relaxed"] | None = None
    review_mode: Literal["all", "sampling", "auto"] | None = None


class MerchantRulesResponse(BaseSchema):
    id: UUID
    merchant_id: UUID
    tone_preset: str | None
    banned_words: list[str]
    required_claims: list[str]
    banned_claims: list[str]
    compliance_level: Literal["strict", "standard", "relaxed"]
    review_mode: Literal["all", "sampling", "auto"]
    created_at: datetime
    updated_at: datetime
