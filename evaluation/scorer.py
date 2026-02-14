"""
评测评分器
基于 LLM 实现自动化评分
"""
from typing import Optional
from app.config import settings
from agentscope.models import DashScopeChatWrapper


class EvaluationScorer:
    """
    评测评分器
    基于通义千问大模型的自动评分能力
    主要从准确性和相关性两个维度进行评估
    """

    def __init__(self):
        self.model = DashScopeChatWrapper(
            config_name='dashscope',
            model_name=settings.dashscope_model,
            api_key=settings.dashscope_api_key,
        )

    async def score(
        self,
        test_case_id: str,
        input_text: str,
        expected_output: str,
        actual_output: str
    ) -> dict:
        """
        评分

        Args:
            test_case_id: 测试用例ID
            input_text: 输入文本
            expected_output: 期望输出
            actual_output: 实际输出

        Returns:
            评分结果
        """
        prompt = self._build_prompt(input_text, expected_output, actual_output)

        response = self.model(prompt)

        result = self._parse_response(response.content)

        return {
            "test_case_id": test_case_id,
            "input_text": input_text,
            "expected_output": expected_output,
            "actual_output": actual_output,
            **result
        }

    def _build_prompt(
        self,
        input_text: str,
        expected_output: str,
        actual_output: str
    ) -> str:
        """构建评分提示词"""
        return f"""你是一个 AI 评测专家。请对以下测试用例进行评分。

测试输入：
{input_text}

期望输出：
{expected_output}

实际输出：
{actual_output}

请从以下两个维度进行评分（0-100分）：

1. 准确性（Accuracy）：实际输出与期望输出的一致程度
   - 100分：完全一致
   - 75分：大部分一致
   - 50分：部分一致
   - 25分：少量一致
   - 0分：完全不同

2. 相关性（Relevance）：实际输出与输入的相关程度
   - 100分：完全相关
   - 75分：大部分相关
   - 50分：部分相关
   - 25分：少量相关
   - 0分：不相关

请输出 JSON 格式的评分结果：
{{
    "accuracy_score": 0-100,
    "relevance_score": 0-100,
    "feedback": "具体的改进建议"
}}

请直接输出 JSON，不要其他内容。"""

    def _parse_response(self, response: str) -> dict:
        """解析评分响应"""
        import json

        try:
            start = response.find("{")
            end = response.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                return result
            else:
                return {
                    "accuracy_score": 0,
                    "relevance_score": 0,
                    "feedback": "解析失败"
                }
        except Exception as e:
            return {
                "accuracy_score": 0,
                "relevance_score": 0,
                "feedback": f"解析错误: {str(e)}"
            }
