from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.temporal.activities.daily_batch import run_daily_batch_activity


@workflow.defn(name="DailyBatchWorkflow")
class DailyBatchWorkflow:
    """One-activity daily batch for a single merchant (expand to multi-tenant later)."""

    @workflow.run
    async def run(self, payload: dict) -> dict:
        return await workflow.execute_activity(
            run_daily_batch_activity,
            payload,
            start_to_close_timeout=timedelta(hours=2),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
