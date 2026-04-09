from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.temporal.activities.daily_run_all import run_daily_run_all_activity


@workflow.defn(name="DailyRunAllScheduledWorkflow")
class DailyRunAllScheduledWorkflow:
    """Scheduled parent: one activity runs all merchants (sync pipeline in worker)."""

    @workflow.run
    async def run(self, payload: dict) -> dict:
        return await workflow.execute_activity(
            run_daily_run_all_activity,
            payload,
            start_to_close_timeout=timedelta(hours=4),
            retry_policy=RetryPolicy(maximum_attempts=1),
        )
