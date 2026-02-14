"""
对话路由
"""
import uuid
import json
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models import ChatRequest, ChatResponse
from agents.main_plan_agent import MainPlanAgent

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """聊天接口"""
    # 获取或创建智能体
    agent = MainPlanAgent(session_id=request.session_id)

    # 处理消息
    if request.stream:
        # 流式响应
        async def generate():
            async for chunk in agent.stream_chat(request.message):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            yield f"data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    else:
        # 非流式响应
        result = await agent.chat(request.message)
        return result


@router.post("/chat/simple")
async def chat_simple(request: ChatRequest):
    """简单聊天接口（非流式）"""
    agent = MainPlanAgent(session_id=request.session_id)
    result = await agent.chat(request.message)
    return result


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """获取聊天历史"""
    from sqlalchemy import select
    from app.database import async_session, Message

    async with async_session() as session:
        result = await session.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()

        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ]
        }
