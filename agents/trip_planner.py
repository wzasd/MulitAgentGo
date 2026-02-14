"""
行程规划智能体
"""
from typing import AsyncGenerator
from agentscope.agents import ReActAgent
from agentscope.models import DashScopeModel

from app.config import settings
from context.memory import MemoryManager
from agents.tools import trip_tools


class TripPlannerAgent:
    """行程规划智能体"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_manager = MemoryManager(session_id)
        self.model = DashScopeModel(
            model=settings.dashscope_model,
            api_key=settings.dashscope_api_key,
        )

        self.agent = ReActAgent(
            model=self.model,
            tools=trip_tools,
            sys_prompt=self._get_system_prompt()
        )

    def _get_system_prompt(self) -> str:
        return """你是阿里商旅的行程规划专家。

你的职责是帮助用户规划完整的出差行程。

工作流程：
1. 首先收集用户的出差信息（目的地、时间、目的等）
2. 根据收集的信息为用户规划行程
3. 提供交通和住宿建议
4. 引导用户完成订单申请

重要提示：
- 遵循循序渐进的原则，不要一次性询问所有问题
- 根据用户的回答逐步补充行程信息
- 在信息收集完成后，主动给出行程规划建议"""

    async def plan(self, user_input: str) -> dict:
        """规划行程"""
        context = await self.memory_manager.get_context(agent_name="trip_planner")

        response = self.agent(user_input, context)

        return {
            "message": response.content,
            "intent": "trip_planner",
            "type": "trip_plan"
        }

    async def stream_plan(self, user_input: str) -> AsyncGenerator[dict, None]:
        """流式规划行程"""
        context = await self.memory_manager.get_context(agent_name="trip_planner")

        async for chunk in self.agent.stream_run(user_input, context):
            yield chunk
