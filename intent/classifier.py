"""
意图分类器
实现快车道（规则引擎）和慢车道（LLM分析）的分层处理
"""
from typing import Optional
from intent.recognizer import IntentRecognizer


class IntentClassifier:
    """
    意图分类器
    采用分层处理策略：快车道（规则匹配） + 慢车道（LLM分析）
    """

    # 简单意图模式匹配
    FAST_LANE_PATTERNS = {
        # 行程规划相关
        "为我规划行程": "trip_planner",
        "开始规划": "trip_planner",
        "帮我规划": "trip_planner",
        "规划行程": "trip_planner",

        # 申请相关
        "为我提申请": "apply",
        "申请订单": "apply",
        "提申请": "apply",

        # 知识库查询
        "查差旅政策": "rag_agent",
        "查政策": "rag_agent",
        "差标": "rag_agent",
        "什么是差标": "rag_agent",
        "差旅规定": "rag_agent",

        # 信息查询
        "查询": "info_query",
        "帮我查": "info_query",

        # 事项收集
        "收集事项": "collect",
        "确认信息": "collect",
    }

    def __init__(self):
        self.recognizer = IntentRecognizer()

    def classify(self, query: str) -> Optional[dict]:
        """
        意图分类
        返回结果或 None（需要走慢车道）
        """
        query = query.strip()

        # 快速精确匹配
        for pattern, intent in self.FAST_LANE_PATTERNS.items():
            if pattern == query:
                return {
                    "intent": intent,
                    "type": "simple",
                    "confidence": 1.0,
                    "pattern": pattern
                }

        # 模糊匹配
        for pattern, intent in self.FAST_LANE_PATTERNS.items():
            if pattern in query:
                return {
                    "intent": intent,
                    "type": "simple",
                    "confidence": 0.8,
                    "pattern": pattern
                }

        # 无法匹配，返回 None（走慢车道）
        return None

    async def recognize_complex_intent(self, query: str, context: list = None) -> dict:
        """
        识别复杂意图（慢车道）
        使用 LLM 进行意图分析
        """
        return await self.recognizer.recognize(query, context or [])

    def get_intent_description(self, intent: str) -> str:
        """获取意图描述"""
        descriptions = {
            "trip_planner": "行程规划",
            "apply": "订单申请",
            "rag_agent": "知识库查询",
            "info_query": "信息查询",
            "collect": "事项收集",
            "unknown": "未知意图"
        }
        return descriptions.get(intent, "未知意图")
