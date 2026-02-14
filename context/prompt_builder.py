"""
动态 Prompt 构建器
根据对话状态机动态组装 Prompt
"""
from typing import Optional
from enum import Enum


class ConversationStage(Enum):
    """对话阶段枚举"""
    GREETING = "greeting"           # 问候
    INTENT_CLARIFY = "intent_clarify"  # 意图澄清
    INFO_COLLECT = "info_collect"   # 信息收集
    TRIP_PLANNING = "trip_planning"  # 行程规划
    POLICY_QUERY = "policy_query"   # 政策查询
    ORDER_CONFIRM = "order_confirm"  # 订单确认
    COMPLETED = "completed"          # 完成
    ERROR = "error"                  # 错误


class PromptBuilder:
    """
    动态 Prompt 构建器
    基于状态机实现动态 Prompt 组装
    """

    # 阶段系统提示词模板
    STAGE_PROMPTS = {
        ConversationStage.GREETING: """你是一个友好的差旅助手。当前是问候阶段。
请简洁地回应用户并引导用户说出需求。""",

        ConversationStage.INTENT_CLARIFY: """当前阶段是意图澄清。
用户的需求可能不够明确，你需要通过询问来明确用户的真实意图。
可用的意图类型：行程规划、订单申请、政策查询、信息查询、事项收集。""",

        ConversationStage.INFO_COLLECT: """当前阶段是信息收集。
你需要收集用户出差的相关信息，包括：
- 目的地
- 出发时间
- 返回时间
- 出差目的
- 预算

请逐步收集，不要一次性询问所有问题。""",

        ConversationStage.TRIP_PLANNING: """当前阶段是行程规划。
你需要根据已收集的信息，为用户规划完整的出差行程。
包括交通方式、住宿安排、日程安排等。""",

        ConversationStage.POLICY_QUERY: """当前阶段是政策查询。
请根据企业差旅政策，回答用户关于差旅规定、费用标准等问题。""",

        ConversationStage.ORDER_CONFIRM: """当前阶段是订单确认。
请确认用户的订单信息，并引导用户完成申请。""",

        ConversationStage.COMPLETED: """任务已完成。
请给用户一个友好的结束语，并告知后续操作。""",
    }

    def __init__(self):
        self.current_stage = ConversationStage.GREETING
        self.collected_info = {}

    def set_stage(self, stage: ConversationStage):
        """设置当前阶段"""
        self.current_stage = stage

    def get_stage_prompt(self) -> str:
        """获取当前阶段的系统提示词"""
        return self.STAGE_PROMPTS.get(self.current_stage, "")

    def update_info(self, key: str, value: any):
        """更新已收集的信息"""
        self.collected_info[key] = value

    def get_collected_info(self) -> dict:
        """获取已收集的信息"""
        return self.collected_info.copy()

    def build_main_prompt(self, user_input: str, context: list = None) -> str:
        """
        构建主智能体 Prompt
        根据当前阶段动态选择不同的 Prompt 模板
        """
        stage_prompt = self.get_stage_prompt()

        context_str = ""
        if context:
            context_str = "\n".join([
                f"用户: {m.get('content', '')}"
                for m in context[-5:]
            ])

        collected = ""
        if self.collected_info:
            collected = "\n已收集的信息:\n"
            for k, v in self.collected_info.items():
                collected += f"- {k}: {v}\n"

        prompt = f"""{stage_prompt}

{collected}

对话历史：
{context_str}

用户最新输入：{user_input}

请根据当前阶段处理用户输入，并输出你的响应。"""

        return prompt

    def build_intent_prompt(self, user_input: str, rule_match: dict = None) -> str:
        """
        构建意图识别 Prompt

        Args:
            user_input: 用户输入
            rule_match: 规则匹配结果（快车道）
        """
        if rule_match:
            # 快车道：简单意图
            return f"""用户输入：{user_input}

规则匹配结果：{rule_match}

请直接路由到对应的子智能体。"""
        else:
            # 慢车道：复杂意图
            return f"""请分析以下用户输入的意图：

用户输入：{user_input}

意图类型：
- trip_planner: 行程规划
- apply: 订单申请
- rag_agent: 差旅政策/知识查询
- info_query: 信息查询
- collect: 事项收集

请进行推理并输出结构化的意图识别结果。"""

    def get_next_stage(self, intent: str) -> ConversationStage:
        """
        根据意图确定下一阶段

        Args:
            intent: 识别到的意图
        """
        stage_mapping = {
            "trip_planner": ConversationStage.INFO_COLLECT,
            "apply": ConversationStage.ORDER_CONFIRM,
            "rag_agent": ConversationStage.POLICY_QUERY,
            "info_query": ConversationStage.INFO_COLLECT,
            "collect": ConversationStage.INFO_COLLECT,
        }
        return stage_mapping.get(intent, ConversationStage.GREETING)
