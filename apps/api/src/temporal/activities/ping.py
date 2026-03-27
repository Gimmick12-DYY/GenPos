from __future__ import annotations

from temporalio import activity


@activity.defn(name="ping_activity")
async def ping_activity() -> str:
    return "pong"
