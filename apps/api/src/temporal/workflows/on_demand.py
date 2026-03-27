from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.temporal.activities.on_demand import run_on_demand_pipeline_activity


@workflow.defn(name="OnDemandGenerationWorkflow")
class OnDemandGenerationWorkflow:
    """Single-activity workflow wrapping the existing agent orchestrator."""

    @workflow.run
    async def run(self, payload: dict) -> dict:
        return await workflow.execute_activity(
            run_on_demand_pipeline_activity,
            payload,
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
