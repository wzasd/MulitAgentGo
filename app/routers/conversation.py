"""
会话路由
"""
import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, Conversation, Message
from app.models import ConversationCreate, ConversationResponse

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreate):
    """创建会话"""
    session_id = str(uuid.uuid4())

    async with async_session() as db:
        conversation = Conversation(
            session_id=session_id,
            user_id=request.user_id,
            title=request.title or "新会话"
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return ConversationResponse(
            session_id=conversation.session_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )


@router.get("/conversations/{user_id}")
async def get_conversations(user_id: str, limit: int = 20):
    """获取用户的会话列表"""
    async with async_session() as db:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        conversations = result.scalars().all()

        return {
            "user_id": user_id,
            "conversations": [
                {
                    "session_id": c.session_id,
                    "title": c.title,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat()
                }
                for c in conversations
            ]
        }


@router.get("/conversations/detail/{session_id}")
async def get_conversation(session_id: str):
    """获取会话详情"""
    async with async_session() as db:
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 获取消息
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        messages = msg_result.scalars().all()

        return {
            "session_id": conversation.session_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
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


@router.delete("/conversations/{session_id}")
async def delete_conversation(session_id: str):
    """删除会话"""
    async with async_session() as db:
        # 删除消息
        await db.execute(
            delete(Message).where(Message.session_id == session_id)
        )
        # 删除会话
        await db.execute(
            delete(Conversation).where(Conversation.session_id == session_id)
        )
        await db.commit()

        return {"message": "删除成功"}
