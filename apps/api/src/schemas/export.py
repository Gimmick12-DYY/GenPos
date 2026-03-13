from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from .common import BaseSchema


class ExportResponse(BaseSchema):
    note_package_id: UUID
    brief_type: Literal["note_export", "juguang", "pugongying"]
    content_json: dict[str, Any]
    export_url: str | None = None
    created_at: datetime
