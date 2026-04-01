"""Asia/Shanghai calendar helpers for daily batch idempotency (BL-201)."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

_SHANGHAI = ZoneInfo("Asia/Shanghai")


def shanghai_today() -> date:
    """Current calendar date in Asia/Shanghai."""
    return datetime.now(_SHANGHAI).date()


def shanghai_date_iso(d: date | None = None) -> str:
    """ISO date string for workflow IDs (YYYY-MM-DD)."""
    day = d or shanghai_today()
    return day.isoformat()
