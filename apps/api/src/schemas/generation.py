from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from .common import BaseSchema
from .note_package import NotePackageResponse


class GenerationRequest(BaseSchema):
    merchant_id: UUID
    product_id: UUID | None = None
    objective: str = Field(..., max_length=128)
    persona: str | None = Field(default=None, max_length=128)
    style_preference: str | None = Field(default=None, max_length=64)
    special_instructions: str | None = None
    is_juguang: bool = False
    is_pugongying: bool = False


class DailyRunRequest(BaseSchema):
    merchant_id: UUID
    packages_per_product: int = Field(default=3, ge=1, le=10)


class DailyBatchAsyncStartResponse(BaseSchema):
    """Daily batch enqueued on Temporal worker."""

    workflow_id: str
    run_id: str
    mode: Literal["async"] = "async"


class GenerationJobResponse(BaseSchema):
    id: UUID
    merchant_id: UUID
    source_mode: Literal["daily_auto", "on_demand", "campaign"]
    trigger_type: Literal["scheduler", "user_request", "api"]
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    team_id: UUID | None
    created_at: datetime
    completed_at: datetime | None


class GenerationTaskResponse(BaseSchema):
    id: UUID
    job_id: UUID
    task_type: Literal["strategy", "text_gen", "image_gen", "compliance", "ranking"]
    status: Literal["pending", "running", "completed", "failed"]
    agent_role: str | None
    persona_id: UUID | None
    created_at: datetime
    completed_at: datetime | None


class TaskListResponse(BaseSchema):
    tasks: list[GenerationTaskResponse]


class GenerationAsyncStartResponse(BaseSchema):
    """Returned when `USE_TEMPORAL_FOR_GENERATION` is enabled: pipeline runs in the worker."""

    generation_job_id: UUID
    workflow_id: str
    run_id: str
    status: Literal["pending"] = "pending"
    mode: Literal["async"] = "async"


class GenerationJobResultResponse(BaseSchema):
    """Payload when a job has finished (BL-111)."""

    job: GenerationJobResponse
    note_package: NotePackageResponse | None = None
