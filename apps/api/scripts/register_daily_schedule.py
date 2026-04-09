#!/usr/bin/env python3
"""
Register Temporal schedule: DailyRunAllScheduledWorkflow at 06:00 Asia/Shanghai (BL-201).

Requires Temporal reachable (TEMPORAL_HOST) and worker registered with the workflow/activity.

Usage (from repo root or apps/api with PYTHONPATH=src):
  cd apps/api && PYTHONPATH=src python scripts/register_daily_schedule.py
  PYTHONPATH=src python scripts/register_daily_schedule.py --replace
  PYTHONPATH=src python scripts/register_daily_schedule.py --packages-per-product 2
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# apps/api/src on path
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from temporalio.client import (  # noqa: E402
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec,
    ScheduleState,
)
from temporalio.service import RPCError, RPCStatusCode  # noqa: E402

from src.core.config import settings  # noqa: E402
from src.temporal.workflows.daily_run_all import DailyRunAllScheduledWorkflow  # noqa: E402

SCHEDULE_ID = "genpos-daily-run-all"


async def main() -> None:
    parser = argparse.ArgumentParser(description="Register GenPos daily run-all Temporal schedule")
    parser.add_argument(
        "--replace",
        action="store_true",
        help=f"Delete existing schedule {SCHEDULE_ID!r} before creating",
    )
    parser.add_argument(
        "--packages-per-product",
        type=int,
        default=3,
        help="Payload passed to each scheduled run (default 3)",
    )
    args = parser.parse_args()

    client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
    )

    handle = client.get_schedule_handle(SCHEDULE_ID)
    if args.replace:
        try:
            await handle.delete()
            print(f"Deleted schedule {SCHEDULE_ID!r}")
        except RPCError as e:
            if e.status != RPCStatusCode.NOT_FOUND:
                raise

    schedule = Schedule(
        action=ScheduleActionStartWorkflow(
            DailyRunAllScheduledWorkflow.run,
            {"packages_per_product": args.packages_per_product},
            task_queue=settings.temporal_task_queue,
        ),
        spec=ScheduleSpec(
            cron_expressions=["0 6 * * *"],
            time_zone_name="Asia/Shanghai",
        ),
        state=ScheduleState(note="GenPos BL-201: daily batch for all merchants with active products"),
    )

    try:
        await client.create_schedule(SCHEDULE_ID, schedule)
        print(
            f"Created schedule {SCHEDULE_ID!r}: 06:00 Asia/Shanghai, "
            f"packages_per_product={args.packages_per_product}, queue={settings.temporal_task_queue!r}"
        )
    except RPCError as e:
        if e.status == RPCStatusCode.ALREADY_EXISTS:
            print(
                f"Schedule {SCHEDULE_ID!r} already exists. Re-run with --replace to recreate.",
                file=sys.stderr,
            )
            raise SystemExit(1) from e
        raise


if __name__ == "__main__":
    asyncio.run(main())
