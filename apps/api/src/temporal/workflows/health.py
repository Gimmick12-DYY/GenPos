from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.temporal.activities.ping import ping_activity


@workflow.defn(name="HealthCheckWorkflow")
class HealthCheckWorkflow:
    @workflow.run
    async def run(self) -> str:
        return await workflow.execute_activity(
            ping_activity,
            start_to_close_timeout=timedelta(seconds=30),
        )
