from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ChatMessage


async def append_message(
    db: AsyncSession,
    *,
    merchant_id: UUID,
    session_id: UUID,
    role: str,
    content: str,
    metadata: dict | None = None,
) -> ChatMessage:
    row = ChatMessage(
        merchant_id=merchant_id,
        session_id=session_id,
        role=role,
        content=content,
        metadata_json=metadata,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def list_messages(
    db: AsyncSession,
    *,
    merchant_id: UUID,
    session_id: UUID,
    limit: int = 50,
    before: datetime | None = None,
) -> list[ChatMessage]:
    q = select(ChatMessage).where(
        ChatMessage.merchant_id == merchant_id,
        ChatMessage.session_id == session_id,
    )
    if before is not None:
        q = q.where(ChatMessage.created_at < before)
    q = q.order_by(ChatMessage.created_at.desc()).limit(limit)
    rows = list((await db.execute(q)).scalars().all())
    return list(reversed(rows))


async def delete_session_messages(
    db: AsyncSession,
    *,
    merchant_id: UUID,
    session_id: UUID,
) -> int:
    """Delete all messages for a chat session. Returns deleted row count."""
    stmt = delete(ChatMessage).where(
        ChatMessage.merchant_id == merchant_id,
        ChatMessage.session_id == session_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return int(result.rowcount or 0)
