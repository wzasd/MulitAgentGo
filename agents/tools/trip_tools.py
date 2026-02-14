"""
智能体工具定义
使用 AgentScope ServiceToolkit
"""
from typing import List
from agentscope.service import ServiceToolkit


# 创建工具包
toolkit = ServiceToolkit()


# 定义工具函数
def search_knowledge(query: str, top_k: int = 3) -> str:
    """搜索知识库"""
    from knowledge.client import KnowledgeClient

    client = KnowledgeClient()
    results = client.sync_query(query, top_k)

    if not results:
        return "未找到相关内容"

    output = "搜索结果：\n"
    for i, r in enumerate(results, 1):
        output += f"\n{i}. {r.content}\n"
        output += f"   来源: {r.source}, 相似度: {r.similarity:.2f}\n"

    return output


def query_trip_policy(policy_type: str = "差标") -> str:
    """查询差旅政策"""
    from knowledge.client import KnowledgeClient

    client = KnowledgeClient()
    results = client.sync_query(f"什么是{policy_type}", top_k=1)

    if results:
        return results[0].content
    else:
        return f"未找到关于{policy_type}的相关政策"


def plan_trip(
    destination: str,
    start_date: str = None,
    end_date: str = None,
    purpose: str = None,
    budget: float = None
) -> str:
    """规划行程"""
    output = f"""行程规划：
目的地：{destination}
时间：{start_date or '待定'} - {end_date or '待定'}
目的：{purpose or '待确认'}
预算：{budget or '待评估'}

交通建议：
- 建议乘坐高铁/飞机前往

住宿建议：
- 建议选择市区酒店，便于出行

注意事项：
- 提前预订机票/火车票
- 了解当地天气情况
"""
    return output


def book_ticket(
    ticket_type: str,
    from_city: str,
    to_city: str,
    date: str,
    budget: float = None
) -> str:
    """预订机票/火车票"""
    return f"""订单申请：
票类型：{ticket_type}
出发：{from_city}
到达：{to_city}
日期：{date}
预算：{budget}

请确认以上信息，我将为您创建订单申请。
"""


def collect_trip_info(info_type: str, info: str) -> str:
    """收集出差信息"""
    return f"已收集 {info_type}: {info}，请问还有其他信息需要补充吗？"


# 注册工具
toolkit.add(search_knowledge, description="搜索知识库内容，回答差旅政策相关问题")
toolkit.add(query_trip_policy, description="查询差旅政策，如差标、报销等")
toolkit.add(plan_trip, description="为用户规划出差行程")
toolkit.add(book_ticket, description="为用户预订机票或火车票")
toolkit.add(collect_trip_info, description="收集用户的出差信息")


# 导出工具包
trip_toolkit = toolkit
knowledge_toolkit = toolkit
all_toolkit = toolkit
