"""
意图识别器（慢车道）
使用 LLM 进行复杂意图识别
"""
from typing import Optional
from app.config import settings
from agentscope.models import DashScopeChatWrapper


class IntentRecognizer:
    """
    复杂意图识别器
    使用 LLM 分析用户的复杂意图
    """

    def __init__(self):
        self.model = DashScopeChatWrapper(
            config_name='dashscope',
            model_name=settings.dashscope_model,
            api_key=settings.dashscope_api_key,
        )

    async def recognize(self, query: str, context: list) -> dict:
        """
        识别复杂意图

        Args:
            query: 用户查询
            context: 对话上下文

        Returns:
            结构化的意图识别结果
        """
        prompt = self._build_prompt(query, context)

        response = self.model(prompt)

        # 解析 LLM 响应
        result = self._parse_response(response.content)

        return result

    def _build_prompt(self, query: str, context: list) -> str:
        """构建提示词"""
        context_str = ""
        if context:
            context_str = "\n".join([
                f"用户: {m.get('content', '')[:100]}"
                for m in context[-3:]
            ])

        return f"""你是一个意图识别专家。请分析用户的查询，理解其真实意图。

上一轮对话：
{context_str}

当前用户查询：{query}

请进行两步推理：
1. 先思考用户的意图是什么
2. 然后输出 JSON 格式的识别结果

意图类型包括：
- trip_planner: 行程规划
- apply: 订单申请
- rag_agent: 差旅政策/知识查询
- info_query: 信息查询
- collect: 事项收集

输出格式（JSON）：
{{
    "intent": "意图类型",
    "confidence": 0.0-1.0,
    "reasoning": "推理过程",
    "entities": {{"实体信息"}}
}}

请直接输出 JSON，不要其他内容。"""

    def _parse_response(self, response: str) -> dict:
        """解析 LLM 响应"""
        try:
            import json
            # 尝试提取 JSON
            start = response.find("{")
            end = response.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                return result
            else:
                # 无法解析，返回默认结果
                return {
                    "intent": "unknown",
                    "confidence": 0.0,
                    "reasoning": response[:100],
                    "entities": {}
                }
        except Exception as e:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "reasoning": f"解析失败: {str(e)}",
                "entities": {}
            }
