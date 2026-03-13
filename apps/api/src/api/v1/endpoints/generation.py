from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.models import GenerationJob, GenerationTask
from src.schemas import (
    DailyRunRequest,
    GenerationJobResponse,
    GenerationRequest,
    GenerationTaskResponse,
    TaskListResponse,
)
from src.services import generation_service

router = APIRouter()


@router.post("/request")
async def generate_on_demand(
    body: GenerationRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Submit an on-demand generation request and run the full agent pipeline."""
    result = await generation_service.run_on_demand_generation(
        db=db,
        merchant_id=body.merchant_id,
        product_id=body.product_id,
        objective=body.objective,
        persona=body.persona or "",
        style_preference=body.style_preference or "",
        special_instructions=body.special_instructions or "",
        is_juguang=body.is_juguang,
        is_pugongying=body.is_pugongying,
    )

    if "error" in result and "note_package_id" not in result:
        return JSONResponse(status_code=422, content=result)

    return result


@router.post("/daily/run")
async def trigger_daily_generation(
    body: DailyRunRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Trigger daily generation pipeline (Phase 2)."""
    return JSONResponse(
        status_code=501,
        content={"detail": "Daily generation pipeline not yet implemented"},
    )


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get generation job status and metadata."""
    job = await db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")

    return GenerationJobResponse(
        id=job.id,
        merchant_id=job.merchant_id,
        source_mode=job.source_mode,
        trigger_type=job.trigger_type,
        status=job.status,
        team_id=job.team_id,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.get("/jobs/{job_id}/tasks", response_model=TaskListResponse)
async def list_generation_tasks(
    job_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """List tasks belonging to a generation job."""
    job = await db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")

    stmt = (
        select(GenerationTask)
        .where(GenerationTask.job_id == job_id)
        .order_by(GenerationTask.created_at)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=[
            GenerationTaskResponse(
                id=t.id,
                job_id=t.job_id,
                task_type=t.task_type,
                status=t.status,
                agent_role=t.agent_role,
                persona_id=t.persona_id,
                created_at=t.created_at,
                completed_at=t.completed_at,
            )
            for t in tasks
        ]
    )
