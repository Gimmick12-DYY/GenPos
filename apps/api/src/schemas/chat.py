from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .common import BaseSchema
from .note_package import NotePackageResponse


class ChatMessageRequest(BaseSchema):
    merchant_id: str
    message: str


class ChatStreamRequest(BaseSchema):
    merchant_id: str
    session_id: str
    message: str
    product_id: str | None = None
    objective: str = "seeding"


class ChatHistoryMessage(BaseSchema):
    id: UUID
    role: str
    content: str
    created_at: datetime
    metadata_json: dict | None = None


class ChatMessageResponse(BaseSchema):
    response: str
    intent: str | None = None
    structured_job: dict | None = None
    note_packages: list[NotePackageResponse] | None = None
