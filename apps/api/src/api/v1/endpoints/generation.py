from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.common import WorkflowIDReusePolicy
from temporalio.exceptions import WorkflowAlreadyStartedError

from src.core.config import settings
from src.core.database import async_session_factory, get_db
from src.core.security import verify_cron_or_jwt, verify_token
from src.core.shanghai_calendar import shanghai_date_iso
from src.core.tenant import resolve_merchant_id
from src.models import GenerationJob, GenerationTask, NotePackage
from src.schemas import (
    DailyBatchAsyncStartResponse,
    DailyRunAllRequest,
    DailyRunAllResponse,
    DailyRunMerchantResult,
    DailyRunRequest,
    GenerationAsyncStartResponse,
    GenerationJobResponse,
    GenerationJobResultResponse,
    GenerationRequest,
    GenerationTaskResponse,
    TaskListResponse,
)
from src.services import generation_service, note_package_service
from src.temporal.client import get_temporal_client
from src.temporal.workflows.daily_batch import DailyBatchWorkflow
from src.temporal.workflows.on_demand import OnDemandGenerationWorkflow

router = APIRouter()


async def _count_active_generation_jobs(db: AsyncSession, merchant_id: UUID) -> int:
    stmt = (
        select(func.count())
        .select_from(GenerationJob)
        .where(
            GenerationJob.merchant_id == merchant_id,
            GenerationJob.status.in_(("pending", "running")),
        )
    )
    return int((await db.execute(stmt)).scalar_one())


async def _apply_generation_job_timeout(db: AsyncSession, job: GenerationJob) -> None:
    if job.status not in ("pending", "running"):
        return
    now = datetime.now(timezone.utc)
    created = job.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if now - created > timedelta(seconds=settings.generation_job_timeout_seconds):
        job.status = "failed"
        job.completed_at = now
        await db.commit()


