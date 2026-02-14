"""
RAG 知识库智能体
"""
from typing import AsyncGenerator
from agentscope.agents import ReActAgent
from agentscope.models import DashScopeModel

from app.config import settings
from context.memory import MemoryManager
from agents.tools import knowledge_tools


class RAGAgent:
    """RAG 知识库智能体"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_manager = MemoryManager(session_id)
        self.model = DashScopeModel(
            model=settings.dashscope_model,
            api_key=settings.dashscope_api_key,
        )

        self.agent = ReActAgent(
            model=self.model,
            tools=knowledge_tools,
            sys_prompt=self._get_system_prompt()
        )

    def _get_system_prompt(self) -> str:
        return """你是阿里商旅的知识库助手。

你的职责是回答用户关于差旅政策、企业制度等相关问题。

可查询的内容：
- 差旅费用标准（差标）
- 报销政策
- 预订流程
- 企业差旅规定

工作流程：
1. 理解用户的问题
2. 搜索相关知识库内容
3. 结合知识库内容给出准确的回答
4. 如果知识库没有相关内容，请明确告知用户"""

    async def query(self, user_input: str) -> dict:
        """查询知识库"""
        context = await self.memory_manager.get_context(agent_name="rag_agent")

        response = self.agent(user_input, context)

        return {
            "message": response.content,
            "intent": "rag_agent",
            "type": "knowledge_query"
        }

    async def stream_query(self, user_input: str) -> AsyncGenerator[dict, None]:
        """流式查询知识库"""
        context = await self.memory_manager.get_context(agent_name="rag_agent")

        async for chunk in self.agent.stream_run(user_input, context):
            yield chunk
