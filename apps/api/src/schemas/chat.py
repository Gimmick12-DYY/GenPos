from __future__ import annotations

from .common import BaseSchema
from .note_package import NotePackageResponse


class ChatMessageRequest(BaseSchema):
    merchant_id: str
    message: str


class ChatMessageResponse(BaseSchema):
    response: str
    intent: str | None = None
    structured_job: dict | None = None
    note_packages: list[NotePackageResponse] | None = None
