"""
主规划智能体
简化版：不使用工具，仅使用 LLM 进行意图识别和回答
"""
import json
from typing import AsyncGenerator, Optional
from agentscope.models import DashScopeChatWrapper
from agentscope.agents import ReActAgent

from app.config import settings
from context.memory import MemoryManager
from intent.classifier import IntentClassifier


class MainPlanAgent:
    """
    主规划智能体
    负责协调各个子智能体，处理用户请求
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_manager = MemoryManager(session_id)
        self.classifier = IntentClassifier()

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是阿里商旅智能助手，专门帮助用户处理差旅相关事务。

你的主要职责：
1. 理解用户需求，识别用户意图
2. 根据用户意图回答问题或调用相应功能
3. 返回结构化的结果

可处理的业务：
- 行程规划：为用户规划出差行程，包括交通、住宿等
- 事项收集：收集用户的出差信息（时间、地点、目的等）
- 政策查询：解答差旅政策相关问题
- 订单申请：帮助用户申请差旅订单

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
            # 慢车道：简单回答（暂时不使用工具）
            result = await self._handle_simple_intent(message, {"intent": "chat", "type": "simple"})

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
            async for chunk in self._handle_simple_intent_stream(message, {"intent": "chat", "type": "simple"}):
                yield chunk

    async def _handle_simple_intent(self, message: str, intent_result: dict) -> dict:
        """处理简单意图"""
        intent = intent_result.get("intent")

        # 根据意图返回不同的响应
        if intent == "trip_planner" or "规划" in message:
            return {
                "message": "好的，我来帮您规划出差行程。请告诉我以下信息：\n1. 目的地是哪里？\n2. 出发时间是什么时候？\n3. 计划什么时候返回？\n4. 出差目的是什么？",
                "intent": intent_result.get("intent"),
                "type": "trip_plan"
            }
        elif intent == "rag_agent" or "政策" in message or "差标" in message:
            return {
                "message": "关于差旅政策，我为您查询到以下信息：\n\n差标是指本次差旅形成中，出行人乘坐飞机以及入住酒店等差旅类目的费用标准。\n\n预算指的是本次差旅出行的整体预算费用，包括交通、住宿、餐饮等各项支出。\n\n如果您想了解更多具体政策，请告诉我您想了解哪方面的内容。",
                "intent": intent_result.get("intent"),
                "type": "policy_query"
            }
        elif intent == "apply" or "申请" in message:
            return {
                "message": "好的，我来帮您申请订单。请先确认您的行程信息，我已经记录了您之前的出差需求。",
                "intent": intent_result.get("intent"),
                "type": "apply"
            }
        else:
            # 默认对话
            return {
                "message": f"收到您的消息：{message}\n\n我是阿里商旅智能助手，可以帮您：\n- 规划出差行程\n- 查询差旅政策\n- 申请订单\n\n请问有什么可以帮到您的？",
                "intent": "chat",
                "type": "chat"
            }

    async def _handle_simple_intent_stream(self, message: str, intent_result: dict) -> AsyncGenerator[dict, None]:
        """处理简单意图（流式）"""
        intent = intent_result.get("intent")

        if intent == "trip_planner" or "规划" in message:
            response = "好的，我来帮您规划出差行程。请告诉我以下信息：\n1. 目的地是哪里？\n2. 出发时间是什么时候？\n3. 计划什么时候返回？\n4. 出差目的是什么？"
        elif intent == "rag_agent" or "政策" in message or "差标" in message:
            response = "关于差旅政策，我为您查询到以下信息：\n\n差标是指本次差旅形成中，出行人乘坐飞机以及入住酒店等差旅类目的费用标准。\n\n预算指的是本次差旅出行的整体预算费用，包括交通、住宿、餐饮等各项支出。"
        elif intent == "apply" or "申请" in message:
            response = "好的，我来帮您申请订单。请先确认您的行程信息。"
        else:
            response = f"收到您的消息：{message}\n\n我是阿里商旅智能助手，可以帮您规划出差行程、查询差旅政策、申请订单。"

        # 流式输出
        for char in response:
            yield {"type": "text", "content": char}

        yield {"type": "done"}
