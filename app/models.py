"""
数据模型定义
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ========== 对话相关模型 ==========


class Message(BaseModel):
    """消息模型"""
    role: str = Field(description="角色: user/assistant/system")
    content: str = Field(description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)


class ConversationCreate(BaseModel):
    """创建会话请求"""
    user_id: str = Field(description="用户ID")
    title: Optional[str] = Field(default="新会话", description="会话标题")


class ConversationResponse(BaseModel):
    """会话响应"""
    session_id: str = Field(description="会话ID")
    title: str = Field(description="会话标题")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: str = Field(description="会话ID")
    message: str = Field(description="用户消息")
    stream: bool = Field(default=True, description="是否流式输出")


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    message: str
    thought_chain: list = Field(default_factory=list, description="思考链")
    tools_used: list = Field(default_factory=list, description="使用的工具")
    metadata: dict = Field(default_factory=dict)


# ========== 意图识别相关模型 ==========


class IntentClassification(BaseModel):
    """意图分类结果"""
    intent: str = Field(description="意图类型")
    confidence: float = Field(description="置信度", ge=0, le=1)
    entities: dict = Field(default_factory=dict, description="提取的实体")
    reasoning: str = Field(description="推理过程")


class IntentRequest(BaseModel):
    """意图识别请求"""
    query: str = Field(description="用户查询")
    context: list = Field(default_factory=list, description="对话上下文")


# ========== 行程规划相关模型 ==========


class TripInfo(BaseModel):
    """行程信息"""
    destination: str = Field(description="目的地")
    departure: Optional[str] = Field(default=None, description="出发地")
    start_date: Optional[str] = Field(default=None, description="开始日期")
    end_date: Optional[str] = Field(default=None, description="结束日期")
    purpose: Optional[str] = Field(default=None, description="出差目的")
    budget: Optional[float] = Field(default=None, description="预算")


class TripPlan(BaseModel):
    """行程计划"""
    trip_info: TripInfo
    transportation: list = Field(default_factory=list, description="交通方案")
    accommodation: list = Field(default_factory=list, description="住宿方案")
    schedule: list = Field(default_factory=list, description="日程安排")


# ========== 知识库相关模型 ==========


class KnowledgeQuery(BaseModel):
    """知识库查询请求"""
    query: str = Field(description="查询内容")
    top_k: int = Field(default=3, description="返回结果数量")
    threshold: float = Field(default=0.7, description="相似度阈值")


class KnowledgeResult(BaseModel):
    """知识库查询结果"""
    content: str = Field(description="内容")
    source: str = Field(description="来源")
    similarity: float = Field(description="相似度")


# ========== 评测相关模型 ==========


class EvaluationRequest(BaseModel):
    """评测请求"""
    test_case_id: str = Field(description="测试用例ID")
    input_text: str = Field(description="输入文本")
    expected_output: str = Field(description="期望输出")
    actual_output: str = Field(description="实际输出")


class EvaluationResult(BaseModel):
    """评测结果"""
    test_case_id: str
    accuracy_score: float = Field(description="准确率得分")
    relevance_score: float = Field(description="相关性得分")
    feedback: str = Field(description="评测反馈")
    details: dict = Field(default_factory=dict)


# ========== 工具调用相关模型 ==========


class ToolCall(BaseModel):
    """工具调用"""
    tool_name: str
    arguments: dict
    result: Optional[Any] = None
    success: bool = True


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str = Field(description="PENDING/DOING/DONE/FAILED")
    result: Optional[Any] = None
    error: Optional[str] = None
