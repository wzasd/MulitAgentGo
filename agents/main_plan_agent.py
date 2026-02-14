"""
主规划智能体
基于 AgentScope 实现，是整个系统的核心协调器
"""
import json
from typing import AsyncGenerator, Optional
from agentscope import msghub
from agentscope.agents import ReActAgent
from agentscope.models import DashScopeModel
from agentscope.states import AgentStates

from app.config import settings
from context.memory import MemoryManager
from intent.classifier import IntentClassifier
from chain.hooks import register_hooks


class MainPlanAgent:
    """
    主规划智能体
    负责协调各个子智能体，处理用户请求
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_manager = MemoryManager(session_id)
        self.classifier = IntentClassifier()

        # 初始化模型
        self.model = DashScopeModel(
            model=settings.dashscope_model,
            api_key=settings.dashscope_api_key,
        )

        # 注册 ReAct Hooks
        self.agent = ReActAgent(
            model=self.model,
            tools=self._get_tools(),
            sys_prompt=self._get_system_prompt(),
        )
        register_hooks(self.agent)

    def _get_tools(self):
        """获取可用工具"""
        from agents.tools import trip_tools, knowledge_tools
        return trip_tools + knowledge_tools

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是阿里商旅智能助手，专门帮助用户处理差旅相关事务。

你的主要职责：
1. 理解用户需求，识别用户意图
2. 根据用户意图调用相应的子智能体
3. 协调各子智能体完成复杂任务
4. 返回结构化的结果

可处理的业务：
- 行程规划：为用户规划出差行程，包括交通、住宿等
- 事项收集：收集用户的出差信息（时间、地点、目的等）
- 政策查询：解答差旅政策相关问题
- 订单申请：帮助用户申请差旅订单

工作流程：
1. 首先理解用户输入，判断意图
2. 如果是简单意图，直接路由到对应子智能体
3. 如果是复杂意图，调用意图识别智能体分析
4. 协调子智能体执行任务
5. 整合结果，返回给用户

注意：
- 始终保持专业、友好的服务态度
- 对于不确定的问题，主动询问用户确认
- 如果遇到错误，给出清晰的错误提示和解决建议"""

    async def chat(self, message: str) -> dict:
        """处理用户消息（非流式）"""
        # 1. 意图分类（快车道/慢车道）
        intent_result = self.classifier.classify(message)

        if intent_result and intent_result.get("type") == "simple":
            # 快车道：直接路由
            result = await self._handle_simple_intent(message, intent_result)
        else:
            # 慢车道：LLM 分析
            result = await self._handle_complex_intent(message)

        # 保存到记忆
        await self.memory_manager.add_user_message(message)
        await self.memory_manager.add_assistant_message(result["message"])

        return result

    async def stream_chat(self, message: str) -> AsyncGenerator[dict, None]:
        """处理用户消息（流式）"""
        # 1. 意图分类
        intent_result = self.classifier.classify(message)

        # 发送意图识别结果
        yield {
            "type": "intent",
            "intent": intent_result.get("intent") if intent_result else "unknown",
            "channel": "fast" if intent_result and intent_result.get("type") == "simple" else "slow"
        }

        if intent_result and intent_result.get("type") == "simple":
            # 快车道
            async for chunk in self._handle_simple_intent_stream(message, intent_result):
                yield chunk
        else:
            # 慢车道
            async for chunk in self._handle_complex_intent_stream(message):
                yield chunk

    async def _handle_simple_intent(self, message: str, intent_result: dict) -> dict:
        """处理简单意图"""
        intent = intent_result.get("intent")

        # 根据意图路由到对应智能体
        if intent == "trip_planner":
            from agents.trip_planner import TripPlannerAgent
            agent = TripPlannerAgent(self.session_id)
            result = await agent.plan(message)
        elif intent == "rag_agent":
            from agents.rag_agent import RAGAgent
            agent = RAGAgent(self.session_id)
            result = await agent.query(message)
        else:
            result = {"message": f"收到您的请求：{message}"}

        return result

    async def _handle_simple_intent_stream(self, message: str, intent_result: dict) -> AsyncGenerator[dict, None]:
        """处理简单意图（流式）"""
        intent = intent_result.get("intent")

        if intent == "trip_planner":
            from agents.trip_planner import TripPlannerAgent
            agent = TripPlannerAgent(self.session_id)
            async for chunk in agent.stream_plan(message):
                yield chunk
        elif intent == "rag_agent":
            from agents.rag_agent import RAGAgent
            agent = RAGAgent(self.session_id)
            async for chunk in agent.stream_query(message):
                yield chunk
        else:
            yield {"type": "text", "content": f"收到您的请求：{message}"}

    async def _handle_complex_intent(self, message: str) -> dict:
        """处理复杂意图"""
        # 获取上下文
        context = await self.memory_manager.get_context()

        # 调用主智能体处理
        with msghub(self.agent):
            response = self.agent(message, context)

        return {
            "message": response.content,
            "intent": "complex",
            "tools_used": response.metadata.get("tools_used", [])
        }

    async def _handle_complex_intent_stream(self, message: str) -> AsyncGenerator[dict, None]:
        """处理复杂意图（流式）"""
        context = await self.memory_manager.get_context()

        # 流式处理
        async for chunk in self.agent.stream_run(message, context):
            yield chunk
