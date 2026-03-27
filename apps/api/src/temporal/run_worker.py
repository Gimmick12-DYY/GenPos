from __future__ import annotations

import asyncio
import logging
import signal

from temporalio.client import Client
from temporalio.worker import Worker

from src.core.config import settings
from src.temporal.activities.on_demand import run_on_demand_pipeline_activity
from src.temporal.activities.ping import ping_activity
from src.temporal.workflows.health import HealthCheckWorkflow
from src.temporal.workflows.on_demand import OnDemandGenerationWorkflow

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger.info(
        "Temporal worker connecting address=%s namespace=%s queue=%s",
        settings.temporal_host,
        settings.temporal_namespace,
        settings.temporal_task_queue,
    )
    client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
    )
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[OnDemandGenerationWorkflow, HealthCheckWorkflow],
        activities=[run_on_demand_pipeline_activity, ping_activity],
    )

    loop = asyncio.get_running_loop()

    def _request_shutdown() -> None:
        logger.info("Shutdown signal received; stopping Temporal worker…")
        asyncio.create_task(worker.shutdown())

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _request_shutdown)
        except NotImplementedError:
            pass

    await worker.run()


def main_sync() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main_sync()
