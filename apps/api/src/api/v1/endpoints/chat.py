import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import ChatMessageRequest, ChatMessageResponse, NotePackageResponse
from src.services import generation_service

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    body: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Send a free-text message to the Founder Copilot and run the generation pipeline."""
    try:
        merchant_uuid = UUID(body.merchant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid merchant_id format")

    try:
        result = await generation_service.run_on_demand_generation(
            db=db,
            merchant_id=merchant_uuid,
            user_message=body.message,
        )
    except Exception as e:
        logging.getLogger(__name__).exception("Chat generation failed")
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
