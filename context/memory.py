"""
上下文工程 - 记忆管理
"""
from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, SessionMemory


class MemoryManager:
    """
    记忆管理器
    负责管理会话级别的记忆，支持多智能体间的记忆共享
    """

    def __init__(self, session_id: str):
        self.session_id = session_id

    async def add_user_message(self, content: str, agent_name: str = "user"):
        """添加用户消息到记忆"""
        await self._add_memory(agent_name, "user_message", content)

    async def add_assistant_message(self, content: str, agent_name: str = "main"):
        """添加助手消息到记忆"""
        await self._add_memory(agent_name, "assistant_message", content)

    async def add_agent_memory(self, agent_name: str, memory_type: str, content: str):
        """添加智能体专用记忆"""
        await self._add_memory(agent_name, memory_type, content)

    async def _add_memory(self, agent_name: str, memory_type: str, content: str):
        """添加记忆到数据库"""
        async with async_session() as db:
            memory = SessionMemory(
                session_id=self.session_id,
                agent_name=agent_name,
                memory_type=memory_type,
                content=content
            )
            db.add(memory)
            await db.commit()

    async def get_context(self, agent_name: str = None, limit: int = 10) -> List[dict]:
        """获取对话上下文"""
        async with async_session() as db:
            query = select(SessionMemory).where(
                SessionMemory.session_id == self.session_id
            )

            if agent_name:
                query = query.where(SessionMemory.agent_name == agent_name)

            query = query.order_by(SessionMemory.created_at.desc()).limit(limit)

            result = await db.execute(query)
            memories = result.scalars().all()

            # 返回倒序（旧的在前）
            return [
                {
                    "role": m.memory_type.replace("_message", ""),
                    "content": m.content,
                    "agent": m.agent_name,
                    "timestamp": m.created_at.isoformat()
                }
                for m in reversed(memories)
            ]

    async def get_shared_context(self, agent_names: List[str], limit: int = 10) -> List[dict]:
        """获取跨智能体共享的上下文"""
        async with async_session() as db:
            result = await db.execute(
                select(SessionMemory)
                .where(SessionMemory.session_id == self.session_id)
                .where(SessionMemory.agent_name.in_(agent_names))
                .order_by(SessionMemory.created_at.desc())
                .limit(limit)
            )
            memories = result.scalars().all()

            return [
                {
                    "role": m.memory_type.replace("_message", ""),
                    "content": m.content,
                    "agent": m.agent_name,
                    "timestamp": m.created_at.isoformat()
                }
                for m in reversed(memories)
            ]

    async def get_agent_memory(self, agent_name: str, memory_type: str = None) -> List[dict]:
        """获取特定智能体的记忆"""
        async with async_session() as db:
            query = select(SessionMemory).where(
                SessionMemory.session_id == self.session_id,
                SessionMemory.agent_name == agent_name
            )

            if memory_type:
                query = query.where(SessionMemory.memory_type == memory_type)

            result = await db.execute(query.order_by(SessionMemory.created_at))
            memories = result.scalars().all()

            return [{"type": m.memory_type, "content": m.content} for m in memories]

    async def clear(self):
        """清除会话记忆"""
        async with async_session() as db:
            await db.execute(
                delete(SessionMemory).where(
                    SessionMemory.session_id == self.session_id
                )
            )
            await db.commit()

    async def get_latest_intent(self) -> Optional[dict]:
        """获取最近的意图识别结果"""
        async with async_session() as db:
            result = await db.execute(
                select(SessionMemory)
                .where(
                    SessionMemory.session_id == self.session_id,
                    SessionMemory.memory_type == "intent_result"
                )
                .order_by(SessionMemory.created_at.desc())
                .limit(1)
            )
            memory = result.scalar_one_or_none()

            if memory:
                return {"intent": memory.content, "timestamp": memory.created_at.isoformat()}

            return None
