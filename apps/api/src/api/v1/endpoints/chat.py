import json
import logging
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.llm_client import llm_client
from src.core.database import async_session_factory, get_db
from src.core.security import verify_token
from src.core.tenant import merchant_id_from_token, parse_optional_merchant_id_str
from src.schemas import (
    ChatHistoryMessage,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionClearResponse,
    ChatStreamRequest,
    NotePackageResponse,
)
from src.services import chat_service, generation_service, product_catalog_service

router = APIRouter()
logger = logging.getLogger(__name__)


def _parse_uuid(value: str, field: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid {field}") from e


@router.delete("/session", response_model=ChatSessionClearResponse)
async def clear_chat_session(
    session_id: UUID,
    merchant_id: UUID = Depends(merchant_id_from_token),
    db: AsyncSession = Depends(get_db),
):
    """Delete all messages for this chat session (server-side history)."""
    deleted = await chat_service.delete_session_messages(
        db, merchant_id=merchant_id, session_id=session_id
    )
    return ChatSessionClearResponse(deleted=deleted)


@router.get("/messages", response_model=list[ChatHistoryMessage])
async def list_chat_messages(
    session_id: UUID,
    merchant_id: UUID = Depends(merchant_id_from_token),
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """BL-101: paginated chat history for a session."""
    rows = await chat_service.list_messages(
        db, merchant_id=merchant_id, session_id=session_id, limit=limit
    )
    return [
        ChatHistoryMessage(
            id=r.id,
            role=r.role,
            content=r.content,
            created_at=r.created_at,
            metadata_json=r.metadata_json,
        )
        for r in rows
    ]


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    body: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Send a free-text message to the Founder Copilot and run the generation pipeline."""
    merchant_uuid = parse_optional_merchant_id_str(body.merchant_id, token)

    try:
        result = await generation_service.run_on_demand_generation(
            db=db,
            merchant_id=merchant_uuid,
            user_message=body.message,
        )
    except Exception as e:
        logger.exception("Chat generation failed")
        return ChatMessageResponse(
            response=f"生成过程遇到问题：{getattr(e, 'message', str(e))}。请检查 API 日志或稍后重试。",
            intent="error",
            structured_job=None,
            note_packages=None,
        )

    note_packages: list[NotePackageResponse] | None = None
    if result.get("note_package_id"):
        note_packages = []

    response_text = result.get("response_to_user", "")
    if not response_text:
        if result.get("error"):
            response_text = f"生成过程遇到问题：{result['error']}"
        elif result.get("note_content"):
            response_text = "内容已生成完成，请查看笔记包详情。"
        else:
            response_text = "请求已处理。"

    structured_job = result.get("strategy_plan") or result.get("note_content")
    intent: str | None = None
    if result.get("note_content"):
        intent = "generate_note"
    elif result.get("error"):
        intent = "error"

    return ChatMessageResponse(
        response=response_text,
        intent=intent,
        structured_job=structured_job,
        note_packages=note_packages,
    )


async def _chat_stream_events(body: ChatStreamRequest, token: dict) -> AsyncIterator[str]:
    merchant_uuid = parse_optional_merchant_id_str(body.merchant_id, token)
    session_uuid = _parse_uuid(body.session_id, "session_id")

    product_id: UUID | None = None
    if body.product_id:
        product_id = _parse_uuid(body.product_id, "product_id")

    meta_out: dict = {}

    catalog_block = ""
    async with async_session_factory() as db:
        await chat_service.append_message(
            db,
            merchant_id=merchant_uuid,
            session_id=session_uuid,
            role="user",
            content=body.message,
        )
        catalog = await product_catalog_service.load_active_product_catalog(
            db, merchant_uuid
        )
        catalog_block = product_catalog_service.format_catalog_text_for_prompt(catalog)

    yield f"data: {json.dumps({'type': 'start'}, ensure_ascii=False)}\n\n"

    system_preamble = (
        "你是小红书商家的创作顾问，熟悉该商户「我的产品库」里已录入的商品。"
        "你必须根据下方「产品库」中的真实商品来理解用户提到的简称或代号，不要要求用户重复填写库里已有信息。"
        "先用一两句话友好确认理解，并说明接下来会为其整理笔记思路或生成草案（语气轻松专业，纯中文）。\n\n"
        f"{catalog_block}"
    )
    try:
        async for chunk in llm_client.chat_completion_stream(
            system_prompt=system_preamble,
            user_prompt=body.message,
            max_tokens=500,
        ):
            yield f"data: {json.dumps({'type': 'token', 'text': chunk}, ensure_ascii=False)}\n\n"
    except Exception as e:
        logger.warning("Chat stream preamble failed: %s", e)
        yield f"data: {json.dumps({'type': 'token', 'text': '正在生成内容，请稍候…'}, ensure_ascii=False)}\n\n"

    try:
        async with async_session_factory() as db:
            result = await generation_service.run_on_demand_generation(
                db=db,
                merchant_id=merchant_uuid,
                product_id=product_id,
                user_message=body.message,
                objective=body.objective,
                session_id=session_uuid,
            )
    except Exception as e:
        logger.exception("Chat stream pipeline failed")
        err_payload = {"type": "error", "message": str(e)}
        yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
        async with async_session_factory() as db:
            await chat_service.append_message(
                db,
                merchant_id=merchant_uuid,
                session_id=session_uuid,
                role="assistant",
                content=f"生成失败：{e}",
                metadata={"error": True},
            )
        return

    response_text = result.get("response_to_user", "")
    if not response_text:
        if result.get("error"):
            response_text = f"生成遇到问题：{result['error']}"
        elif result.get("note_content"):
            response_text = "内容已生成。你可以在「待审核」中查看笔记包。"
        else:
            response_text = "请求已处理。"

    np_id = result.get("note_package_id")
    meta_out["note_package_id"] = np_id
    meta_out["generation_job_id"] = result.get("generation_job_id")

    async with async_session_factory() as db:
        await chat_service.append_message(
            db,
            merchant_id=merchant_uuid,
            session_id=session_uuid,
            role="assistant",
            content=response_text,
            metadata=meta_out or None,
        )

    done = {
        "type": "done",
        "response": response_text,
        "note_package_id": np_id,
        "generation_job_id": result.get("generation_job_id"),
        "error": result.get("error"),
    }
    yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def chat_stream(
    body: ChatStreamRequest,
    token: dict = Depends(verify_token),
):
    """BL-101: SSE stream (preamble tokens + pipeline + done payload)."""
    return StreamingResponse(
        _chat_stream_events(body, token),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