@router.post("/request")
async def generate_on_demand(
    body: GenerationRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Submit an on-demand generation request and run the full agent pipeline."""
    merchant_id = resolve_merchant_id(body.merchant_id, token)
    active = await _count_active_generation_jobs(db, merchant_id)
    if active >= settings.max_concurrent_generation_jobs:
        raise HTTPException(
            status_code=429,
            detail=f"Too many concurrent generation jobs (max {settings.max_concurrent_generation_jobs})",
        )

    if settings.use_temporal_for_generation:
        job = GenerationJob(
            merchant_id=merchant_id,
            source_mode="on_demand",
            trigger_type="user_request",
            status="pending",
        )
        db.add(job)
        await db.flush()
        await db.commit()

        payload = {
            "job_id": str(job.id),
            "merchant_id": str(merchant_id),
            "product_id": str(body.product_id) if body.product_id else None,
            "user_message": "",
            "objective": body.objective,
            "persona": body.persona or "",
            "style_preference": body.style_preference or "",
            "special_instructions": body.special_instructions or "",
            "is_juguang": body.is_juguang,
            "is_pugongying": body.is_pugongying,
        }

        try:
            client = await get_temporal_client()
            handle = await client.start_workflow(
                OnDemandGenerationWorkflow.run,
                payload,
                id=f"on-demand-gen-{job.id}",
                task_queue=settings.temporal_task_queue,
            )
        except Exception as exc:
            async with async_session_factory() as session:
                row = await session.get(GenerationJob, job.id)
                if row:
                    row.status = "failed"
                    await session.commit()
            raise HTTPException(
                status_code=503,
                detail=f"Temporal unavailable: {exc}",
            ) from exc

        return GenerationAsyncStartResponse(
            generation_job_id=job.id,
            workflow_id=handle.id,
            run_id=handle.first_execution_run_id,
        )

    result = await generation_service.run_on_demand_generation(
        db=db,
        merchant_id=merchant_id,
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
    token: dict = Depends(verify_token),
):
    """Trigger daily generation for a merchant: all active products (sync or Temporal)."""
    merchant_id = resolve_merchant_id(body.merchant_id, token)
    date_str = shanghai_date_iso()
    if settings.use_temporal_for_daily_batch:
        try:
            client = await get_temporal_client()
            if body.force:
                wf_id = f"daily-batch-{merchant_id}-{date_str}-{uuid4().hex[:8]}"
            else:
                wf_id = f"daily-batch-{merchant_id}-{date_str}"
            handle = await client.start_workflow(
                DailyBatchWorkflow.run,
                {
                    "merchant_id": str(merchant_id),
                    "packages_per_product": body.packages_per_product,
                },
                id=wf_id,
                task_queue=settings.temporal_task_queue,
                id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
            )
            return DailyBatchAsyncStartResponse(
                workflow_id=handle.id,
                run_id=handle.first_execution_run_id,
                shanghai_date=date_str,
            )
        except WorkflowAlreadyStartedError as exc:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Daily batch already ran or is running for this merchant today "
                    f"({date_str}). Pass force=true to start a new run."
                ),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Temporal unavailable: {exc}",
            ) from exc

    result = await generation_service.run_daily_batch(
        db,
        merchant_id=merchant_id,
        packages_per_product=body.packages_per_product,
        max_concurrent=1,
        force=body.force,
        skip_if_already_run=body.skip_if_already_run,
    )
    return result


@router.post("/daily/run-all", response_model=DailyRunAllResponse)
async def trigger_daily_generation_all_merchants(
    body: DailyRunAllRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_cron_or_jwt),
):
    """
    Run daily batch for each merchant that has at least one product (BL-201 cron hook).
    Protected by JWT or X-GenPos-Cron-Secret when DAILY_BATCH_CRON_SECRET is set.
    """
    date_str = shanghai_date_iso()
    merchant_ids = await generation_service.list_all_merchant_ids(db)
    results: list[DailyRunMerchantResult] = []

    if settings.use_temporal_for_daily_batch:
        try:
            client = await get_temporal_client()
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Temporal unavailable: {exc}",
            ) from exc

        for mid in merchant_ids:
            if body.force:
                wf_id = f"daily-batch-{mid}-{date_str}-{uuid4().hex[:8]}"
            else:
                wf_id = f"daily-batch-{mid}-{date_str}"
            try:
                handle = await client.start_workflow(
                    DailyBatchWorkflow.run,
                    {
                        "merchant_id": str(mid),
                        "packages_per_product": body.packages_per_product,
                    },
                    id=wf_id,
                    task_queue=settings.temporal_task_queue,
                    id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
                )
                results.append(
                    DailyRunMerchantResult(
                        merchant_id=mid,
                        status="started",
                        workflow_id=handle.id,
                        detail=None,
                        packages_created=None,
                    )
                )
            except WorkflowAlreadyStartedError:
                results.append(
                    DailyRunMerchantResult(
                        merchant_id=mid,
                        status="skipped",
                        workflow_id=wf_id,
                        detail="already_running_or_completed_today",
                        packages_created=None,
                    )
                )
            except Exception as exc:
                results.append(
                    DailyRunMerchantResult(
                        merchant_id=mid,
                        status="error",
                        detail=str(exc),
                        packages_created=None,
                    )
                )

        return DailyRunAllResponse(
            shanghai_date=date_str,
            temporal=True,
            merchants=results,
        )

    for mid in merchant_ids:
        try:
            out = await generation_service.run_daily_batch(
                db,
                merchant_id=mid,
                packages_per_product=body.packages_per_product,
                max_concurrent=1,
                force=body.force,
                skip_if_already_run=body.skip_if_already_run,
            )
            if out.get("skipped"):
                results.append(
                    DailyRunMerchantResult(
                        merchant_id=mid,
                        status="skipped",
                        detail=out.get("reason"),
                        packages_created=0,
                    )
                )
            else:
                results.append(
                    DailyRunMerchantResult(
                        merchant_id=mid,
                        status="completed",
                        packages_created=int(out.get("packages_created") or 0),
                        detail=None,
                    )
                )
        except Exception as exc:
            results.append(
                DailyRunMerchantResult(
                    merchant_id=mid,
                    status="error",
                    detail=str(exc),
                    packages_created=None,
                )
            )

    return DailyRunAllResponse(
        shanghai_date=date_str,
        temporal=False,
        merchants=results,
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

    await _apply_generation_job_timeout(db, job)
    job = await db.get(GenerationJob, job_id)

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


@router.get("/jobs/{job_id}/result", response_model=GenerationJobResultResponse)
async def get_generation_job_result(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """BL-111: note package produced by a completed job (if any)."""
    job = await db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    await _apply_generation_job_timeout(db, job)
    job = await db.get(GenerationJob, job_id)
    if not job or job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Job not complete: {job.status if job else 'missing'}",
        )
    stmt = select(NotePackage).where(NotePackage.generation_job_id == job_id).limit(1)
    row = (await db.execute(stmt)).scalar_one_or_none()
    pkg_resp = None
    if row is not None:
        full = await note_package_service.get_note_package_detail(db, row.id)
        if full is not None:
            pkg_resp = note_package_service.note_package_to_response(full)
    return GenerationJobResultResponse(
        job=GenerationJobResponse(
            id=job.id,
            merchant_id=job.merchant_id,
            source_mode=job.source_mode,  # type: ignore[arg-type]
            trigger_type=job.trigger_type,  # type: ignore[arg-type]
            status=job.status,  # type: ignore[arg-type]
            team_id=job.team_id,
            created_at=job.created_at,
            completed_at=job.completed_at,
        ),
        note_package=pkg_resp,
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
